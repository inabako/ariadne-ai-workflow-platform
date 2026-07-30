from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.constants.runtime_values import SCHEMA_VERSION  # noqa: E402
from runtime.common import gate_restart, find_repo_root, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.constants.cli_defaults import FLUTTER_TIMEOUT_SECONDS_DEFAULT  # noqa: E402
from runtime.constants.workflow_limits import FLUTTER_COMMAND_SLUG_MAX_CHARS  # noqa: E402
from runtime.constants.paths import WINDOWS_FLUTTER_BIN  # noqa: E402
from runtime.constants.schemas import FLUTTER_DEVELOPMENT_CONTEXT_SCHEMA  # noqa: E402
from runtime.constants.workspace import (  # noqa: E402
    DEFAULT_TARGET_REPO_HELP,
    context_file,
    implementation_dir_for_work_dir,
    implementation_path_pattern,
    manifest_path_for_work_dir,
    reports_dir_for_work_dir,
    resolve_work_dir as workspace_resolve_work_dir,
    target_repository_dir_for_work_dir,
)
from runtime.constants.workspace import target_repository_dir_for_work_dir  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402



ARTIFACT_TYPE = "flutter-development-context"
DEFAULT_SCHEMA = FLUTTER_DEVELOPMENT_CONTEXT_SCHEMA
TARGET_DECLARATION = "requirements/flutter-targets.yaml"
TARGETS = ["android", "ios", "web", "windows", "macos", "linux"]
BUILD_MODES = ["debug", "profile", "release"]
MOBILE_TARGETS = {"android", "ios"}
DESKTOP_TARGETS = {"windows", "macos", "linux"}
EXECUTABLE_STATUS = {"planned", "passed", "failed", "skipped"}


def resolve_repo_path(repo_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def resolve_work_dir(repo_root: Path, work_id: str, work_dir: str = "") -> Path:
    if not work_id:
        raise ValueError("--work-id is required when --work-dir is not specified.")
    return workspace_resolve_work_dir(repo_root, work_id, work_dir)


def default_target_repo(work_dir: Path) -> Path:
    return target_repository_dir_for_work_dir(work_dir)


def normalize_target(value: str) -> str:
    return value.strip().lower().replace("_", "-")


def parse_targets_arg(value: str | None) -> tuple[list[str], list[str]]:
    if not value:
        return [], []
    seen: list[str] = []
    unknown: list[str] = []
    for raw in value.split(","):
        target = normalize_target(raw)
        if not target:
            continue
        if target not in TARGETS:
            unknown.append(target)
            continue
        if target not in seen:
            seen.append(target)
    return seen, unknown


def yaml_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "Null", "NULL", "~"}:
        return None
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        return [item.strip().strip("'\"") for item in body.split(",") if item.strip()] if body else []
    return value.strip("'\"")


def parse_flutter_targets_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "targets": {}, "requirements": {}, "framework": ""}
    data: dict[str, Any] = {"exists": True, "targets": {}, "requirements": {}, "framework": ""}
    section = ""
    current_target = ""
    current_key = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        line = raw_line.rstrip()
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            current_target = ""
            current_key = ""
            continue
        if indent == 0 and ":" in stripped:
            key, value = stripped.split(":", 1)
            if key.strip() == "framework":
                data["framework"] = yaml_scalar(value)
            continue
        if section == "targets" and indent == 2 and stripped.endswith(":"):
            current_target = normalize_target(stripped[:-1])
            data["targets"].setdefault(current_target, {})
            current_key = ""
            continue
        if section == "targets" and current_target and indent >= 4:
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                key = key.strip()
                if value.strip():
                    data["targets"].setdefault(current_target, {})[key] = yaml_scalar(value)
                    current_key = ""
                else:
                    data["targets"].setdefault(current_target, {})[key] = []
                    current_key = key
                continue
            if stripped.startswith("- ") and current_key:
                current = data["targets"].setdefault(current_target, {}).setdefault(current_key, [])
                if isinstance(current, list):
                    current.append(yaml_scalar(stripped[2:]))
            continue
        if section == "requirements" and indent >= 2 and ":" in stripped:
            key, value = stripped.split(":", 1)
            data["requirements"][key.strip()] = yaml_scalar(value)
    return data


def render_targets_yaml(targets: list[str]) -> str:
    lines = ["framework: flutter", "", "targets:"]
    for target in TARGETS:
        lines.extend([f"  {target}:", f"    enabled: {'true' if target in targets else 'false'}"])
        if target == "windows" and target in targets:
            lines.extend(["    architecture:", "      - x64"])
    lines.extend(
        [
            "",
            "requirements:",
            "  responsive_ui: true",
            "  offline_support: false",
            "  native_integration: false",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def load_target_declaration(work_dir: Path, cli_targets: str | None) -> dict[str, Any]:
    cli_selected, cli_unknown = parse_targets_arg(cli_targets)
    declaration_path = work_dir / TARGET_DECLARATION
    parsed = parse_flutter_targets_yaml(declaration_path)
    unknown = list(cli_unknown)
    if cli_selected or cli_unknown:
        return {
            "source": "cli",
            "path": declaration_path.as_posix(),
            "exists": parsed["exists"],
            "targets": cli_selected,
            "unknown_targets": unknown,
            "requirements": parsed.get("requirements", {}),
            "framework": parsed.get("framework", ""),
        }
    yaml_targets: list[str] = []
    for target, config in parsed.get("targets", {}).items():
        if target not in TARGETS:
            unknown.append(target)
            continue
        if isinstance(config, dict) and config.get("enabled") is True:
            yaml_targets.append(target)
    return {
        "source": "yaml" if parsed["exists"] else "missing",
        "path": declaration_path.as_posix(),
        "exists": parsed["exists"],
        "targets": yaml_targets,
        "unknown_targets": unknown,
        "requirements": parsed.get("requirements", {}),
        "framework": parsed.get("framework", ""),
    }


def host_os_name() -> str:
    name = platform.system().lower()
    if name == "darwin":
        return "macos"
    if name.startswith("win"):
        return "windows"
    if name.startswith("linux"):
        return "linux"
    return name or "unknown"


def default_flutter_bin() -> Path:
    return WINDOWS_FLUTTER_BIN


def command_environment() -> dict[str, str]:
    import os

    env = dict(os.environ)
    flutter_bin = default_flutter_bin()
    if flutter_bin.exists():
        path = env.get("Path") or env.get("PATH") or ""
        parts = [part for part in path.split(";") if part]
        if not any(part.rstrip("\\").lower() == str(flutter_bin).rstrip("\\").lower() for part in parts):
            env["Path"] = f"{flutter_bin};{path}" if path else str(flutter_bin)
    return env


def tool_available(name: str) -> bool:
    if shutil.which(name):
        return True
    suffixes = [".bat", ".cmd", ".exe", ""]
    for suffix in suffixes:
        if (default_flutter_bin() / f"{name}{suffix}").exists():
            return True
    return False


def flutter_target_gate_restart(status: str, target: str) -> dict[str, Any]:
    return gate_restart.build_status_gate_restart(
        "flutter-target-environment-gate",
        status=status,
        restart_reason="flutter-target-environment",
        repair_command=f"aiwfctl env select {target} --work-id <work-id>"
        if status in {"build_environment_required", "remote_build_required", "human_check_required"}
        else "",
    )


def _target_environment_without_gate(target: str, host_os: str | None = None) -> dict[str, Any]:
    host = host_os or host_os_name()
    if target in {"android", "web"}:
        supported = host in {"windows", "macos", "linux"}
        return {
            "target": target,
            "host_os": host,
            "status": "build_available" if supported else "build_environment_required",
            "required_environment": "Windows / macOS / Linux",
            "reason": "Flutter SDKでhost OS上のbuildを計画できます。" if supported else "Flutter対応host OSを確認できません。",
        }
    if target in {"ios", "macos"}:
        supported = host == "macos"
        return {
            "target": target,
            "host_os": host,
            "status": "build_available" if supported else "remote_build_required",
            "required_environment": "macOS",
            "reason": f"{target} buildにはmacOS/Xcode系環境が必要です。",
        }
    if target == "windows":
        supported = host == "windows"
        return {
            "target": target,
            "host_os": host,
            "status": "build_available" if supported else "build_environment_required",
            "required_environment": "Windows",
            "reason": "Windows desktop buildにはWindows環境が必要です。",
        }
    if target == "linux":
        supported = host == "linux"
        return {
            "target": target,
            "host_os": host,
            "status": "build_available" if supported else "build_environment_required",
            "required_environment": "Linux",
            "reason": "Linux desktop buildにはLinux環境が必要です。",
        }
    return {
        "target": target,
        "host_os": host,
        "status": "human_check_required",
        "required_environment": "unknown",
        "reason": "未登録のFlutter targetです。",
    }


def target_environment(target: str, host_os: str | None = None) -> dict[str, Any]:
    record = _target_environment_without_gate(target, host_os)
    record["gate_restart"] = flutter_target_gate_restart(str(record.get("status", "")), target)
    return record


def detect_flutter_project(target_repo: Path) -> dict[str, Any]:
    pubspec = target_repo / "pubspec.yaml"
    text = pubspec.read_text(encoding="utf-8", errors="ignore") if pubspec.exists() else ""
    platform_dirs = [target for target in TARGETS if (target_repo / target).exists()]
    return {
        "path": str(target_repo),
        "exists": target_repo.exists(),
        "has_pubspec": pubspec.exists(),
        "is_flutter_project": pubspec.exists() and ("flutter:" in text or "sdk: flutter" in text),
        "has_lib": (target_repo / "lib").exists(),
        "has_test": (target_repo / "test").exists(),
        "has_integration_test": (target_repo / "integration_test").exists(),
        "platform_directories": platform_dirs,
    }


def select_boilerplate(targets: list[str]) -> dict[str, str]:
    target_set = set(targets)
    category_count = int(bool(target_set & MOBILE_TARGETS)) + int("web" in target_set) + int(bool(target_set & DESKTOP_TARGETS))
    if not targets:
        name = "application"
    elif category_count > 1:
        name = "multi-platform"
    elif target_set <= MOBILE_TARGETS:
        name = "mobile"
    elif target_set == {"web"}:
        name = "web"
    elif target_set <= DESKTOP_TARGETS:
        name = "desktop"
    else:
        name = "application"
    template_name = name if name == "multi-platform" else "multi-platform"
    return {
        "name": name,
        "template_name": template_name,
        "template_path": f"templates/boilerplates/apps/flutter-app-template/{template_name}",
        "destination": implementation_path_pattern("flutter-project"),
    }


def build_command(target: str, mode: str) -> str:
    mode_flag = f" --{mode}" if mode in BUILD_MODES else ""
    commands = {
        "android": f"flutter build apk{mode_flag}",
        "ios": f"flutter build ios{mode_flag}",
        "web": f"flutter build web{mode_flag}",
        "windows": f"flutter build windows{mode_flag}",
        "macos": f"flutter build macos{mode_flag}",
        "linux": f"flutter build linux{mode_flag}",
    }
    return commands[target]


def artifact_path_for(target: str, mode: str) -> str:
    mapping = {
        "android": f"build/app/outputs/flutter-apk/app-{mode}.apk",
        "ios": "build/ios/iphoneos/Runner.app",
        "web": "build/web",
        "windows": "build/windows/x64/runner/Release",
        "macos": "build/macos/Build/Products/Release",
        "linux": "build/linux/x64/release/bundle",
    }
    return mapping[target]


def build_dispatch(targets: list[str], mode: str, environment_decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flutter_available = tool_available("flutter")
    status_by_target = {item["target"]: item["status"] for item in environment_decisions}
    results: list[dict[str, Any]] = []
    for target in targets:
        env_status = status_by_target.get(target, "human_check_required")
        status = "planned"
        warnings: list[str] = []
        errors: list[str] = []
        if env_status != "build_available":
            status = env_status
            warnings.append("現在のhost OSではこのtargetのbuildを実行できません。")
        elif not flutter_available:
            status = "build_environment_required"
            warnings.append("flutter commandがPATH上にありません。")
        if mode == "release":
            warnings.append("release buildは署名・配布設定のHuman Check後に実行してください。")
        results.append(
            {
                "target": target,
                "status": status,
                "command": build_command(target, mode),
                "artifact_path": artifact_path_for(target, mode),
                "started_at": None,
                "finished_at": None,
                "warnings": warnings,
                "errors": errors,
            }
        )
    return results


def verification_plan(work_dir: Path, targets: list[str]) -> dict[str, Any]:
    evidence = work_dir / "evidence" / "flutter" / "common" / "verification-plan.md"
    integration_command = "flutter test integration_test"
    if "web" in targets:
        integration_command = "flutter drive --driver=test_driver/integration_test.dart --target=integration_test/application_flow_test.dart -d chrome"
    elif "windows" in targets and host_os_name() == "windows":
        integration_command = "flutter test integration_test -d windows"
    elif "linux" in targets and host_os_name() == "linux":
        integration_command = "flutter test integration_test -d linux"
    elif "macos" in targets and host_os_name() == "macos":
        integration_command = "flutter test integration_test -d macos"
    commands = [
        "flutter pub get",
        "dart format --output=none --set-exit-if-changed .",
        "flutter analyze",
        "flutter test",
        integration_command,
    ]
    target_evidence = [
        {"target": target, "evidence_dir": f"evidence/flutter/{target}", "status": "planned"} for target in targets
    ]
    return {
        "commands": commands,
        "flutter_available": tool_available("flutter"),
        "dart_available": tool_available("dart"),
        "evidence": evidence.as_posix(),
        "target_evidence": target_evidence,
    }


def command_slug(command: str) -> str:
    value = command.lower()
    for old, new in [(" --", "-"), (" ", "-"), ("/", "-"), ("\\", "-"), (".", "-")]:
        value = value.replace(old, new)
    return "".join(ch for ch in value if ch.isalnum() or ch in {"-"})[:FLUTTER_COMMAND_SLUG_MAX_CHARS].strip("-") or "command"


def run_captured_command(
    *,
    command: str,
    cwd: Path,
    evidence_dir: Path,
    timeout_seconds: int,
    label: str = "",
) -> dict[str, Any]:
    started_at = utc_now_iso()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    slug = command_slug(label or command)
    stdout_path = evidence_dir / f"{slug}-stdout.txt"
    stderr_path = evidence_dir / f"{slug}-stderr.txt"
    summary_path = evidence_dir / f"{slug}-summary.md"
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            env=command_environment(),
            shell=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        status = "passed" if returncode == 0 else "failed"
        error = ""
        combined = f"{stdout}\n{stderr}"
        if returncode != 0 and ("WebDriver" in combined or "chromedriver" in combined):
            status = "build-environment-required"
            error = "Web integration test requires a running WebDriver such as chromedriver."
    except subprocess.TimeoutExpired as exc:
        returncode = None
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        status = "failed"
        error = f"timeout after {timeout_seconds} seconds"
    finished_at = utc_now_iso()
    stdout_path.write_text(stdout or "", encoding="utf-8")
    stderr_path.write_text(stderr or "", encoding="utf-8")
    summary_path.write_text(
        "\n".join(
            [
                f"# {label or command}",
                "",
                f"- command: `{command}`",
                f"- cwd: `{cwd}`",
                f"- status: `{status}`",
                f"- returncode: `{returncode}`",
                f"- started_at: `{started_at}`",
                f"- finished_at: `{finished_at}`",
                f"- error: {error or 'なし'}",
                f"- stdout: `{stdout_path.name}`",
                f"- stderr: `{stderr_path.name}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "command": command,
        "cwd": str(cwd),
        "status": status,
        "returncode": returncode,
        "started_at": started_at,
        "finished_at": finished_at,
        "error": error,
        "stdout_path": stdout_path.as_posix(),
        "stderr_path": stderr_path.as_posix(),
        "summary_path": summary_path.as_posix(),
    }


def execution_project_dir(work_dir: Path, target_repo: Path) -> Path | None:
    if (target_repo / "pubspec.yaml").exists():
        return target_repo
    copied = implementation_dir_for_work_dir(work_dir) / "flutter-project"
    if (copied / "pubspec.yaml").exists():
        return copied
    return None


def execute_verification(work_dir: Path, project_dir: Path, plan: dict[str, Any], timeout_seconds: int) -> dict[str, Any]:
    evidence_dir = work_dir / "evidence" / "flutter" / "common"
    results = [
        run_captured_command(command=command, cwd=project_dir, evidence_dir=evidence_dir, timeout_seconds=timeout_seconds)
        for command in plan.get("commands", [])
    ]
    if results and all(item.get("status") == "passed" for item in results):
        status = "passed"
    elif any(item.get("status") == "build-environment-required" for item in results):
        status = "build-environment-required"
    else:
        status = "failed"
    return {
        "executed": True,
        "project_dir": project_dir.as_posix(),
        "status": status,
        "result_count": len(results),
        "results": results,
    }


def execute_builds(
    *,
    work_dir: Path,
    project_dir: Path,
    build_results: list[dict[str, Any]],
    timeout_seconds: int,
    human_check: str = "",
) -> list[dict[str, Any]]:
    executed: list[dict[str, Any]] = []
    for item in build_results:
        target = str(item.get("target", ""))
        command = str(item.get("command", ""))
        env_status = str(item.get("status", ""))
        result = dict(item)
        evidence_dir = work_dir / "evidence" / "flutter" / target
        if env_status != "planned":
            result["execution"] = {"executed": False, "status": "skipped", "reason": env_status}
            executed.append(result)
            continue
        if "--release" in command and human_check != "approved":
            result["status"] = "human-check-required"
            result["execution"] = {"executed": False, "status": "skipped", "reason": "release build requires --human-check approved"}
            executed.append(result)
            continue
        execution = run_captured_command(
            command=command,
            cwd=project_dir,
            evidence_dir=evidence_dir,
            timeout_seconds=timeout_seconds,
            label=f"build-{target}",
        )
        result["status"] = execution["status"]
        result["started_at"] = execution["started_at"]
        result["finished_at"] = execution["finished_at"]
        result["execution"] = execution
        executed.append(result)
    return executed


def human_checks_for(
    *,
    targets: list[str],
    unknown_targets: list[str],
    environment_decisions: list[dict[str, Any]],
    mode: str,
    project: dict[str, Any],
) -> list[str]:
    checks: list[str] = []
    if not targets:
        checks.append("対象Flutter platformが未指定です。全platform対応と推測せず、人間が対象platformを確定してください。")
    if unknown_targets:
        checks.append(f"未登録のFlutter targetがあります: {', '.join(unknown_targets)}")
    for item in environment_decisions:
        if item.get("status") in {"build_environment_required", "remote_build_required", "human_check_required"}:
            checks.append(f"{item.get('target')} buildには {item.get('required_environment')} の確認が必要です。")
    if mode == "release":
        checks.append("release buildはSigning、Store配布、成果物公開範囲のHuman Checkが必要です。")
    if project.get("exists") and not project.get("is_flutter_project"):
        checks.append("対象repositoryは存在しますがFlutter projectとして確認できません。既存構成を人間確認してください。")
    return list(dict.fromkeys(checks))


def knowledge_targets(context: dict[str, Any]) -> list[str]:
    return [
        "Flutter対象platformとbuild環境判断",
        "Flutter project構成とboilerplate選択理由",
        "Platform差分、test、build evidenceの保存方針",
    ]


def context_status(human_checks: list[str], verification: dict[str, Any] | None = None) -> str:
    if human_checks:
        return "human-check-required"
    if verification and verification.get("execution", {}).get("status") == "failed":
        return "failed"
    if verification and verification.get("execution", {}).get("status") == "build-environment-required":
        return "build-environment-required"
    if verification and (not verification.get("flutter_available") or not verification.get("dart_available")):
        return "build-environment-required"
    return "available"


def render_report(context: dict[str, Any]) -> str:
    lines = [
        "# Flutter Multi-platform Report",
        "",
        "## 対応概要",
        "",
        f"- status: `{context.get('status', '')}`",
        f"- stage: `{context.get('stage', '')}`",
        f"- work_id: `{context.get('work_id', '')}`",
        "",
        "## 対象プラットフォーム",
        "",
    ]
    targets = context.get("target_declaration", {}).get("targets", [])
    lines.append(f"- targets: `{', '.join(targets) or '未確定'}`")
    lines.append(f"- source: `{context.get('target_declaration', {}).get('source', '')}`")
    lines.extend(["", "## 開発環境", ""])
    for item in context.get("environment_decisions", []):
        lines.append(
            f"- {item.get('target')}: `{item.get('status')}` / required=`{item.get('required_environment')}` / {item.get('reason')}"
        )
    lines.extend(["", "## Flutterプロジェクト構成", ""])
    project = context.get("flutter_project", {})
    lines.append(f"- path: `{project.get('path', '')}`")
    lines.append(f"- is_flutter_project: `{project.get('is_flutter_project', False)}`")
    lines.append(f"- platform_directories: `{', '.join(project.get('platform_directories', [])) or '未検出'}`")
    lines.extend(["", "## Boilerplate", ""])
    boilerplate = context.get("boilerplate", {})
    lines.append(f"- selected: `{boilerplate.get('name', '')}`")
    lines.append(f"- template: `{boilerplate.get('template_path', '')}`")
    if boilerplate.get("copied_to"):
        lines.append(f"- copied_to: `{boilerplate.get('copied_to')}`")
    lines.extend(
        [
            "",
            "## 共通実装",
            "",
            "- Domain / Service / UI / Platform Interfaceを分離し、platform判定をAdapter境界へ寄せる。",
            "",
            "## プラットフォーム固有実装",
            "",
            "- platform固有権限、Manifest、Info.plist、Desktop依存、Web制約はtarget別evidenceへ保存する。",
            "",
            "## Platform Channel",
            "",
            "- Platform Channel追加はHuman Check対象。Dart側InterfaceとNative側実装を分離する。",
            "",
            "## UI・レスポンシブ対応",
            "",
            "- LayoutBuilder / MediaQuery / Adaptive Navigation候補を検討し、固定サイズ前提を避ける。",
            "",
            "## 静的解析結果",
            "",
        ]
    )
    verification = context.get("verification", {})
    if verification:
        for command in verification.get("commands", []):
            lines.append(f"- planned: `{command}`")
        execution = verification.get("execution", {})
        if execution:
            lines.append(f"- execution: `{execution.get('status', '')}`")
            for item in execution.get("results", []):
                lines.append(f"  - `{item.get('command')}`: `{item.get('status')}` / summary=`{item.get('summary_path')}`")
    else:
        lines.append("- 未実行")
    lines.extend(["", "## Unit Test結果", "", "- planned: `flutter test`"])
    lines.extend(["", "## Widget Test結果", "", "- planned: `flutter test` 内のwidget testを確認する。"])
    lines.extend(["", "## Integration Test結果", "", "- planned: `flutter test integration_test`"])
    lines.extend(["", "## プラットフォーム別ビルド結果", ""])
    for item in context.get("build_results", []):
        lines.append(f"- {item.get('target')}: `{item.get('status')}` / `{item.get('command')}` / artifact=`{item.get('artifact_path')}`")
        execution = item.get("execution", {})
        if execution:
            lines.append(f"  - execution: `{execution.get('status')}` / summary=`{execution.get('summary_path', '')}`")
    lines.extend(["", "## 成果物", ""])
    for key, value in context.get("artifacts", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## プラットフォーム間の差分", "", "- target別にbuild/evidenceを分離し、差分はPlatform Interface境界へ集約する。"])
    lines.extend(["", "## Human Check", ""])
    checks = context.get("human_checks", [])
    lines.extend(f"- {item}" for item in checks) if checks else lines.append("- なし")
    lines.extend(["", "## 未確認事項", ""])
    warnings = [warning for item in context.get("build_results", []) for warning in item.get("warnings", [])]
    lines.extend(f"- {item}" for item in warnings) if warnings else lines.append("- なし")
    finalization = context.get("finalization", {})
    if finalization:
        lines.extend(["", "## 完了判定", ""])
        lines.append(f"- status: `{finalization.get('status', '')}`")
        for item in finalization.get("completion_checks", []):
            lines.append(f"- {item.get('id')}: `{item.get('status')}` - {item.get('detail')}")
    lines.extend(["", "## 残課題", "", "- 署名、Store配布、実機試験はHuman Check後に実行する。"])
    lines.extend(["", "## Knowledge化対象", ""])
    lines.extend(f"- {item}" for item in context.get("knowledge_targets", []))
    return "\n".join(lines).rstrip() + "\n"


def write_verification_evidence(plan: dict[str, Any]) -> str:
    evidence_path = Path(plan["evidence"])
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Flutter Verification Plan",
        "",
        "## Commands",
        "",
        *(f"- `{command}`" for command in plan.get("commands", [])),
        "",
        "## Tool Availability",
        "",
        f"- flutter: `{plan.get('flutter_available', False)}`",
        f"- dart: `{plan.get('dart_available', False)}`",
    ]
    evidence_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return evidence_path.as_posix()


def copy_boilerplate(repo_root: Path, work_dir: Path, boilerplate: dict[str, str], *, force: bool = False) -> dict[str, Any]:
    source = resolve_repo_path(repo_root, boilerplate["template_path"])
    destination = implementation_dir_for_work_dir(work_dir) / "flutter-project"
    if not source.exists():
        return {"status": "template-missing", "source": relative_to_repo(repo_root, source), "destination": relative_to_repo(repo_root, destination)}
    if destination.exists() and not force:
        return {"status": "exists", "source": relative_to_repo(repo_root, source), "destination": relative_to_repo(repo_root, destination)}
    if destination.exists() and force:
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return {"status": "copied", "source": relative_to_repo(repo_root, source), "destination": relative_to_repo(repo_root, destination)}


def write_outputs(repo_root: Path, work_dir: Path, context: dict[str, Any]) -> dict[str, str]:
    report_path = reports_dir_for_work_dir(work_dir) / "flutter-multiplatform-report.md"
    context_path = context_file(work_dir, "flutter-development-context.json")
    artifacts = {
        "report": relative_to_repo(repo_root, report_path),
        "context": relative_to_repo(repo_root, context_path),
    }
    verification = context.get("verification", {})
    if isinstance(verification, dict) and verification.get("evidence_written"):
        artifacts["verification_evidence"] = relative_to_repo(repo_root, Path(str(verification["evidence_written"])))
    finalization = context.get("finalization", {})
    if isinstance(finalization, dict) and finalization.get("evidence_path"):
        artifacts["finalization_evidence"] = relative_to_repo(repo_root, Path(str(finalization["evidence_path"])))
    context["artifacts"] = artifacts
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(context), encoding="utf-8")
    write_json(context_path, context)
    manifest = register_context(
        repo_root,
        work_dir,
        work_id=str(context.get("work_id", "")),
        context_type="flutter-development",
        path=context_path,
        required=False,
        generated_by="flutter-multiplatform",
        owner="flutter-multiplatform",
        schema=DEFAULT_SCHEMA,
        status=str(context.get("status", "")),
    )
    context["manifest_path"] = relative_to_repo(repo_root, manifest_path_for_work_dir(work_dir))
    context["manifest_contexts"] = [item.get("type") for item in manifest.get("contexts", []) if isinstance(item, dict)]
    write_json(context_path, context)
    return artifacts


def build_context(
    repo_root: Path,
    *,
    command: str,
    work_id: str,
    work_dir: str = "",
    target_repo: str = "",
    targets: str = "",
    mode: str = "debug",
    force: bool = False,
    execute: bool = False,
    human_check: str = "",
    timeout_seconds: int = FLUTTER_TIMEOUT_SECONDS_DEFAULT,
) -> dict[str, Any]:
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    target_path = resolve_repo_path(repo_root, target_repo) if target_repo else default_target_repo(work_path)
    previous_context = read_json(context_file(work_path, "flutter-development-context.json"), default={})
    previous_context = previous_context if isinstance(previous_context, dict) else {}
    declaration = load_target_declaration(work_path, targets)
    selected_targets = declaration["targets"]
    env_decisions = [target_environment(target) for target in selected_targets]
    project = detect_flutter_project(target_path)
    boilerplate = select_boilerplate(selected_targets)
    verification: dict[str, Any] = {}
    build_results: list[dict[str, Any]] = []
    human_checks = human_checks_for(
        targets=selected_targets,
        unknown_targets=declaration["unknown_targets"],
        environment_decisions=env_decisions,
        mode=mode,
        project=project,
    )
    if command in {"init", "run-workflow"}:
        if selected_targets and not (work_path / TARGET_DECLARATION).exists():
            declaration_path = work_path / TARGET_DECLARATION
            declaration_path.parent.mkdir(parents=True, exist_ok=True)
            declaration_path.write_text(render_targets_yaml(selected_targets), encoding="utf-8")
            declaration["exists"] = True
            declaration["source"] = "generated-from-cli"
        copy_result = copy_boilerplate(repo_root, work_path, boilerplate, force=force) if selected_targets else {"status": "skipped"}
        boilerplate = {**boilerplate, "copy_status": copy_result.get("status", ""), "copied_to": copy_result.get("destination", "")}
    if command in {"verify", "run-workflow"}:
        verification = verification_plan(work_path, selected_targets)
        verification["evidence_written"] = write_verification_evidence(verification)
        if execute and not human_checks:
            project_dir = execution_project_dir(work_path, target_path)
            if project_dir is None:
                human_checks.append("実試験を実行するFlutter projectが見つかりません。先にinitするか--target-repoを指定してください。")
            else:
                verification["execution"] = execute_verification(work_path, project_dir, verification, timeout_seconds)
    if command in {"build", "run-workflow"}:
        build_results = build_dispatch(selected_targets, mode, env_decisions)
        blocking_checks = [item for item in human_checks if "release build" not in item]
        if execute and not blocking_checks:
            project_dir = execution_project_dir(work_path, target_path)
            if project_dir is None:
                human_checks.append("buildを実行するFlutter projectが見つかりません。先にinitするか--target-repoを指定してください。")
            else:
                build_results = execute_builds(
                    work_dir=work_path,
                    project_dir=project_dir,
                    build_results=build_results,
                    timeout_seconds=timeout_seconds,
                    human_check=human_check,
                )
    if command == "build" and not verification and isinstance(previous_context.get("verification"), dict):
        verification = previous_context.get("verification", {})
    if command == "verify" and not build_results and isinstance(previous_context.get("build_results"), list):
        build_results = previous_context.get("build_results", [])
    status = context_status(human_checks, verification if command in {"verify", "run-workflow"} else None)
    if any(item.get("status") == "failed" for item in build_results):
        status = "failed"
    elif any(item.get("status") == "human-check-required" for item in build_results):
        status = "human-check-required"
    context = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "status": status,
        "work_id": work_id,
        "workflow": "flutter-multiplatform",
        "stage": command,
        "generated_at": utc_now_iso(),
        "target_repo": str(target_path),
        "build_mode": mode,
        "target_declaration": {
            **declaration,
            "path": relative_to_repo(repo_root, Path(declaration["path"])),
        },
        "environment_decisions": env_decisions,
        "flutter_project": project,
        "boilerplate": boilerplate,
        "verification": verification,
        "build_results": build_results,
        "human_checks": human_checks,
        "knowledge_targets": [],
        "rules": {
            "do_not_assume_all_platforms_when_targets_missing": True,
            "do_not_execute_store_distribution_without_human_check": True,
            "do_not_generate_signing_credentials": True,
            "build_commands_are_planned_until_parent_workflow_executes_them": True,
            "execute_requires_explicit_execute_flag": True,
        },
    }
    context["knowledge_targets"] = knowledge_targets(context)
    write_outputs(repo_root, work_path, context)
    return context


def finalize_context(repo_root: Path, *, work_id: str, work_dir: str = "", target_repo: str = "") -> dict[str, Any]:
    work_path = resolve_work_dir(repo_root, work_id, work_dir)
    target_path = resolve_repo_path(repo_root, target_repo) if target_repo else default_target_repo(work_path)
    context_path = context_file(work_path, "flutter-development-context.json")
    previous = read_json(context_path, default={})
    previous = previous if isinstance(previous, dict) else {}
    checks: list[dict[str, str]] = []
    verification = previous.get("verification", {}) if isinstance(previous.get("verification"), dict) else {}
    verification_execution = verification.get("execution", {}) if isinstance(verification.get("execution"), dict) else {}
    if verification_execution.get("status") == "passed":
        checks.append({"id": "flutter-verification", "status": "passed", "detail": "静的解析、Unit/Widget Test、Integration Testがpassしています。"})
    elif verification_execution.get("status") == "build-environment-required":
        checks.append({"id": "flutter-verification", "status": "build-environment-required", "detail": "Integration Testに必要なtoolまたは実行環境が不足しています。"})
    elif verification_execution:
        checks.append({"id": "flutter-verification", "status": "failed", "detail": "Flutter verify実行結果に失敗があります。"})
    else:
        checks.append({"id": "flutter-verification", "status": "missing", "detail": "Flutter verify --execute の証跡がありません。"})
    build_results = previous.get("build_results", []) if isinstance(previous.get("build_results"), list) else []
    if build_results:
        failed = [item for item in build_results if item.get("status") in {"failed", "human-check-required"}]
        passed = [item for item in build_results if item.get("status") == "passed"]
        skipped = [item for item in build_results if item.get("status") in {"build_environment_required", "remote_build_required"}]
        if failed:
            checks.append({"id": "flutter-build", "status": "failed", "detail": f"失敗またはHuman Check待ちのbuildがあります: {len(failed)}件"})
        elif passed:
            checks.append({"id": "flutter-build", "status": "passed", "detail": f"実行可能targetのbuildがpassしています: {len(passed)}件"})
        elif skipped:
            checks.append({"id": "flutter-build", "status": "conditional-pass", "detail": "現在hostでbuildできないtargetはremote/build環境待ちです。"})
        else:
            checks.append({"id": "flutter-build", "status": "missing", "detail": "build --execute の証跡がありません。"})
    else:
        checks.append({"id": "flutter-build", "status": "missing", "detail": "build dispatchまたはbuild実行証跡がありません。"})
    evidence_files = sorted(
        relative_to_repo(repo_root, path)
        for path in (work_path / "evidence" / "flutter").rglob("*")
        if path.is_file()
    ) if (work_path / "evidence" / "flutter").exists() else []
    if evidence_files:
        checks.append({"id": "flutter-evidence", "status": "passed", "detail": f"Flutter evidenceが保存されています: {len(evidence_files)}件"})
    else:
        checks.append({"id": "flutter-evidence", "status": "missing", "detail": "Flutter evidenceが見つかりません。"})
    statuses = {item["status"] for item in checks}
    if "failed" in statuses:
        status = "failed"
    elif "missing" in statuses or "build-environment-required" in statuses:
        status = "human-check-required"
    elif "conditional-pass" in statuses:
        status = "conditional-pass"
    else:
        status = "passed"
    evidence_path = work_path / "evidence" / "flutter" / "finalization-summary.md"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_lines = [f"- `{item}`" for item in evidence_files] if evidence_files else ["- なし"]
    evidence_path.write_text(
        "\n".join(
            [
                "# Flutter Finalization Summary",
                "",
                f"- status: `{status}`",
                f"- work_id: `{work_id}`",
                f"- target_repo: `{target_path}`",
                "",
                "## Completion Checks",
                "",
                *(f"- {item['id']}: `{item['status']}` - {item['detail']}" for item in checks),
                "",
                "## Evidence Files",
                "",
                *evidence_lines,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    context = {
        **previous,
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "status": status,
        "work_id": work_id,
        "workflow": "flutter-multiplatform",
        "stage": "finalize",
        "generated_at": utc_now_iso(),
        "target_repo": previous.get("target_repo", str(target_path)),
        "finalization": {
            "status": status,
            "completion_checks": checks,
            "evidence_files": evidence_files,
            "evidence_path": evidence_path.as_posix(),
        },
        "human_checks": previous.get("human_checks", []),
        "knowledge_targets": previous.get("knowledge_targets", []),
        "rules": {
            **(previous.get("rules", {}) if isinstance(previous.get("rules"), dict) else {}),
            "finalize_reads_evidence_without_running_commands": True,
        },
    }
    write_outputs(repo_root, work_path, context)
    return context


def format_result(result: dict[str, Any]) -> str:
    lines = [
        "Flutter Multi-platform",
        "",
        f"Status  : {result.get('status', '')}",
        f"Stage   : {result.get('stage', '')}",
        f"Work ID : {result.get('work_id', '')}",
        f"Context : {result.get('artifacts', {}).get('context', '')}",
        f"Report  : {result.get('artifacts', {}).get('report', '')}",
        "",
        "Targets",
    ]
    targets = result.get("target_declaration", {}).get("targets", [])
    lines.append(f"  - {', '.join(targets) if targets else '未確定'}")
    lines.extend(["", "Environment"])
    for item in result.get("environment_decisions", []):
        lines.append(f"  - {item.get('target')}: {item.get('status')} ({item.get('required_environment')})")
    verification = result.get("verification", {})
    if isinstance(verification, dict) and verification.get("execution"):
        lines.extend(["", "Verification Execution"])
        lines.append(f"  - {verification.get('execution', {}).get('status')}")
    if result.get("build_results"):
        lines.extend(["", "Build Dispatch"])
        for item in result.get("build_results", []):
            lines.append(f"  - {item.get('target')}: {item.get('status')} / {item.get('command')}")
    checks = result.get("human_checks", [])
    if checks:
        lines.extend(["", "Human Check"])
        lines.extend(f"  - {item}" for item in checks)
    finalization = result.get("finalization", {})
    if isinstance(finalization, dict) and finalization:
        lines.extend(["", "Finalization"])
        lines.append(f"  - {finalization.get('status')}")
        for item in finalization.get("completion_checks", []):
            lines.append(f"    - {item.get('id')}: {item.get('status')}")
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze Flutter multi-platform targets and build dispatch.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["analyze", "init", "verify", "build", "run-workflow"]:
        cmd = sub.add_parser(name)
        cmd.add_argument("--work-id", required=True)
        cmd.add_argument("--work-dir", default="")
        cmd.add_argument("--target-repo", default="", help=DEFAULT_TARGET_REPO_HELP)
        cmd.add_argument("--targets", default="", help="Comma-separated Flutter targets: android,ios,web,windows,macos,linux")
        cmd.add_argument("--mode", choices=BUILD_MODES, default="debug")
        cmd.add_argument("--force", action="store_true", help="Refresh copied boilerplate during init.")
        cmd.add_argument("--execute", action="store_true", help="Run verification/build commands and capture evidence.")
        cmd.add_argument("--human-check", choices=["approved"], default="", help="Required for release execution.")
        cmd.add_argument("--timeout-seconds", type=int, default=FLUTTER_TIMEOUT_SECONDS_DEFAULT)
        cmd.add_argument("--json", action="store_true")
    finalize = sub.add_parser("finalize")
    finalize.add_argument("--work-id", required=True)
    finalize.add_argument("--work-dir", default="")
    finalize.add_argument("--target-repo", default="")
    finalize.add_argument("--json", action="store_true")
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if getattr(args, "repo_root", "") else find_repo_root()
    if args.command == "finalize":
        return finalize_context(
            repo_root,
            work_id=args.work_id,
            work_dir=getattr(args, "work_dir", ""),
            target_repo=getattr(args, "target_repo", ""),
        )
    return build_context(
        repo_root,
        command=args.command,
        work_id=args.work_id,
        work_dir=getattr(args, "work_dir", ""),
        target_repo=getattr(args, "target_repo", ""),
        targets=getattr(args, "targets", ""),
        mode=getattr(args, "mode", "debug"),
        force=bool(getattr(args, "force", False)),
        execute=bool(getattr(args, "execute", False)),
        human_check=getattr(args, "human_check", ""),
        timeout_seconds=int(getattr(args, "timeout_seconds", FLUTTER_TIMEOUT_SECONDS_DEFAULT)),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = run(args)
    if getattr(args, "json", False):
        import json

        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_result(result), end="")
    return 0 if result.get("status") not in {"human-check-required", "failed"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
