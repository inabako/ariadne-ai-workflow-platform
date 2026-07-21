from __future__ import annotations

import os
from pathlib import Path

from .config import ServerConfig


def load_config_from_env(base_dir: Path | None = None) -> ServerConfig:
    base = Path.cwd() if base_dir is None else base_dir
    config = ServerConfig(
        input_root=Path(os.environ.get("LOCAL_MODEL_MCP_INPUT_ROOT", "workspace/input")),
        output_root=Path(os.environ.get("LOCAL_MODEL_MCP_OUTPUT_ROOT", "workspace/output")),
        model_id=os.environ.get("LOCAL_MODEL_MCP_MODEL_ID", "mock-local-model"),
        protocol_version=os.environ.get("LOCAL_MODEL_MCP_PROTOCOL_VERSION", "2025-06-18"),
        max_file_bytes=int(os.environ.get("LOCAL_MODEL_MCP_MAX_FILE_BYTES", "1048576")),
    )
    return config.resolved(base)

