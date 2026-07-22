from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from runtime.ctl import ctl
from runtime.workflow import flutter_multiplatform


def write_flutter_project(target: Path) -> None:
    (target / "lib").mkdir(parents=True)
    (target / "test").mkdir()
    (target / "integration_test").mkdir()
    (target / "web").mkdir()
    (target / "pubspec.yaml").write_text(
        "\n".join(
            [
                "name: sample_app",
                "dependencies:",
                "  flutter:",
                "    sdk: flutter",
            ]
        ),
        encoding="utf-8",
    )


def write_template(repo_root: Path) -> None:
    template = repo_root / "templates" / "boilerplates" / "apps" / "flutter-app-template" / "multi-platform"
    (template / "lib").mkdir(parents=True)
    (template / "test").mkdir()
    (template / "integration_test").mkdir()
    (template / "assets").mkdir()
    (template / "pubspec.yaml").write_text("name: template\n", encoding="utf-8")
    (template / "analysis_options.yaml").write_text("linter:\n", encoding="utf-8")
    (template / "README.md").write_text("# Template\n", encoding="utf-8")


def test_analyze_without_targets_requires_human_check(tmp_path: Path) -> None:
    result = flutter_multiplatform.build_context(
        tmp_path,
        command="analyze",
        work_id="issue-1",
    )

    assert result["status"] == "human-check-required"
    assert result["target_declaration"]["targets"] == []
    assert any("全platform対応と推測せず" in item for item in result["human_checks"])
    assert "flutter-development" in result["manifest_contexts"]


def test_yaml_target_declaration_is_loaded(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-2"
    declaration = work_dir / "requirements" / "flutter-targets.yaml"
    declaration.parent.mkdir(parents=True)
    declaration.write_text(
        "\n".join(
            [
                "framework: flutter",
                "",
                "targets:",
                "  android:",
                "    enabled: true",
                "  ios:",
                "    enabled: false",
                "  web:",
                "    enabled: true",
                "  windows:",
                "    enabled: true",
                "",
                "requirements:",
                "  responsive_ui: true",
            ]
        ),
        encoding="utf-8",
    )

    result = flutter_multiplatform.build_context(tmp_path, command="analyze", work_id="issue-2")

    assert result["target_declaration"]["source"] == "yaml"
    assert result["target_declaration"]["targets"] == ["android", "web", "windows"]
    assert result["target_declaration"]["requirements"]["responsive_ui"] is True


def test_cli_targets_override_yaml_and_unknown_targets_are_reported(tmp_path: Path) -> None:
    work_dir = tmp_path / "work" / "issue-3"
    declaration = work_dir / "requirements" / "flutter-targets.yaml"
    declaration.parent.mkdir(parents=True)
    declaration.write_text(
        "framework: flutter\n\ntargets:\n  web:\n    enabled: true\n",
        encoding="utf-8",
    )

    result = flutter_multiplatform.build_context(
        tmp_path,
        command="analyze",
        work_id="issue-3",
        targets="android,web,unknown",
    )

    assert result["target_declaration"]["source"] == "cli"
    assert result["target_declaration"]["targets"] == ["android", "web"]
    assert result["target_declaration"]["unknown_targets"] == ["unknown"]
    assert any("未登録のFlutter target" in item for item in result["human_checks"])


def test_environment_decision_marks_ios_as_remote_build_when_not_macos(monkeypatch) -> None:
    monkeypatch.setattr(flutter_multiplatform, "host_os_name", lambda: "windows")

    result = flutter_multiplatform.target_environment("ios")

    assert result["status"] == "remote_build_required"
    assert result["required_environment"] == "macOS"


def test_init_copies_boilerplate_and_generates_target_declaration(tmp_path: Path) -> None:
    write_template(tmp_path)

    result = flutter_multiplatform.build_context(
        tmp_path,
        command="init",
        work_id="issue-4",
        targets="android,web,windows",
    )

    work_dir = tmp_path / "work" / "issue-4"
    assert result["boilerplate"]["copy_status"] == "copied"
    assert (work_dir / "requirements" / "flutter-targets.yaml").exists()
    assert (work_dir / "implementation" / "flutter-project" / "pubspec.yaml").exists()
    assert (work_dir / "context" / "flutter-development-context.json").exists()
    assert (work_dir / "reports" / "flutter-multiplatform-report.md").exists()


def test_verify_writes_verification_evidence(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(flutter_multiplatform.shutil, "which", lambda name: f"C:/tools/{name}.exe")

    result = flutter_multiplatform.build_context(
        tmp_path,
        command="verify",
        work_id="issue-5",
        targets="web",
    )

    evidence = tmp_path / "work" / "issue-5" / "evidence" / "flutter" / "common" / "verification-plan.md"
    assert result["status"] == "available"
    assert evidence.exists()
    assert "flutter analyze" in evidence.read_text(encoding="utf-8")


def test_build_dispatch_creates_target_specific_commands(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(flutter_multiplatform, "host_os_name", lambda: "windows")
    monkeypatch.setattr(flutter_multiplatform.shutil, "which", lambda name: "C:/flutter/bin/flutter.exe")

    result = flutter_multiplatform.build_context(
        tmp_path,
        command="build",
        work_id="issue-6",
        targets="android,web,windows,ios",
        mode="release",
    )

    commands = {item["target"]: item["command"] for item in result["build_results"]}
    statuses = {item["target"]: item["status"] for item in result["build_results"]}
    assert commands["android"] == "flutter build apk --release"
    assert commands["web"] == "flutter build web --release"
    assert commands["windows"] == "flutter build windows --release"
    assert statuses["ios"] == "remote_build_required"
    assert result["status"] == "human-check-required"


def test_ctl_parser_accepts_flutter_subcommands() -> None:
    args = ctl.build_parser().parse_args(
        [
            "flutter",
            "build",
            "--work-id",
            "issue-7",
            "--targets",
            "android,web",
            "--mode",
            "profile",
        ]
    )

    assert args.command == "flutter"
    assert args.flutter_command == "build"
    assert args.targets == "android,web"
    assert args.mode == "profile"


def test_aiwfctl_flutter_namespace_runs_runtime(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, str] = {}

    def fake_run(args: argparse.Namespace) -> dict[str, object]:
        captured["command"] = args.command
        captured["repo_root"] = args.repo_root
        return {
            "artifact_type": "flutter-development-context",
            "status": "available",
            "stage": args.command,
            "work_id": args.work_id,
            "target_declaration": {"targets": ["web"]},
            "environment_decisions": [],
            "build_results": [],
            "human_checks": [],
            "artifacts": {"context": "work/issue-8/context/flutter-development-context.json", "report": "work/issue-8/reports/flutter-multiplatform-report.md"},
        }

    monkeypatch.setattr(ctl.flutter_multiplatform, "run", fake_run)
    args = ctl.build_parser().parse_args(
        ["--repo-root", str(tmp_path), "flutter", "analyze", "--work-id", "issue-8", "--targets", "web"]
    )

    code, output = ctl.run(args)

    assert code == 0
    assert captured["command"] == "analyze"
    assert captured["repo_root"] == str(tmp_path)
    assert "Flutter Multi-platform" in output


def test_verify_execute_runs_commands_and_captures_evidence(monkeypatch, tmp_path: Path) -> None:
    write_template(tmp_path)

    monkeypatch.setattr(flutter_multiplatform, "tool_available", lambda name: True)

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr(flutter_multiplatform.subprocess, "run", fake_run)
    flutter_multiplatform.build_context(tmp_path, command="init", work_id="issue-9", targets="web")

    result = flutter_multiplatform.build_context(
        tmp_path,
        command="verify",
        work_id="issue-9",
        targets="web",
        execute=True,
    )

    execution = result["verification"]["execution"]
    evidence_dir = tmp_path / "work" / "issue-9" / "evidence" / "flutter" / "common"
    assert result["status"] == "available"
    assert execution["status"] == "passed"
    assert execution["result_count"] == 5
    assert (evidence_dir / "flutter-analyze-summary.md").exists()
    assert "ok" in (evidence_dir / "flutter-analyze-stdout.txt").read_text(encoding="utf-8")


def test_build_execute_captures_failed_command_and_status(monkeypatch, tmp_path: Path) -> None:
    write_template(tmp_path)
    monkeypatch.setattr(flutter_multiplatform, "host_os_name", lambda: "windows")
    monkeypatch.setattr(flutter_multiplatform, "tool_available", lambda name: True)

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=1, stdout="", stderr="build failed\n")

    monkeypatch.setattr(flutter_multiplatform.subprocess, "run", fake_run)
    flutter_multiplatform.build_context(tmp_path, command="init", work_id="issue-10", targets="web")

    result = flutter_multiplatform.build_context(
        tmp_path,
        command="build",
        work_id="issue-10",
        targets="web",
        execute=True,
    )

    build = result["build_results"][0]
    assert result["status"] == "failed"
    assert build["status"] == "failed"
    assert build["execution"]["returncode"] == 1
    assert (tmp_path / "work" / "issue-10" / "evidence" / "flutter" / "web" / "build-web-stderr.txt").read_text(encoding="utf-8") == "build failed\n"


def test_release_build_execute_requires_human_check(monkeypatch, tmp_path: Path) -> None:
    write_template(tmp_path)
    monkeypatch.setattr(flutter_multiplatform, "host_os_name", lambda: "windows")
    monkeypatch.setattr(flutter_multiplatform, "tool_available", lambda name: True)
    flutter_multiplatform.build_context(tmp_path, command="init", work_id="issue-11", targets="web")

    result = flutter_multiplatform.build_context(
        tmp_path,
        command="build",
        work_id="issue-11",
        targets="web",
        mode="release",
        execute=True,
    )

    assert result["status"] == "human-check-required"
    assert result["build_results"][0]["execution"]["status"] == "skipped"
    assert "release build" in result["human_checks"][0]


def test_finalize_reports_passed_when_verify_and_build_evidence_pass(monkeypatch, tmp_path: Path) -> None:
    write_template(tmp_path)
    monkeypatch.setattr(flutter_multiplatform, "host_os_name", lambda: "windows")
    monkeypatch.setattr(flutter_multiplatform, "tool_available", lambda name: True)

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr(flutter_multiplatform.subprocess, "run", fake_run)
    flutter_multiplatform.build_context(tmp_path, command="init", work_id="issue-12", targets="web")
    flutter_multiplatform.build_context(tmp_path, command="verify", work_id="issue-12", targets="web", execute=True)
    flutter_multiplatform.build_context(tmp_path, command="build", work_id="issue-12", targets="web", execute=True)

    result = flutter_multiplatform.finalize_context(tmp_path, work_id="issue-12")

    assert result["status"] == "passed"
    assert result["stage"] == "finalize"
    assert result["finalization"]["status"] == "passed"
    assert (tmp_path / "work" / "issue-12" / "evidence" / "flutter" / "finalization-summary.md").exists()


def test_finalize_requires_execute_evidence_when_missing(tmp_path: Path) -> None:
    result = flutter_multiplatform.build_context(tmp_path, command="analyze", work_id="issue-13", targets="web")
    assert result["status"] == "available"

    final = flutter_multiplatform.finalize_context(tmp_path, work_id="issue-13")

    assert final["status"] == "human-check-required"
    statuses = {item["id"]: item["status"] for item in final["finalization"]["completion_checks"]}
    assert statuses["flutter-verification"] == "missing"
    assert statuses["flutter-build"] == "missing"


def test_webdriver_failure_is_environment_required(monkeypatch, tmp_path: Path) -> None:
    write_template(tmp_path)
    monkeypatch.setattr(flutter_multiplatform, "tool_available", lambda name: True)

    def fake_run(*args, **kwargs):
        command = args[0]
        if "flutter drive" in command:
            return subprocess.CompletedProcess(args=command, returncode=1, stdout="", stderr="Unable to start a WebDriver session for web testing.\n")
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr(flutter_multiplatform.subprocess, "run", fake_run)
    flutter_multiplatform.build_context(tmp_path, command="init", work_id="issue-15", targets="web")

    result = flutter_multiplatform.build_context(tmp_path, command="verify", work_id="issue-15", targets="web", execute=True)

    assert result["status"] == "build-environment-required"
    assert result["verification"]["execution"]["status"] == "build-environment-required"


def test_ctl_parser_accepts_flutter_finalize_and_execute() -> None:
    build_args = ctl.build_parser().parse_args(
        ["flutter", "verify", "--work-id", "issue-14", "--targets", "web", "--execute", "--timeout-seconds", "30"]
    )
    finalize_args = ctl.build_parser().parse_args(["flutter", "finalize", "--work-id", "issue-14"])

    assert build_args.execute is True
    assert build_args.timeout_seconds == 30
    assert finalize_args.flutter_command == "finalize"
