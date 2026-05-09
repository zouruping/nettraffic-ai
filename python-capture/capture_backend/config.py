from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CaptureConfig:
    interface: str | None = None
    output_dir: Path = Path("data")
    output_file_prefix: str = "packets"
    bpf_filter: str | None = None
    max_seconds: float | None = 60.0
    store_raw_payload: bool = False
    flush_interval_sec: float = 2.0
    rotate_every_packets: int = 10000
    database_url: str | None = None
    high_traffic_threshold_bytes: int = 10 * 1024 * 1024
