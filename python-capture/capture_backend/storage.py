from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import PacketRecord


class JsonlPacketStore:
    def __init__(self, output_dir: Path, file_prefix: str) -> None:
        self.output_dir = output_dir
        self.file_prefix = file_prefix
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._file_index = 0
        self._packet_written = 0
        self._fh = self._open_new_file()

    def _open_new_file(self):
        path = self.output_dir / f"{self.file_prefix}_{self._file_index:04d}.jsonl"
        self._file_index += 1
        return path.open("a", encoding="utf-8")

    def write_batch(self, batch: Iterable[PacketRecord]) -> int:
        count = 0
        for record in batch:
            self._fh.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
            count += 1
        self._packet_written += count
        if count:
            self._fh.flush()
        return count

    def rotate(self) -> None:
        self._fh.close()
        self._fh = self._open_new_file()

    def close(self) -> None:
        self._fh.close()

