from __future__ import annotations

import json
from pathlib import Path

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
    assert (
        sync.normalize_collected_node(r"tests\test_sample.py::test_example[name-\u521d\u671f]")
        == r"runtime/tests/test_sample.py::test_example[name-\u521d\u671f]"
    )
    assert cases == [sync.SpecCase("RT-UT-CASE-001", "runtime/tests/test_sample.py::test_example[value0]")]


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


def test_report_payload_and_context_first_registration(tmp_path: Path) -> None:
    repo_root = tmp_path
    runtime_root = repo_root / "runtime"
    spec_path = repo_root / "docs" / "reference" / "runtime-pytest-ut-case-specification.md"
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
