from __future__ import annotations

import signal
import threading
import time
from collections import deque

from scapy.all import IP, IPv6, TCP, UDP, Ether, AsyncSniffer

from .config import CaptureConfig
from .models import PacketRecord
from .mysql_store import MySQLPacketStore
from .protocols import classify_application_protocol
from .storage import JsonlPacketStore


class PacketCaptureService:
    def __init__(self, cfg: CaptureConfig):
        self.cfg = cfg
        self._queue: deque[PacketRecord] = deque()
        self._queue_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._sniffer: AsyncSniffer | None = None
        self._store = JsonlPacketStore(cfg.output_dir, cfg.output_file_prefix)
        self._mysql_store = (
            MySQLPacketStore(
                cfg.database_url,
                high_traffic_threshold_bytes=cfg.high_traffic_threshold_bytes,
            )
            if cfg.database_url
            else None
        )
        self._metrics = {
            "packets_total": 0,
            "bytes_total": 0,
            "last_print": time.time(),
            "last_packets": 0,
            "last_bytes": 0,
            "written_total": 0,
            "db_written_total": 0,
        }

    def _detect_direction(self, src_ip: str | None, dst_ip: str | None) -> str:
        if not src_ip or not dst_ip:
            return "unknown"
        if src_ip.startswith(("10.", "192.168.", "172.")):
            return "outbound_or_lan"
        if dst_ip.startswith(("10.", "192.168.", "172.")):
            return "inbound_or_lan"
        return "unknown"

    def _packet_to_record(self, packet) -> PacketRecord:
        src_ip = None
        dst_ip = None
        protocol_l3 = "OTHER"
        if IP in packet:
            protocol_l3 = "IPv4"
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
        elif IPv6 in packet:
            protocol_l3 = "IPv6"
            src_ip = packet[IPv6].src
            dst_ip = packet[IPv6].dst

        protocol_l4 = "OTHER"
        src_port = None
        dst_port = None
        if TCP in packet:
            protocol_l4 = "TCP"
            src_port = int(packet[TCP].sport)
            dst_port = int(packet[TCP].dport)
        elif UDP in packet:
            protocol_l4 = "UDP"
            src_port = int(packet[UDP].sport)
            dst_port = int(packet[UDP].dport)

        src_mac = None
        dst_mac = None
        if Ether in packet:
            src_mac = packet[Ether].src
            dst_mac = packet[Ether].dst

        app_protocol = classify_application_protocol(protocol_l4, src_port, dst_port)
        payload_hex = bytes(packet).hex() if self.cfg.store_raw_payload else None
        return PacketRecord(
            timestamp=PacketRecord.now_iso(),
            protocol_l3=protocol_l3,
            protocol_l4=protocol_l4,
            app_protocol=app_protocol,
            src_mac=src_mac,
            dst_mac=dst_mac,
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            length=len(packet),
            direction_hint=self._detect_direction(src_ip, dst_ip),
            interface=self.cfg.interface or "unknown",
            payload_hex=payload_hex,
        )

    def _on_packet(self, packet) -> None:
        record = self._packet_to_record(packet)
        with self._queue_lock:
            self._queue.append(record)
        self._metrics["packets_total"] += 1
        self._metrics["bytes_total"] += record.length

    def _flush_once(self) -> None:
        batch: list[PacketRecord] = []
        with self._queue_lock:
            while self._queue:
                batch.append(self._queue.popleft())
        if not batch:
            return
        written = self._store.write_batch(batch)
        self._metrics["written_total"] += written
        if self._mysql_store:
            db_written = self._mysql_store.write_batch(batch)
            self._metrics["db_written_total"] += db_written

        if self.cfg.rotate_every_packets > 0:
            if self._metrics["written_total"] % self.cfg.rotate_every_packets < written:
                self._store.rotate()

    def _metrics_loop(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(1)
            now = time.time()
            elapsed = max(now - self._metrics["last_print"], 1e-6)
            pkt_now = self._metrics["packets_total"]
            bytes_now = self._metrics["bytes_total"]
            pps = (pkt_now - self._metrics["last_packets"]) / elapsed
            bps = (bytes_now - self._metrics["last_bytes"]) / elapsed
            print(
                f"[capture] total={pkt_now} written={self._metrics['written_total']} "
                f"db_written={self._metrics['db_written_total']} "
                f"pps={pps:.1f} bps={bps:.1f}"
            )
            self._metrics["last_print"] = now
            self._metrics["last_packets"] = pkt_now
            self._metrics["last_bytes"] = bytes_now

    def _flush_loop(self) -> None:
        while not self._stop_event.is_set():
            self._flush_once()
            time.sleep(self.cfg.flush_interval_sec)
        self._flush_once()

    def start(self) -> None:
        flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        metric_thread = threading.Thread(target=self._metrics_loop, daemon=True)
        flush_thread.start()
        metric_thread.start()

        self._sniffer = AsyncSniffer(
            iface=self.cfg.interface,
            filter=self.cfg.bpf_filter,
            prn=self._on_packet,
            store=False,
        )
        self._sniffer.start()
        print(f"[capture] started on interface={self.cfg.interface} filter={self.cfg.bpf_filter}")
        started_at = time.time()

        def handle_stop(_sig, _frame):
            self.stop()

        signal.signal(signal.SIGINT, handle_stop)
        signal.signal(signal.SIGTERM, handle_stop)

        while not self._stop_event.is_set():
            if self.cfg.max_seconds is not None:
                elapsed = time.time() - started_at
                if elapsed >= self.cfg.max_seconds:
                    print(
                        f"[capture] auto-stop: reached max_seconds={self.cfg.max_seconds}"
                    )
                    self.stop()
                    break
            time.sleep(0.2)

        flush_thread.join(timeout=2)
        self._store.close()
        print("[capture] stopped.")

    def stop(self) -> None:
        if self._stop_event.is_set():
            return
        self._stop_event.set()
        if self._sniffer is not None:
            self._sniffer.stop()
