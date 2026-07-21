from __future__ import annotations

from typing import Protocol


class WorkspacePort(Protocol):
    def list_input_files(self, relative_path: str = ".") -> list[str]:
        ...

    def read_input_text(self, relative_path: str, *, max_file_bytes: int) -> str:
        ...

    def list_output_artifacts(self) -> list[str]:
        ...

    def write_output_text(self, relative_path: str, content: str, *, overwrite: bool, max_file_bytes: int) -> str:
        ...
