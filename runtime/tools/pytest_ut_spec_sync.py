from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, utc_now_iso, write_json
from runtime.workflow import context_first


CASE_HEADING_PREFIX = "#### RT-UT-CASE-"
CONFIRM_PREFIX = "- 確認内容:"
INPUT_PREFIX = "- 入力値:"
EXPECTED_PREFIX = "- 期待結果:"
TEXT_FENCE = "```text"
REPORT_SCHEMA = ".github/schemas/pytest-ut-spec-sync-report.schema.json"

FIXTURE_MEANINGS = {
    "tmp_path": "temporary filesystem",
    "monkeypatch": "environment / function monkeypatch",
    "capsys": "captured stdout/stderr",
    "caplog": "captured log records",
    "request": "pytest request context",
}


@dataclass(frozen=True)
class SpecCase:
    case_id: str
    node_id: str


@dataclass(frozen=True)
class FunctionInfo:
    source_path: Path
    line_no: int
    arguments: tuple[str, ...]
    parametrize_names: tuple[str, ...]
    inline_inputs: tuple[str, ...]


def runtime_dir_from_spec(spec_path: Path) -> Path:
    resolved = spec_path.resolve()
    for parent in resolved.parents:
        if parent.name == "docs":
            return parent.parent / "runtime"
    return resolved.parents[2] / "runtime"


def normalize_collected_node(node_id: str) -> str:
    node_id = node_id.strip()
    path_part, separator, rest = node_id.partition("::")
    normalized_path = path_part.replace("\\", "/")
    normalized = f"{normalized_path}{separator}{rest}" if separator else normalized_path
    if normalized.startswith("runtime/"):
        return normalized
    if normalized.startswith("tests/"):
        return f"runtime/{normalized}"
    return normalized


def collect_pytest_nodes(runtime_dir: Path) -> list[str]:
    command = [sys.executable, "-m", "pytest", "--collect-only", "-q", "tests"]
    completed = subprocess.run(
        command,
        cwd=runtime_dir,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    nodes: list[str] = []
    for line in completed.stdout.splitlines():
        stripped = line.strip()
        if "::" not in stripped:
            continue
        if stripped.startswith("tests/") or stripped.startswith("runtime/tests/"):
            nodes.append(normalize_collected_node(stripped))
    return nodes


def parse_spec_cases(spec_text: str) -> list[SpecCase]:
    cases: list[SpecCase] = []
    current_case: str | None = None
    in_node_fence = False
    for line in spec_text.splitlines():
        if line.startswith(CASE_HEADING_PREFIX):
            current_case = line.strip("# ").strip()
            in_node_fence = False
            continue
        if current_case and line == TEXT_FENCE:
            in_node_fence = True
            continue
        if current_case and in_node_fence and line == "```":
            in_node_fence = False
            continue
        if current_case and in_node_fence and line.strip().startswith("runtime/tests/"):
            cases.append(SpecCase(current_case, line.strip()))
            current_case = None
            in_node_fence = False
    return cases


def split_node(node_id: str) -> tuple[Path, str, str]:
    path_part, _, rest = node_id.partition("::")
    function_part = rest.split("::")[-1]
    function_name = function_part.split("[", 1)[0]
    parameter_id = ""
    if "[" in function_part and function_part.endswith("]"):
        parameter_id = function_part.rsplit("[", 1)[1][:-1]
    return Path(path_part), function_name, parameter_id


def _parametrize_names_from_decorator(decorator: ast.AST) -> tuple[str, ...]:
    call = decorator if isinstance(decorator, ast.Call) else None
    if call is None:
        return ()
    func = call.func
    if not (
        isinstance(func, ast.Attribute)
        and func.attr == "parametrize"
        and isinstance(func.value, ast.Attribute)
        and func.value.attr == "mark"
    ):
        return ()
    if not call.args:
        return ()
    first_arg = call.args[0]
    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
        return tuple(part.strip() for part in first_arg.value.split(",") if part.strip())
    if isinstance(first_arg, (ast.List, ast.Tuple)):
        names: list[str] = []
        for element in first_arg.elts:
            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                names.append(element.value)
        return tuple(names)
    return ()


def _simple_call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _simple_call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _assignment_target_names(target: ast.AST) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        names: list[str] = []
        for element in target.elts:
            names.extend(_assignment_target_names(element))
        return names
    return []


def _is_inline_input_value(value: ast.AST) -> bool:
    if isinstance(value, (ast.Constant, ast.Dict, ast.List, ast.Tuple, ast.Set)):
        return True
    if isinstance(value, ast.Call):
        call_name = _simple_call_name(value.func)
        return call_name.endswith(
            (
                "Namespace",
                "SimpleNamespace",
                "parse_args",
                "loads",
                "load",
                "read_text",
                "write_text",
            )
        )
    return False


def _inline_inputs(function: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, ...]:
    names: list[str] = []
    for statement in ast.walk(function):
        if isinstance(statement, ast.Assign) and _is_inline_input_value(statement.value):
            for target in statement.targets:
                names.extend(_assignment_target_names(target))
        elif isinstance(statement, ast.AnnAssign) and statement.value and _is_inline_input_value(statement.value):
            names.extend(_assignment_target_names(statement.target))
    filtered: list[str] = []
    for name in names:
        if name.startswith("_") or name in filtered:
            continue
        filtered.append(name)
    return tuple(filtered[:6])


def function_info(runtime_root: Path, node_id: str) -> FunctionInfo:
    path_part, function_name, _ = split_node(node_id)
    source_path = runtime_root.parent / path_part
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    for item in ast.walk(tree):
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == function_name:
            arguments = tuple(arg.arg for arg in [*item.args.args, *item.args.kwonlyargs] if arg.arg not in {"self", "cls"})
            parametrize_names: list[str] = []
            for decorator in item.decorator_list:
                parametrize_names.extend(_parametrize_names_from_decorator(decorator))
            return FunctionInfo(
                source_path=path_part,
                line_no=item.lineno,
                arguments=arguments,
                parametrize_names=tuple(dict.fromkeys(parametrize_names)),
                inline_inputs=_inline_inputs(item),
            )
    raise ValueError(f"Test function was not found: {node_id}")


def _code_list(values: Iterable[str]) -> str:
    values = tuple(values)
    if not values:
        return "なし"
    return ", ".join(f"`{value}`" for value in values)


def _fixture_detail(arguments: tuple[str, ...], parametrize_names: tuple[str, ...]) -> str:
    fixtures = tuple(arg for arg in arguments if arg not in parametrize_names)
    if not fixtures:
        return "なし"
    descriptions = []
    for fixture in fixtures:
        meaning = FIXTURE_MEANINGS.get(fixture)
        descriptions.append(f"`{fixture}` ({meaning})" if meaning else f"`{fixture}`")
    return ", ".join(descriptions)


def input_lines_for_node(runtime_root: Path, node_id: str) -> list[str]:
    info = function_info(runtime_root, node_id)
    _, _, parameter_id = split_node(node_id)
    parameter_names = _code_list(info.parametrize_names)
    parameter_case = f"`{parameter_id}`" if parameter_id else "なし"
    inline_inputs = _code_list(info.inline_inputs)
    if inline_inputs == "なし":
        inline_inputs = "test関数内で生成される固定入力、mock入力、または一時ファイル"
    return [
        INPUT_PREFIX,
        "  - pytest node: 上記コードブロックのnode id",
        f"  - source: `{info.source_path.as_posix()}:{info.line_no}`",
        f"  - fixture/arg: {_fixture_detail(info.arguments, info.parametrize_names)}",
        f"  - parameter: names={parameter_names}, case={parameter_case}",
        f"  - inline input: {inline_inputs}",
    ]


def replace_input_sections(spec_text: str, runtime_root: Path) -> tuple[str, int]:
    cases = {case.case_id: case.node_id for case in parse_spec_cases(spec_text)}
    output: list[str] = []
    current_case: str | None = None
    skipping_input = False
    replaced = 0
    lines = spec_text.splitlines()
    for line in lines:
        if line.startswith(CASE_HEADING_PREFIX):
            current_case = line.strip("# ").strip()
            skipping_input = False
            output.append(line)
            continue
        if skipping_input:
            if line.startswith("- ") and not line.startswith("  - "):
                skipping_input = False
            else:
                continue
        if line.startswith(INPUT_PREFIX):
            skipping_input = True
            continue
        output.append(line)
        if current_case and line.startswith(CONFIRM_PREFIX):
            node_id = cases.get(current_case)
            if node_id:
                output.extend(input_lines_for_node(runtime_root, node_id))
                replaced += 1
    return "\n".join(output) + "\n", replaced


def check_spec(spec_path: Path, runtime_root: Path) -> dict[str, object]:
    spec_text = spec_path.read_text(encoding="utf-8-sig")
    spec_cases = parse_spec_cases(spec_text)
    spec_nodes = [case.node_id for case in spec_cases]
    pytest_nodes = collect_pytest_nodes(runtime_root)
    missing_in_spec = [node for node in pytest_nodes if node not in spec_nodes]
    stale_in_spec = [node for node in spec_nodes if node not in pytest_nodes]
    order_matches = spec_nodes == pytest_nodes

    input_count = spec_text.count(INPUT_PREFIX)
    confirm_count = spec_text.count(CONFIRM_PREFIX)
    expected_count = spec_text.count(EXPECTED_PREFIX)
    bad_position: list[str] = []
    for block in spec_text.split(f"\n{CASE_HEADING_PREFIX}")[1:]:
        case_id = "RT-UT-CASE-" + block.split("\n", 1)[0].strip().split("RT-UT-CASE-", 1)[-1]
        confirm_index = block.find(CONFIRM_PREFIX)
        input_index = block.find(INPUT_PREFIX)
        expected_index = block.find(EXPECTED_PREFIX)
        if not (confirm_index != -1 and input_index != -1 and expected_index != -1 and confirm_index < input_index < expected_index):
            bad_position.append(case_id)

    return {
        "status": "ok" if not missing_in_spec and not stale_in_spec and order_matches and not bad_position else "error",
        "pytest_count": len(pytest_nodes),
        "spec_count": len(spec_nodes),
        "missing_in_spec": missing_in_spec,
        "stale_in_spec": stale_in_spec,
        "order_matches": order_matches,
        "confirm_count": confirm_count,
        "input_count": input_count,
        "expected_count": expected_count,
        "bad_input_position": bad_position,
    }


def resolve_repo_root(value: str | Path | None) -> Path:
    if value:
        return Path(value).resolve()
    return find_repo_root()


def resolve_work_dir(repo_root: Path, value: str | Path) -> Path:
    raw = Path(value)
    return raw if raw.is_absolute() else repo_root / raw


def default_report_path(work_dir: Path) -> Path:
    return work_dir / "context" / "pytest-ut-spec-sync-report.json"


def default_markdown_path(report_path: Path) -> Path:
    return report_path.with_suffix(".md")


def build_report_payload(
    *,
    repo_root: Path,
    runtime_root: Path,
    spec_path: Path,
    check_result: dict[str, object],
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "artifact_type": "pytest-ut-spec-sync-report",
        "generated_at": utc_now_iso(),
        "status": check_result["status"],
        "observability": {
            "kind": "context-noise-detection",
            "detects": [
                "pytest node missing from UT specification",
                "stale pytest node in UT specification",
                "pytest collection order mismatch",
                "確認内容 / 入力値 / 期待結果の位置ずれ",
            ],
        },
        "inputs": {
            "runtime_root": relative_to_repo(repo_root, runtime_root),
            "spec_path": relative_to_repo(repo_root, spec_path),
            "pytest_collection": "python -m pytest --collect-only -q tests",
        },
        "result": check_result,
    }


def write_report(report_path: Path, payload: dict[str, Any]) -> None:
    write_json(report_path, payload)


def render_report_markdown(payload: dict[str, Any]) -> str:
    result = payload.get("result", {})
    observability = payload.get("observability", {})
    detects = observability.get("detects", [])
    missing = result.get("missing_in_spec", [])
    stale = result.get("stale_in_spec", [])
    bad_positions = result.get("bad_input_position", [])
    status = payload.get("status", "unknown")

    def list_or_none(values: list[Any]) -> str:
        return "\n".join(f"- `{value}`" for value in values) if values else "- なし"

    return f"""# Pytest UT Spec Sync Report

## Summary

| Item | Value |
| --- | --- |
| Status | `{status}` |
| Generated At | `{payload.get("generated_at", "")}` |
| Runtime Root | `{payload.get("inputs", {}).get("runtime_root", "")}` |
| Spec Path | `{payload.get("inputs", {}).get("spec_path", "")}` |
| Pytest Count | {result.get("pytest_count", 0)} |
| Spec Count | {result.get("spec_count", 0)} |
| Order Matches | {result.get("order_matches", False)} |
| Confirm Count | {result.get("confirm_count", 0)} |
| Input Count | {result.get("input_count", 0)} |
| Expected Count | {result.get("expected_count", 0)} |

## Context Noise Detection

{list_or_none(list(detects))}

## Missing In Spec

{list_or_none(list(missing))}

## Stale In Spec

{list_or_none(list(stale))}

## Bad Input Position

{list_or_none(list(bad_positions))}

## Context First

このreportは `test-evidence` contextとして `context-manifest.json` に登録できます。後続workflowはmanifestからこのreportを読み、pytest実体とUT仕様書の同期状態を判断できます。
"""


def write_report_markdown(markdown_path: Path, payload: dict[str, Any]) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_report_markdown(payload).rstrip() + "\n", encoding="utf-8")


def register_test_evidence_context(
    *,
    repo_root: Path,
    work_dir: Path,
    report_path: Path,
    check_result: dict[str, object],
    required: bool,
) -> dict[str, Any]:
    status = "available" if check_result.get("status") == "ok" else "human-check-required"
    return context_first.register_context(
        repo_root,
        work_dir,
        work_id=work_dir.name,
        context_type="test-evidence",
        path=report_path,
        required=required,
        generated_by="pytest-ut-spec-sync",
        owner="workflow",
        schema=REPORT_SCHEMA,
        status=status,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synchronize runtime pytest UT case specification with pytest collection.")
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("../docs/reference/runtime-pytest-ut/case-specification.md"),
        help="Path to runtime pytest UT case specification.",
    )
    parser.add_argument("--runtime-root", type=Path, default=Path("."), help="Path to runtime directory.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="Check spec node ids and input sections against pytest collection.")
    check.add_argument("--repo-root", default="", help="Repository root used for report and Context First paths.")
    check.add_argument("--report", default="", help="Optional JSON report path for CI artifacts or Context First evidence.")
    check.add_argument("--markdown", default="", help="Optional Markdown report path for human-readable evidence.")
    check.add_argument("--work-dir", default="", help="Optional work directory for Context First manifest registration.")
    check.add_argument("--register-context", action="store_true", help="Register the sync report as Context First test-evidence.")
    check.add_argument("--required-context", action="store_true", help="Mark the registered test-evidence context as required.")
    subparsers.add_parser("fix-inputs", help="Regenerate input sections from pytest function signatures and AST metadata.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    spec_path = args.spec.resolve()
    runtime_root = args.runtime_root.resolve()
    if args.command == "fix-inputs":
        spec_text = spec_path.read_text(encoding="utf-8-sig")
        new_text, replaced = replace_input_sections(spec_text, runtime_root)
        spec_path.write_text(new_text, encoding="utf-8-sig", newline="\n")
        print(json.dumps({"status": "ok", "updated_input_sections": replaced}, ensure_ascii=False, indent=2))
        return 0
    result = check_spec(spec_path, runtime_root)
    if args.report or args.register_context:
        repo_root = resolve_repo_root(args.repo_root)
        if args.register_context and not args.work_dir:
            raise SystemExit("--work-dir is required when --register-context is used.")
        work_dir = resolve_work_dir(repo_root, args.work_dir) if args.work_dir else Path()
        report_path = Path(args.report).resolve() if args.report else default_report_path(work_dir)
        payload = build_report_payload(
            repo_root=repo_root,
            runtime_root=runtime_root,
            spec_path=spec_path,
            check_result=result,
        )
        write_report(report_path, payload)
        markdown_path = Path(args.markdown).resolve() if args.markdown else default_markdown_path(report_path)
        write_report_markdown(markdown_path, payload)
        result = {
            **result,
            "report_path": relative_to_repo(repo_root, report_path),
            "markdown_path": relative_to_repo(repo_root, markdown_path),
        }
        if args.register_context:
            manifest = register_test_evidence_context(
                repo_root=repo_root,
                work_dir=work_dir,
                report_path=report_path,
                check_result=result,
                required=args.required_context,
            )
            result = {
                **result,
                "context_manifest": relative_to_repo(repo_root, context_first.manifest_path_for_work_dir(work_dir)),
                "context_types": sorted(
                    item.get("type", "")
                    for item in manifest.get("contexts", [])
                    if isinstance(item, dict)
                ),
            }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
