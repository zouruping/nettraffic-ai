from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass
class PacketRecord:
    timestamp: str
    protocol_l3: str
    protocol_l4: str
    app_protocol: str
    src_mac: str | None
    dst_mac: str | None
    src_ip: str | None
    dst_ip: str | None
    src_port: int | None
    dst_port: int | None
    length: int
    direction_hint: str
    interface: str
    payload_hex: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def now_iso() -> str:
        return datetime.now(tz=timezone.utc).isoformat()
