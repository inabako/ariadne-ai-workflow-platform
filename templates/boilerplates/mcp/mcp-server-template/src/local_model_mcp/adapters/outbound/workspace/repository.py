from __future__ import annotations

from ....audit import AuditRecorder
from ....errors import ArtifactExistsError, FileTooLargeError
from ....input_validation import reject_binary_file, require_text_content
from ....security import WorkspacePathPolicy


class WorkspaceRepository:
    def __init__(self, *, path_policy: WorkspacePathPolicy, audit: AuditRecorder) -> None:
        self.path_policy = path_policy
        self.audit = audit

    def list_input_files(self, relative_path: str = ".") -> list[str]:
        root = self.path_policy.input_path(relative_path)
        if not root.exists():
            return []
        return sorted(str(path.relative_to(self.path_policy.input_root)) for path in root.rglob("*") if path.is_file())

    def read_input_text(self, relative_path: str, *, max_file_bytes: int) -> str:
        path = self.path_policy.input_path(relative_path)
        if path.stat().st_size > max_file_bytes:
            raise FileTooLargeError("file exceeds configured max_file_bytes")
        reject_binary_file(path)
        self.audit.record("read_workspace_file", relative_path, status="ok")
        return path.read_text(encoding="utf-8")

    def list_output_artifacts(self) -> list[str]:
        return sorted(
            str(path.relative_to(self.path_policy.output_root))
            for path in self.path_policy.output_root.rglob("*")
            if path.is_file()
        )

    def write_output_text(self, relative_path: str, content: str, *, overwrite: bool, max_file_bytes: int) -> str:
        path = self.path_policy.output_path(relative_path)
        if path.exists() and not overwrite:
            raise ArtifactExistsError("set overwrite=true to replace existing artifact")
        require_text_content(content, max_file_bytes)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.audit.record("write_output_artifact", relative_path, status="ok")
        return path.relative_to(self.path_policy.output_root).as_posix()
