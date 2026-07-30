from __future__ import annotations

import json
import subprocess
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
    assert task["command"] == "${workspaceFolder}\\runtime\\windows-script\\register-aiwfctl-path.cmd"
    assert task["args"] == ["--shell"]


def test_aiwfctl_cmd_exposes_path_usage() -> None:
    command = repo_root() / "runtime" / "windows-script" / "aiwfctl.cmd"

    result = subprocess.run(
        [str(command), "path"],
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 1
    assert "aiwfctl path check" in result.stdout
    assert "aiwfctl path register" in result.stdout
    assert "aiwfctl path shell" in result.stdout
