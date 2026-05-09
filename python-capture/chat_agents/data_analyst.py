from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import text


class DataAnalystAgent:
    def __init__(self, active_window_minutes: int = 5):
        self.active_window_minutes = active_window_minutes

    def build_context(self, session) -> dict:
        since = datetime.now(timezone.utc) - timedelta(minutes=self.active_window_minutes)
        overview = {
            "active_host_count": session.execute(
                text("SELECT COUNT(*) FROM active_hosts WHERE last_seen >= :since"),
                {"since": since},
            ).scalar_one(),
            "active_ip_count": session.execute(
                text("SELECT COUNT(*) FROM active_ips WHERE last_seen >= :since"),
                {"since": since},
            ).scalar_one(),
            "realtime_alert_count": session.execute(
                text("SELECT COUNT(*) FROM alert_records WHERE status='ACTIVE'")
            ).scalar_one(),
            "active_window_minutes": self.active_window_minutes,
        }

        top_ip_rows = session.execute(
            text(
                """
                SELECT ip_address, byte_count, packet_count, last_seen
                FROM active_ips
                ORDER BY byte_count DESC
                LIMIT 5
                """
            )
        ).mappings()

        recent_alert_rows = session.execute(
            text(
                """
                SELECT alert_type, severity, target_value, message, packet_count, byte_count, last_seen
                FROM alert_records
                ORDER BY last_seen DESC
                LIMIT 5
                """
            )
        ).mappings()

        top_l4_rows = session.execute(
            text(
                """
                SELECT protocol_name, packet_count, byte_count
                FROM protocol_metrics
                WHERE protocol_layer = 'L4'
                ORDER BY byte_count DESC
                LIMIT 5
                """
            )
        ).mappings()

        top_l7_rows = session.execute(
            text(
                """
                SELECT protocol_name, packet_count, byte_count
                FROM protocol_metrics
                WHERE protocol_layer = 'L7'
                ORDER BY byte_count DESC
                LIMIT 5
                """
            )
        ).mappings()

        return {
            "overview": overview,
            "top_traffic_ips": [dict(r) for r in top_ip_rows],
            "recent_alerts": [dict(r) for r in recent_alert_rows],
            "top_l4_protocols": [dict(r) for r in top_l4_rows],
            "top_l7_protocols": [dict(r) for r in top_l7_rows],
        }

    def build_evidence(self, intent: str, context: dict) -> list[str]:
        evidence: list[str] = []
        overview = context.get("overview", {})
        evidence.append(
            "overview: active_hosts={active_host_count}, active_ips={active_ip_count}, alerts={realtime_alert_count}, window={active_window_minutes}min".format(
                **overview
            )
        )

        if intent in {"top_traffic_ip", "general_analysis"}:
            top_ips = context.get("top_traffic_ips", [])
            if top_ips:
                top = top_ips[0]
                evidence.append(
                    f"top_traffic_ip: ip={top.get('ip_address')}, bytes={top.get('byte_count')}, packets={top.get('packet_count')}, last_seen={top.get('last_seen')}"
                )
            else:
                evidence.append("top_traffic_ip: no data")

        if intent in {"alert_status", "general_analysis"}:
            alerts = context.get("recent_alerts", [])
            if alerts:
                latest = alerts[0]
                evidence.append(
                    f"latest_alert: type={latest.get('alert_type')}, severity={latest.get('severity')}, target={latest.get('target_value')}, last_seen={latest.get('last_seen')}"
                )
            else:
                evidence.append("latest_alert: no data")

        if intent in {"protocol_distribution", "general_analysis"}:
            l4 = context.get("top_l4_protocols", [])
            l7 = context.get("top_l7_protocols", [])
            evidence.append(f"top_l4: {l4[0] if l4 else 'no data'}")
            evidence.append(f"top_l7: {l7[0] if l7 else 'no data'}")

        return evidence

