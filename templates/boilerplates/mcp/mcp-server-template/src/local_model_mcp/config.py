from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ServerConfig:
    input_root: Path = Path("workspace/input")
    output_root: Path = Path("workspace/output")
    model_id: str = "mock-local-model"
    protocol_version: str = "2025-06-18"
    max_file_bytes: int = 1_048_576

    def resolved(self, base_dir: Path | None = None) -> "ServerConfig":
        base = Path.cwd() if base_dir is None else base_dir
        return ServerConfig(
            input_root=(base / self.input_root).resolve() if not self.input_root.is_absolute() else self.input_root.resolve(),
            output_root=(base / self.output_root).resolve() if not self.output_root.is_absolute() else self.output_root.resolve(),
            model_id=self.model_id,
            protocol_version=self.protocol_version,
            max_file_bytes=self.max_file_bytes,
        )

