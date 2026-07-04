from __future__ import annotations

import json
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_tasks() -> list[dict[str, object]]:
    path = repo_root() / ".vscode" / "tasks.json"
    return json.loads(path.read_text(encoding="utf-8-sig"))["tasks"]


def test_aiwfctl_path_shell_task_is_provisioned() -> None:
    tasks = {str(task.get("label")): task for task in load_tasks()}

    task = tasks["workflow:aiwfctl-path-shell"]

    assert task["type"] == "process"
    assert task["command"] == "${workspaceFolder}\\runtime\\tools\\register-aiwfctl-path.cmd"
    assert task["args"] == ["--shell"]

