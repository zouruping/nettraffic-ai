from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy import text

from .db import init_db
from .models import PacketRecord


class MySQLPacketStore:
    def __init__(self, database_url: str, high_traffic_threshold_bytes: int = 10 * 1024 * 1024):
        self.database_url = database_url
        self.high_traffic_threshold_bytes = high_traffic_threshold_bytes
        _, self._session_factory = init_db(database_url)

    @staticmethod
    def _parse_timestamp(value: str) -> datetime:
        return datetime.fromisoformat(value)

    def write_batch(self, batch: list[PacketRecord]) -> int:
        if not batch:
            return 0

        host_metrics = defaultdict(lambda: {"packets": 0, "bytes": 0, "first": None, "last": None})
        ip_metrics = defaultdict(lambda: {"packets": 0, "bytes": 0, "first": None, "last": None})
        l4_metrics = defaultdict(lambda: {"packets": 0, "bytes": 0})
        l7_metrics = defaultdict(lambda: {"packets": 0, "bytes": 0})

        packet_rows = []
        for record in batch:
            ts = self._parse_timestamp(record.timestamp)
            packet_rows.append(
                {
                    "captured_at": ts,
                    "interface": record.interface,
                    "protocol_l3": record.protocol_l3,
                    "protocol_l4": record.protocol_l4,
                    "app_protocol": record.app_protocol,
                    "src_mac": record.src_mac,
                    "dst_mac": record.dst_mac,
                    "src_ip": record.src_ip,
                    "dst_ip": record.dst_ip,
                    "src_port": record.src_port,
                    "dst_port": record.dst_port,
                    "packet_len": record.length,
                    "direction_hint": record.direction_hint,
                    "payload_hex": record.payload_hex,
                }
            )

            if record.src_mac:
                self._accumulate_entity(host_metrics[record.src_mac], ts, record.length)
            if record.dst_mac:
                self._accumulate_entity(host_metrics[record.dst_mac], ts, record.length)
            if record.src_ip:
                self._accumulate_entity(ip_metrics[record.src_ip], ts, record.length)
            if record.dst_ip:
                self._accumulate_entity(ip_metrics[record.dst_ip], ts, record.length)

            l4_metrics[record.protocol_l4]["packets"] += 1
            l4_metrics[record.protocol_l4]["bytes"] += record.length
            l7_metrics[record.app_protocol]["packets"] += 1
            l7_metrics[record.app_protocol]["bytes"] += record.length

        with self._session_factory() as session:
            self._insert_packets(session, packet_rows)
            self._upsert_hosts(session, host_metrics)
            self._upsert_ips(session, ip_metrics)
            self._upsert_protocol_metrics(session, "L4", l4_metrics)
            self._upsert_protocol_metrics(session, "L7", l7_metrics)
            self._insert_alerts(session, ip_metrics)
            session.commit()
        return len(batch)

    @staticmethod
    def _accumulate_entity(entity: dict, ts: datetime, packet_len: int) -> None:
        entity["packets"] += 1
        entity["bytes"] += packet_len
        entity["first"] = ts if entity["first"] is None else min(entity["first"], ts)
        entity["last"] = ts if entity["last"] is None else max(entity["last"], ts)

    @staticmethod
    def _insert_packets(session, packet_rows: list[dict]) -> None:
        session.execute(
            text(
                """
                INSERT INTO captured_packets
                (captured_at, interface, protocol_l3, protocol_l4, app_protocol, src_mac, dst_mac, src_ip, dst_ip,
                src_port, dst_port, packet_len, direction_hint, payload_hex)
                VALUES
                (:captured_at, :interface, :protocol_l3, :protocol_l4, :app_protocol, :src_mac, :dst_mac, :src_ip, :dst_ip,
                :src_port, :dst_port, :packet_len, :direction_hint, :payload_hex)
                """
            ),
            packet_rows,
        )

    @staticmethod
    def _upsert_hosts(session, host_metrics: dict) -> None:
        rows = [
            {
                "mac_address": mac,
                "first_seen": metric["first"],
                "last_seen": metric["last"],
                "packet_count": metric["packets"],
                "byte_count": metric["bytes"],
            }
            for mac, metric in host_metrics.items()
        ]
        if not rows:
            return
        session.execute(
            text(
                """
                INSERT INTO active_hosts (mac_address, first_seen, last_seen, packet_count, byte_count)
                VALUES (:mac_address, :first_seen, :last_seen, :packet_count, :byte_count)
                ON DUPLICATE KEY UPDATE
                    first_seen = LEAST(first_seen, VALUES(first_seen)),
                    last_seen = GREATEST(last_seen, VALUES(last_seen)),
                    packet_count = packet_count + VALUES(packet_count),
                    byte_count = byte_count + VALUES(byte_count)
                """
            ),
            rows,
        )

    @staticmethod
    def _upsert_ips(session, ip_metrics: dict) -> None:
        rows = [
            {
                "ip_address": ip,
                "first_seen": metric["first"],
                "last_seen": metric["last"],
                "packet_count": metric["packets"],
                "byte_count": metric["bytes"],
            }
            for ip, metric in ip_metrics.items()
        ]
        if not rows:
            return
        session.execute(
            text(
                """
                INSERT INTO active_ips (ip_address, first_seen, last_seen, packet_count, byte_count)
                VALUES (:ip_address, :first_seen, :last_seen, :packet_count, :byte_count)
                ON DUPLICATE KEY UPDATE
                    first_seen = LEAST(first_seen, VALUES(first_seen)),
                    last_seen = GREATEST(last_seen, VALUES(last_seen)),
                    packet_count = packet_count + VALUES(packet_count),
                    byte_count = byte_count + VALUES(byte_count)
                """
            ),
            rows,
        )

    @staticmethod
    def _upsert_protocol_metrics(session, layer: str, metrics: dict) -> None:
        rows = [
            {
                "protocol_layer": layer,
                "protocol_name": protocol_name,
                "packet_count": value["packets"],
                "byte_count": value["bytes"],
            }
            for protocol_name, value in metrics.items()
        ]
        if not rows:
            return
        session.execute(
            text(
                """
                INSERT INTO protocol_metrics (protocol_layer, protocol_name, packet_count, byte_count, updated_at)
                VALUES (:protocol_layer, :protocol_name, :packet_count, :byte_count, NOW(6))
                ON DUPLICATE KEY UPDATE
                    packet_count = packet_count + VALUES(packet_count),
                    byte_count = byte_count + VALUES(byte_count),
                    updated_at = NOW(6)
                """
            ),
            rows,
        )

    def _insert_alerts(self, session, ip_metrics: dict) -> None:
        rows = []
        for ip, value in ip_metrics.items():
            if value["bytes"] < self.high_traffic_threshold_bytes:
                continue
            rows.append(
                {
                    "alert_type": "HIGH_TRAFFIC_IP",
                    "severity": "HIGH",
                    "target_value": ip,
                    "message": f"IP {ip} 流量超过阈值 {self.high_traffic_threshold_bytes} bytes",
                    "packet_count": value["packets"],
                    "byte_count": value["bytes"],
                    "first_seen": value["first"],
                    "last_seen": value["last"],
                }
            )
        if not rows:
            return

        session.execute(
            text(
                """
                INSERT INTO alert_records
                (alert_type, severity, target_value, message, packet_count, byte_count, first_seen, last_seen, status)
                VALUES
                (:alert_type, :severity, :target_value, :message, :packet_count, :byte_count, :first_seen, :last_seen, 'ACTIVE')
                """
            ),
            rows,
        )
