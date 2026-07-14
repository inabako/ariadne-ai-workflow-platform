from __future__ import annotations

from pathlib import Path

from .errors import SecurityPolicyError


SECRET_FRAGMENTS = (".env", "secret", "token", "password", "id_rsa", "credential")


class WorkspacePathPolicy:
    def __init__(self, input_root: Path, output_root: Path) -> None:
        self.input_root = input_root.resolve()
        self.output_root = output_root.resolve()

    def input_path(self, relative_path: str) -> Path:
        return self._resolve_inside(self.input_root, relative_path)

    def output_path(self, relative_path: str) -> Path:
        return self._resolve_inside(self.output_root, relative_path)

    def assert_not_secret(self, path: Path) -> None:
        lowered = path.name.lower()
        if any(fragment in lowered for fragment in SECRET_FRAGMENTS):
            raise SecurityPolicyError(f"secret-like path is denied: {path.name}")

    def _resolve_inside(self, root: Path, relative_path: str) -> Path:
        candidate = Path(relative_path)
        if candidate.is_absolute():
            raise SecurityPolicyError("absolute paths are not allowed")
        resolved = (root / candidate).resolve()
        if root != resolved and root not in resolved.parents:
            raise SecurityPolicyError("path traversal outside workspace is not allowed")
        self.assert_not_secret(resolved)
        return resolved

