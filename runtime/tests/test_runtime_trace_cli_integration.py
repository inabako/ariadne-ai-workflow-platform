from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


TEST_LOG_ROOT = Path("logs") / "test" / "runtime-trace-cli-integration"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def publish_runtime_event_log(source: Path, scenario: str) -> Path:
    destination = repo_root() / TEST_LOG_ROOT / scenario / "runtime-events.log"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return destination


def prepare_runtime_repo(tmp_path: Path) -> Path:
    (tmp_path / ".git").mkdir()
    registry_dir = tmp_path / "runtime" / "registries"
    registry_dir.mkdir(parents=True)
    (registry_dir / "workflow_help.json").write_text('{"commands": [], "extensions": []}', encoding="utf-8")
    return tmp_path


def run_aiwfctl(target_repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    root = repo_root()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [
            sys.executable,
            str(root / "runtime" / "ctl" / "ctl.py"),
            "--repo-root",
            str(target_repo),
            *args,
        ],
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_runtime_trace_sequence_continues_across_cli_processes(tmp_path: Path) -> None:
    target_repo = prepare_runtime_repo(tmp_path)
    trace_id = "cli-sequence-trace"

    commands = [
        ("trace", "begin", "--workflow", "/runtime-health-check", "--trace-id", trace_id),
        ("help", "list"),
        ("help", "markdown", "--output", "work/help/runtime-help.md"),
        ("trace", "status", "--json"),
        ("trace", "end"),
    ]
    results = [run_aiwfctl(target_repo, *command) for command in commands]

    assert [result.returncode for result in results] == [0, 0, 0, 0, 0]
    status = json.loads(results[3].stdout)
    assert status["trace_id"] == trace_id
    assert status["last_sequence"] == 7
    assert (target_repo / "work" / "help" / "runtime-help.md").exists()

    log_path = target_repo / "logs" / "runtime" / "runtime-events.log"
    published_log_path = publish_runtime_event_log(log_path, "sequence")
    prefixes = [line.split(" | ", 3) for line in log_path.read_text(encoding="utf-8").splitlines()]
    trace_ids = [prefix[1] for prefix in prefixes]
    sequences = [prefix[2] for prefix in prefixes]
    payloads = [json.loads(prefix[3]) for prefix in prefixes]

    assert trace_ids == [trace_id] * 10
    assert sequences == [f"{index:05d}" for index in range(1, 11)]
    assert published_log_path.exists()
    assert [payload["command"] for payload in payloads] == [
        "trace begin",
        "trace begin",
        "help list",
        "help list",
        "help markdown",
        "help markdown",
        "trace status",
        "trace status",
        "trace end",
        "trace end",
    ]
    assert not (target_repo / "logs" / "runtime" / "active-trace.json").exists()


def test_runtime_trace_without_active_trace_keeps_command_scoped_sequences(tmp_path: Path) -> None:
    target_repo = prepare_runtime_repo(tmp_path)

    results = [
        run_aiwfctl(target_repo, "help", "list"),
        run_aiwfctl(target_repo, "help", "list"),
    ]

    assert [result.returncode for result in results] == [0, 0]
    assert not (target_repo / "logs" / "runtime" / "active-trace.json").exists()

    log_path = target_repo / "logs" / "runtime" / "runtime-events.log"
    published_log_path = publish_runtime_event_log(log_path, "without-active")
    prefixes = [line.split(" | ", 3) for line in log_path.read_text(encoding="utf-8").splitlines()]
    trace_ids = [prefix[1] for prefix in prefixes]
    sequences = [prefix[2] for prefix in prefixes]

    assert len(set(trace_ids)) == 2
    assert trace_ids[:2] == [trace_ids[0], trace_ids[0]]
    assert trace_ids[2:] == [trace_ids[2], trace_ids[2]]
    assert trace_ids[0] != trace_ids[2]
    assert sequences == ["00001", "00002", "00001", "00002"]
    assert published_log_path.exists()
