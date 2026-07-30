from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ArtifactRegistry:
    artifacts: list[dict[str, str]] = field(default_factory=list)

    def register(self, job_id: str, relative_path: str, artifact_type: str = "output") -> None:
        self.artifacts.append({"job_id": job_id, "relative_path": relative_path, "type": artifact_type})

    def paths_for(self, job_id: str) -> list[str]:
        return [item["relative_path"] for item in self.artifacts if item["job_id"] == job_id]

