from __future__ import annotations

import ast
import json
import runpy
import subprocess
from pathlib import Path

import pytest

from runtime.tools import pytest_ut_spec_sync as sync


def test_normalize_collected_node_and_parse_spec_cases() -> None:
    text = """# Spec
#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_sample.py::test_example[value0]
```

- 確認内容: sample
- 入力値: old
- 期待結果: pass
"""

    cases = sync.parse_spec_cases(text)

    assert sync.normalize_collected_node("tests/test_sample.py::test_example") == "runtime/tests/test_sample.py::test_example"
    assert sync.normalize_collected_node("runtime/tests/test_sample.py::test_example") == "runtime/tests/test_sample.py::test_example"
    assert sync.normalize_collected_node("external/test_sample.py::test_example") == "external/test_sample.py::test_example"
    assert (
        sync.normalize_collected_node(r"tests\test_sample.py::test_example[name-\u521d\u671f]")
        == r"runtime/tests/test_sample.py::test_example[name-\u521d\u671f]"
    )
    assert cases == [sync.SpecCase("RT-UT-CASE-001", "runtime/tests/test_sample.py::test_example[value0]")]


def test_defensive_specimen_collect_pytest_nodes_filters_noise_and_reports_collect_error(monkeypatch, tmp_path: Path) -> None:
    captured_envs: list[dict[str, str]] = []

    def failed_run(command, cwd, text, capture_output, check, env):
        captured_envs.append(env)
        return subprocess.CompletedProcess(command, 2, stdout="", stderr="collect failed")

    monkeypatch.setattr(sync.subprocess, "run", failed_run)
    with pytest.raises(RuntimeError, match="collect failed"):
        sync.collect_pytest_nodes(tmp_path)

    assert captured_envs[-1][sync.PYTEST_DISABLE_PLUGIN_AUTOLOAD_ENV] == "1"

    def noisy_run(command, cwd, text, capture_output, check, env):
        captured_envs.append(env)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="\n".join(
                [
                    "collected 2 items",
                    "tests/test_sample.py::test_from_tests",
                    "runtime/tests/test_sample.py::test_from_runtime",
                    "external/test_sample.py::test_ignored",
                    "plain line",
                ]
            ),
            stderr="",
        )

    monkeypatch.setattr(sync.subprocess, "run", noisy_run)

    assert sync.collect_pytest_nodes(tmp_path) == [
        "runtime/tests/test_sample.py::test_from_tests",
        "runtime/tests/test_sample.py::test_from_runtime",
    ]
    assert captured_envs[-1][sync.PYTEST_DISABLE_PLUGIN_AUTOLOAD_ENV] == "1"


def test_defensive_specimen_script_path_load_exposes_helpers() -> None:
    namespace = runpy.run_path(str(Path(sync.__file__)))

    assert namespace["runtime_dir_from_spec"]
    assert namespace["build_parser"]


def test_defensive_specimen_parse_spec_closing_fence_without_node() -> None:
    text = """# Spec
#### RT-UT-CASE-001

- pytest node id:

```text
not-a-runtime-node
```
"""

    assert sync.parse_spec_cases(text) == []


def test_defensive_specimen_ast_decorator_shapes_are_ignored_or_reduced() -> None:
    tree = ast.parse(
        """
@custom_decorator
def test_name_decorator():
    pass

@pytest.mark.skip()
def test_non_parametrize_decorator():
    pass

@pytest.mark.parametrize()
def test_parametrize_without_args():
    pass

@pytest.mark.parametrize(("left", 1, "right"), [(1, 2)])
def test_parametrize_tuple_names(left, right):
    pass

@pytest.mark.parametrize(parameter_names, [(1, 2)])
def test_parametrize_dynamic_names(left, right):
    pass
"""
    )
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

    assert sync._parametrize_names_from_decorator(functions[0].decorator_list[0]) == ()
    assert sync._parametrize_names_from_decorator(functions[1].decorator_list[0]) == ()
    assert sync._parametrize_names_from_decorator(functions[2].decorator_list[0]) == ()
    assert sync._parametrize_names_from_decorator(functions[3].decorator_list[0]) == ("left", "right")
    assert sync._parametrize_names_from_decorator(functions[4].decorator_list[0]) == ()


def test_defensive_specimen_ast_input_helpers_preserve_only_explainable_inputs(tmp_path: Path) -> None:
    assert sync._simple_call_name(ast.Constant(value=1)) == ""
    assert sync._simple_call_name(ast.Attribute(value=ast.Constant(value=1), attr="fallback", ctx=ast.Load())) == "fallback"
    assert sync._assignment_target_names(ast.Attribute(value=ast.Name(id="obj", ctx=ast.Load()), attr="field", ctx=ast.Store())) == []
    assert sync._is_inline_input_value(ast.Name(id="runtime_value", ctx=ast.Load())) is False
    assert sync._is_inline_input_value(ast.Call(func=ast.Name(id="custom_factory", ctx=ast.Load()), args=[], keywords=[])) is False

    runtime_root = tmp_path / "runtime"
    test_dir = runtime_root / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "test_sample.py").write_text(
        """
def test_example():
    value = "x"
    value = "duplicate"
    typed: dict = {"ok": True}
    _hidden = "not public input"
    left, right = (1, 2)
    obj.field = "not a simple target"
    assert value
""",
        encoding="utf-8",
    )

    info = sync.function_info(runtime_root, "runtime/tests/test_sample.py::test_example")

    assert info.inline_inputs == ("value", "typed", "left", "right")


def test_defensive_specimen_function_info_and_input_lines_for_no_inline_inputs(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    test_dir = runtime_root / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "test_sample.py").write_text(
        """
def test_example():
    assert True
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Test function was not found"):
        sync.function_info(runtime_root, "runtime/tests/test_sample.py::test_missing")

    lines = sync.input_lines_for_node(runtime_root, "runtime/tests/test_sample.py::test_example")

    assert lines[-1].startswith("  - inline input:")
    assert "test" in lines[-1]


def test_input_lines_include_source_fixture_parameter_and_inline_values(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    test_dir = runtime_root / "tests"
    test_dir.mkdir(parents=True)
    test_file = test_dir / "test_sample.py"
    test_file.write_text(
        """
import pytest


@pytest.mark.parametrize("payload, expected", [({"a": 1}, "ok")])
def test_example(tmp_path, monkeypatch, payload, expected):
    args = ["--flag"]
    config = {"mode": "dry-run"}
    assert payload
""",
        encoding="utf-8",
    )

    lines = sync.input_lines_for_node(runtime_root, "runtime/tests/test_sample.py::test_example[payload0]")
    joined = "\n".join(lines)

    assert lines[0] == "- 入力値:"
    assert "runtime/tests/test_sample.py:6" in joined
    assert "`tmp_path` (temporary filesystem)" in joined
    assert "`monkeypatch` (environment / function monkeypatch)" in joined
    assert "names=`payload`, `expected`, case=`payload0`" in joined
    assert "`args`, `config`" in joined


def test_replace_input_sections_preserves_confirmation_expected_order(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    test_dir = runtime_root / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "test_sample.py").write_text(
        """
def test_example(tmp_path):
    value = "x"
    assert value
""",
        encoding="utf-8",
    )
    spec = """# Spec
#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_sample.py::test_example
```

- 確認内容: sample
- 入力値: old
- 期待結果: pass
"""

    updated, replaced = sync.replace_input_sections(spec, runtime_root)

    assert replaced == 1
    assert "- 確認内容: sample\n- 入力値:\n  - pytest node:" in updated
    assert updated.index("- 確認内容: sample") < updated.index("- 入力値:") < updated.index("- 期待結果: pass")
    assert "- 入力値: old" not in updated


def test_defensive_specimen_replace_input_sections_skips_legacy_multiline_input_until_next_field(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    test_dir = runtime_root / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "test_sample.py").write_text(
        """
def test_example():
    assert True
""",
        encoding="utf-8",
    )
    spec = f"""# Spec
#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_sample.py::test_example
```

{sync.CONFIRM_PREFIX} sample
{sync.INPUT_PREFIX} old
  - stale child line
  - another stale child line
{sync.EXPECTED_PREFIX} pass
"""

    updated, replaced = sync.replace_input_sections(spec, runtime_root)

    assert replaced == 1
    assert "stale child line" not in updated
    assert updated.count(sync.INPUT_PREFIX) == 1


def test_defensive_specimen_replace_input_sections_keeps_confirm_without_node_id(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    runtime_root.mkdir()
    spec = f"""# Spec
#### RT-UT-CASE-999

{sync.CONFIRM_PREFIX} orphan confirm
{sync.EXPECTED_PREFIX} keep
"""

    updated, replaced = sync.replace_input_sections(spec, runtime_root)

    assert replaced == 0
    assert sync.INPUT_PREFIX not in updated
    assert "orphan confirm" in updated


def test_check_spec_reports_missing_stale_order_and_bad_input(monkeypatch, tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.md"
    spec_path.write_text(
        """# Spec
#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_old.py::test_old
```

- 確認内容: old
- 期待結果: pass
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(sync, "collect_pytest_nodes", lambda runtime_root: ["runtime/tests/test_new.py::test_new"])

    result = sync.check_spec(spec_path, tmp_path / "runtime")

    assert result["status"] == "error"
    assert result["missing_in_spec"] == ["runtime/tests/test_new.py::test_new"]
    assert result["stale_in_spec"] == ["runtime/tests/test_old.py::test_old"]
    assert result["order_matches"] is False
    assert result["bad_input_position"] == ["RT-UT-CASE-001"]


def test_check_spec_reads_split_case_files(monkeypatch, tmp_path: Path) -> None:
    spec_path = tmp_path / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    case_dir = spec_path.with_name("cases")
    case_dir.mkdir(parents=True)
    spec_path.write_text("# Spec index\n", encoding="utf-8")
    (case_dir / "test_sample.md").write_text(
        """# test_sample.py
#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_sample.py::test_example
```

- 確認内容: sample
- 入力値:
  - pytest node: 上記コードブロックのnode id
- 期待結果: pass
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(sync, "collect_pytest_nodes", lambda runtime_root: ["runtime/tests/test_sample.py::test_example"])

    assert sync.spec_case_dir(spec_path) == case_dir
    assert sync.spec_part_paths(spec_path) == [spec_path, case_dir / "test_sample.md"]
    assert "runtime/tests/test_sample.py::test_example" in sync.read_spec_text(spec_path)
    assert sync.check_spec(spec_path, tmp_path / "runtime")["status"] == "ok"


def test_check_spec_accepts_ascii_case_field_labels(monkeypatch, tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.md"
    spec_path.write_text(
        """# Spec
#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_sample.py::test_example
```

- Confirm: sample
- Input:
  - pytest node: runtime pytest node id
- Expected: pass
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(sync, "collect_pytest_nodes", lambda runtime_root: ["runtime/tests/test_sample.py::test_example"])

    result = sync.check_spec(spec_path, tmp_path / "runtime")

    assert result["status"] == "ok"
    assert result["confirm_count"] == 1
    assert result["input_count"] == 1
    assert result["expected_count"] == 1


def test_scaffold_missing_cases_creates_ordered_split_case_blocks(monkeypatch, tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    test_dir = runtime_root / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "test_sample.py").write_text(
        """
def test_first():
    assert True


def test_second(tmp_path):
    value = "x"
    assert value
""",
        encoding="utf-8",
    )
    spec_path = tmp_path / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    case_dir = spec_path.with_name("cases")
    case_dir.mkdir(parents=True)
    spec_path.write_text("# Spec index\n", encoding="utf-8")
    (case_dir / "test_sample.md").write_text(
        """# test_sample.py
#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_sample.py::test_second
```

- Confirm: existing
- Input:
  - pytest node: above node id
- Expected: pass
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sync,
        "collect_pytest_nodes",
        lambda runtime_root: [
            "runtime/tests/test_sample.py::test_first",
            "runtime/tests/test_sample.py::test_second",
        ],
    )

    result = sync.scaffold_missing_cases(spec_path, runtime_root)
    text = (case_dir / "test_sample.md").read_text(encoding="utf-8")

    assert result["status"] == "repaired"
    assert result["repairs"][0]["node_id"] == "runtime/tests/test_sample.py::test_first"
    assert text.index("test_first") < text.index("test_second")
    assert "| cases | 2 |" in text
    assert sync.check_spec(spec_path, runtime_root)["status"] == "ok"


def test_main_fix_inputs_and_check_json_output(monkeypatch, tmp_path: Path, capsys) -> None:
    runtime_root = tmp_path / "runtime"
    test_dir = runtime_root / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "test_sample.py").write_text(
        """
def test_example():
    value = "x"
    assert value
""",
        encoding="utf-8",
    )
    spec_path = tmp_path / "spec.md"
    spec_path.write_text(
        """# Spec
#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_sample.py::test_example
```

- 確認内容: sample
- 入力値: old
- 期待結果: pass
""",
        encoding="utf-8",
    )

    assert sync.main(["--spec", str(spec_path), "--runtime-root", str(runtime_root), "fix-inputs"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["updated_input_sections"] == 1

    monkeypatch.setattr(sync, "collect_pytest_nodes", lambda runtime_root: ["runtime/tests/test_sample.py::test_example"])
    assert sync.main(["--spec", str(spec_path), "--runtime-root", str(runtime_root), "check"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"


def test_main_fix_inputs_updates_split_case_files(monkeypatch, tmp_path: Path, capsys) -> None:
    runtime_root = tmp_path / "runtime"
    test_dir = runtime_root / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "test_sample.py").write_text(
        """
def test_example(tmp_path):
    value = "x"
    assert value
""",
        encoding="utf-8",
    )
    spec_path = tmp_path / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    case_dir = spec_path.with_name("cases")
    case_dir.mkdir(parents=True)
    spec_path.write_text("# Spec index\n", encoding="utf-8")
    case_path = case_dir / "test_sample.md"
    case_path.write_text(
        """# test_sample.py
#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_sample.py::test_example
```

- 確認内容: sample
- 入力値: old
- 期待結果: pass
""",
        encoding="utf-8",
    )

    assert sync.main(["--spec", str(spec_path), "--runtime-root", str(runtime_root), "fix-inputs"]) == 0
    payload = json.loads(capsys.readouterr().out)
    updated = case_path.read_text(encoding="utf-8-sig")

    assert payload["updated_input_sections"] == 1
    assert "- 入力値: old" not in updated
    assert "runtime/tests/test_sample.py:2" in updated


def test_defensive_specimen_default_paths_and_register_context_requires_work_dir(monkeypatch, tmp_path: Path) -> None:
    spec_path = tmp_path / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    spec_path.parent.mkdir(parents=True)
    spec_path.write_text("# spec\n", encoding="utf-8")
    assert sync.runtime_dir_from_spec(spec_path) == tmp_path / "runtime"

    monkeypatch.setattr(sync, "find_repo_root", lambda: tmp_path)
    assert sync.resolve_repo_root("") == tmp_path
    assert sync.resolve_work_dir(tmp_path, "work/issue-1") == tmp_path / "work" / "issue-1"
    assert sync.resolve_work_dir(tmp_path, tmp_path / "work" / "issue-2") == tmp_path / "work" / "issue-2"
    assert sync.default_report_path(tmp_path / "work" / "issue-1") == tmp_path / "work" / "issue-1" / "context" / "pytest-ut-spec-sync-report.json"
    assert sync.default_markdown_path(Path("report.json")) == Path("report.md")

    monkeypatch.setattr(sync, "collect_pytest_nodes", lambda runtime_root: [])
    with pytest.raises(SystemExit, match="--work-dir is required"):
        sync.main(["--spec", str(spec_path), "--runtime-root", str(tmp_path / "runtime"), "check", "--register-context"])


def test_report_payload_and_context_first_registration(tmp_path: Path) -> None:
    repo_root = tmp_path
    runtime_root = repo_root / "runtime"
    spec_path = repo_root / "docs" / "reference" / "runtime-pytest-ut" / "case-specification.md"
    work_dir = repo_root / "runtime" / ".pytest_cache" / "context-first-ci"
    report_path = work_dir / "context" / "pytest-ut-spec-sync-report.json"
    check_result = {
        "status": "ok",
        "pytest_count": 1,
        "spec_count": 1,
        "missing_in_spec": [],
        "stale_in_spec": [],
        "order_matches": True,
        "confirm_count": 1,
        "input_count": 1,
        "expected_count": 1,
        "bad_input_position": [],
    }

    payload = sync.build_report_payload(
        repo_root=repo_root,
        runtime_root=runtime_root,
        spec_path=spec_path,
        check_result=check_result,
    )
    sync.write_report(report_path, payload)
    manifest = sync.register_test_evidence_context(
        repo_root=repo_root,
        work_dir=work_dir,
        report_path=report_path,
        check_result=check_result,
        required=True,
    )

    saved = json.loads(report_path.read_text(encoding="utf-8"))
    markdown = sync.render_report_markdown(payload)
    entry = manifest["contexts"][0]
    assert saved["artifact_type"] == "pytest-ut-spec-sync-report"
    assert saved["observability"]["kind"] == "context-noise-detection"
    assert "# Pytest UT Spec Sync Report" in markdown
    assert "Context Noise Detection" in markdown
    assert entry["type"] == "test-evidence"
    assert entry["schema"] == sync.REPORT_SCHEMA
    assert entry["required"] is True
    assert entry["status"] == "available"


def test_defensive_specimen_main_uses_default_report_paths_when_registering_context(monkeypatch, tmp_path: Path, capsys) -> None:
    repo_root = tmp_path
    runtime_root = repo_root / "runtime"
    test_dir = runtime_root / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "test_sample.py").write_text(
        """
def test_example():
    assert True
""",
        encoding="utf-8",
    )
    spec_path = repo_root / "docs" / "reference" / "spec.md"
    spec_path.parent.mkdir(parents=True)
    spec_path.write_text(
        f"""# Spec
#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_sample.py::test_example
```

{sync.CONFIRM_PREFIX} sample
{sync.INPUT_PREFIX}
  - pytest node: node id
{sync.EXPECTED_PREFIX} pass
""",
        encoding="utf-8",
    )
    work_dir = repo_root / "runtime" / ".pytest_cache" / "context-first-ci"
    monkeypatch.setattr(sync, "collect_pytest_nodes", lambda runtime_root: ["runtime/tests/test_sample.py::test_example"])

    code = sync.main(
        [
            "--spec",
            str(spec_path),
            "--runtime-root",
            str(runtime_root),
            "check",
            "--repo-root",
            str(repo_root),
            "--work-dir",
            str(work_dir),
            "--register-context",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["report_path"] == "runtime/.pytest_cache/context-first-ci/context/pytest-ut-spec-sync-report.json"
    assert output["markdown_path"] == "runtime/.pytest_cache/context-first-ci/context/pytest-ut-spec-sync-report.md"
    assert (work_dir / "context" / "pytest-ut-spec-sync-report.md").exists()


def test_defensive_specimen_main_writes_report_without_context_registration(monkeypatch, tmp_path: Path, capsys) -> None:
    repo_root = tmp_path
    runtime_root = repo_root / "runtime"
    runtime_root.mkdir()
    spec_path = repo_root / "docs" / "reference" / "spec.md"
    spec_path.parent.mkdir(parents=True)
    spec_path.write_text("# spec\n", encoding="utf-8")
    report_path = runtime_root / ".pytest_cache" / "standalone-report.json"
    monkeypatch.setattr(sync, "collect_pytest_nodes", lambda runtime_root: [])

    code = sync.main(
        [
            "--spec",
            str(spec_path),
            "--runtime-root",
            str(runtime_root),
            "check",
            "--repo-root",
            str(repo_root),
            "--report",
            str(report_path),
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["report_path"] == "runtime/.pytest_cache/standalone-report.json"
    assert output["markdown_path"] == "runtime/.pytest_cache/standalone-report.md"
    assert "context_manifest" not in output


def test_main_check_writes_report_and_registers_context(monkeypatch, tmp_path: Path, capsys) -> None:
    repo_root = tmp_path
    runtime_root = repo_root / "runtime"
    test_dir = runtime_root / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "test_sample.py").write_text(
        """
def test_example():
    assert True
""",
        encoding="utf-8",
    )
    spec_path = repo_root / "docs" / "reference" / "spec.md"
    spec_path.parent.mkdir(parents=True)
    spec_path.write_text(
        """# Spec
#### RT-UT-CASE-001

- pytest node id:

```text
runtime/tests/test_sample.py::test_example
```

- 確認内容: sample
- 入力値:
  - pytest node: 上記コードブロックのnode id
- 期待結果: pass
""",
        encoding="utf-8",
    )
    work_dir = repo_root / "runtime" / ".pytest_cache" / "context-first-ci"
    report_path = runtime_root / ".pytest_cache" / "pytest-ut-spec-sync-report.json"
    markdown_path = runtime_root / ".pytest_cache" / "pytest-ut-spec-sync-report.md"
    monkeypatch.setattr(sync, "collect_pytest_nodes", lambda runtime_root: ["runtime/tests/test_sample.py::test_example"])

    code = sync.main(
        [
            "--spec",
            str(spec_path),
            "--runtime-root",
            str(runtime_root),
            "check",
            "--repo-root",
            str(repo_root),
            "--work-dir",
            str(work_dir),
            "--report",
            str(report_path),
            "--markdown",
            str(markdown_path),
            "--register-context",
            "--required-context",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    manifest = json.loads((work_dir / "context" / "context-manifest.json").read_text(encoding="utf-8"))
    assert code == 0
    assert output["status"] == "ok"
    assert output["report_path"] == "runtime/.pytest_cache/pytest-ut-spec-sync-report.json"
    assert output["markdown_path"] == "runtime/.pytest_cache/pytest-ut-spec-sync-report.md"
    assert output["context_manifest"] == "runtime/.pytest_cache/context-first-ci/context/context-manifest.json"
    assert "test-evidence" in output["context_types"]
    assert manifest["contexts"][0]["generated_by"] == "pytest-ut-spec-sync"
    assert "# Pytest UT Spec Sync Report" in markdown_path.read_text(encoding="utf-8")
