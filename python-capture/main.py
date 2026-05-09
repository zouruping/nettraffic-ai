from __future__ import annotations

import argparse
import os
from pathlib import Path

from capture_backend.capture import PacketCaptureService
from capture_backend.config import CaptureConfig
from capture_backend.netio import check_permission_hint, list_interfaces, pick_default_interface


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Network traffic capture backend (Python, Scapy)."
    )
    parser.add_argument("--list-ifaces", action="store_true", help="List interfaces and exit.")
    parser.add_argument("--iface", type=str, default=None, help="Interface name to capture.")
    parser.add_argument("--bpf", type=str, default=None, help="Optional BPF filter.")
    parser.add_argument(
        "--max-seconds",
        type=float,
        default=60.0,
        help="Auto-stop capture after N seconds (default: 60). Set 0 or negative to disable.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data"),
        help="Output directory for jsonl capture files.",
    )
    parser.add_argument(
        "--prefix", type=str, default="packets", help="Output file prefix."
    )
    parser.add_argument(
        "--store-raw-payload",
        action="store_true",
        help="Store packet bytes as hex string (bigger files).",
    )
    parser.add_argument(
        "--flush-interval",
        type=float,
        default=2.0,
        help="Flush interval seconds.",
    )
    parser.add_argument(
        "--rotate-every",
        type=int,
        default=10000,
        help="Rotate output file every N packets.",
    )
    parser.add_argument(
        "--database-url",
        type=str,
        default=os.getenv("DATABASE_URL"),
        help="MySQL database URL, e.g. mysql+pymysql://user:pass@127.0.0.1:3306/nettraffic_ai",
    )
    parser.add_argument(
        "--high-traffic-threshold-bytes",
        type=int,
        default=int(os.getenv("HIGH_TRAFFIC_THRESHOLD_BYTES", 10 * 1024 * 1024)),
        help="Alert threshold in bytes for high-traffic IP in one flush batch.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list_ifaces:
        for iface in list_interfaces():
            print(
                f"name={iface.name} up={iface.is_up} addresses={','.join(iface.addresses)}"
            )
        return

    iface = args.iface or pick_default_interface()
    if not iface:
        raise RuntimeError("No available network interface found.")

    hint = check_permission_hint()
    if hint:
        print(f"[hint] {hint}")

    cfg = CaptureConfig(
        interface=iface,
        output_dir=args.out_dir,
        output_file_prefix=args.prefix,
        bpf_filter=args.bpf,
        max_seconds=args.max_seconds if args.max_seconds > 0 else None,
        store_raw_payload=args.store_raw_payload,
        flush_interval_sec=args.flush_interval,
        rotate_every_packets=args.rotate_every,
        database_url=args.database_url,
        high_traffic_threshold_bytes=args.high_traffic_threshold_bytes,
    )
    service = PacketCaptureService(cfg)
    service.start()


if __name__ == "__main__":
    main()
