from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from runtime.workflow import gui_mode, web_svg_layout_mode


SVG_TEXT = """\
<svg width="640" height="480" viewBox="0 0 640 480" xmlns="http://www.w3.org/2000/svg">
  <title>Robot Console</title>
  <g id="header_status">
    <text id="status_label" x="10" y="20">Ready</text>
  </g>
  <g id="control_panel">
    <rect id="connect_button" class="btn primary" x="10" y="40" width="120" height="32" style="fill: #333; stroke: #111"/>
    <text id="connect_text" x="20" y="60">Start</text>
    <rect id="search_input" class="input" x="10" y="90" width="180" height="32"/>
    <rect id="mode_select" class="dropdown" x="10" y="130" width="180" height="32"/>
    <rect id="enable_check" class="toggle" x="10" y="170" width="24" height="24"/>
    <rect id="speed_slider" class="slider" x="10" y="210" width="180" height="24"/>
  </g>
  <g id="video_view">
    <rect id="camera_display" class="display viewport" x="220" y="40" width="360" height="280"/>
  </g>
</svg>
"""


WEB_SVG_TEXT = """\
<svg width="1024" height="768" viewBox="0 0 1024 768" xmlns="http://www.w3.org/2000/svg">
  <title>Dashboard</title>
  <g id="header_toolbar">
    <text id="page_title">Dashboard</text>
    <rect id="save_button" class="cta button" width="120" height="32"/>
    <text id="save_label">Save</text>
  </g>
  <g id="filter_form">
    <rect id="search_field" class="input" width="200" height="32"/>
    <rect id="status_dropdown" class="select" width="200" height="32"/>
    <rect id="active_toggle" class="switch" width="40" height="24"/>
  </g>
  <g id="metric_summary">
    <rect id="kpi_metric" class="metric card" width="200" height="120"/>
  </g>
  <g id="content_grid">
    <rect id="result_table" class="table grid" width="600" height="320"/>
  </g>
</svg>
"""


def write_svg(path: Path, text: str = SVG_TEXT) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_work(tmp_path: Path, issue_id: str = "SYS-100") -> tuple[Path, Path]:
    repo_root = tmp_path
    work_dir = repo_root / "work" / issue_id
    (work_dir / "context").mkdir(parents=True)
    return repo_root, work_dir


def test_gui_mode_parse_model_render_and_validate_outputs(tmp_path: Path) -> None:
    repo_root, work_dir = make_work(tmp_path, "SYS-100")
    svg_input_dir = repo_root / "work" / "requirements" / "svg-input"
    svg_path = write_svg(work_dir / "input" / "gui" / "SYS_console.svg")

    document = gui_mode.parse_svg(svg_path)
    model = gui_mode.build_model([document], "SYS-100", "system-development")
    state = gui_mode.write_artifacts(
        repo_root,
        work_dir,
        "SYS-100",
        "system-development",
        [svg_path],
        ["work/requirements/svg-input/SYS_console.svg"],
        svg_input_dir,
        "SYS",
        [document],
        model,
    )
    validation = gui_mode.validate_outputs(work_dir)

    assert document.title == "Robot Console"
    assert {widget["type"] for widget in model["widgets"]} >= {"button", "label", "line_edit", "combo_box", "check_box", "slider", "display"}
    assert model["relationships"][0]["event"] == "clicked"
    assert state["status"] == "complete"
    assert validation["status"] == "pass"
    assert (work_dir / "gac-uac" / "generated" / "pyqt6" / "main_window.py").exists()


def test_gui_mode_helpers_cover_prefix_discovery_claim_and_validation_errors(tmp_path: Path) -> None:
    repo_root, work_dir = make_work(tmp_path, "FEAT-200")
    inbox = repo_root / "work" / "requirements" / "svg-input"
    source = write_svg(inbox / "FEAT_console.svg")
    write_svg(inbox / "UNKNOWN_console.svg")
    (inbox / "FEAT_bad.svg").write_text("<svg><g></svg>", encoding="utf-8")

    inspection = gui_mode.inspect_svg_input_dir(repo_root, inbox)
    claimed, sources = gui_mode.claim_svg_inputs(repo_root, work_dir, inbox, "FEAT")

    assert inspection["status"] == "fail"
    assert any(error.startswith("unknown-prefix:") for error in inspection["errors"])
    assert any(error.startswith("invalid-svg:") for error in inspection["errors"])
    assert source.name not in {path.name for path in inbox.glob("*.svg")}
    assert [path.name for path in claimed] == ["FEAT_bad.svg", "FEAT_console.svg"]
    assert sources[0].startswith("work/requirements/svg-input/")
    assert gui_mode.discover_svg_files(work_dir)
    assert gui_mode.svg_prefix(Path("WEB_SYS_dashboard.svg")) == "WEB_SYS"


def test_gui_mode_renderers_and_failure_paths(tmp_path: Path) -> None:
    repo_root, work_dir = make_work(tmp_path, "FIX-300")
    svg_path = write_svg(work_dir / "input" / "gui" / "FIX_console.svg")
    document = gui_mode.parse_svg(svg_path)
    model = gui_mode.build_model([document], "FIX-300", "corrective-improvement")

    assert gui_mode.infer_mode("SYS-1", "auto") == "system-development"
    assert gui_mode.infer_mode("FEAT-1", "auto") == "feature-development"
    assert gui_mode.infer_mode("FIX-1", "auto") == "corrective-improvement"
    assert gui_mode.infer_mode("OTHER-1", "auto") == "generic-gui"
    assert gui_mode.safe_identifier("123 bad id", "fallback") == "item_123_bad_id"
    assert gui_mode.parse_style("fill: red; ignored; stroke: blue") == {"fill": "red", "stroke": "blue"}
    assert gui_mode.qt_widget_name("unknown") == "QWidget"
    assert "# SVG Analysis" in gui_mode.render_svg_analysis([document], "FIX-300", "corrective-improvement")
    assert "semantic-layout-graph" not in gui_mode.render_semantic_yaml(model)
    assert "QMainWindow" in gui_mode.render_layout_spec(model, "FIX-300", "corrective-improvement")
    assert "PyQt6 Generation Plan" in gui_mode.render_generation_plan("FIX-300", "corrective-improvement", "pyqt6")
    assert "QTest Generation Plan" in gui_mode.render_generation_plan("FIX-300", "corrective-improvement", "qtest")
    assert "class MainWindow" in gui_mode.render_pyqt6(model)
    assert "QSignalSpy" in gui_mode.render_qtest(model)
    assert "human-review-required" in gui_mode.render_review("FIX-300", "corrective-improvement", [svg_path])
    assert "GUI SVG Input Inbox" in gui_mode.input_readme()

    with pytest.raises(ValueError, match="Invalid SVG XML"):
        gui_mode.parse_svg(write_svg(tmp_path / "bad.svg", "<svg><g></svg>"))


def test_gui_mode_model_fallbacks_duplicate_ids_and_no_relationship_yaml(tmp_path: Path) -> None:
    repo_root, work_dir = make_work(tmp_path, "GUI-001")
    decorative_svg = write_svg(
        work_dir / "input" / "gui" / "GUI_decorative.svg",
        """\
<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
  <g id="footer_log"><path id="shape" d="M0,0 L10,10"/></g>
</svg>
""",
    )
    duplicate_svg = write_svg(
        work_dir / "input" / "gui" / "GUI_duplicate.svg",
        """\
<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
  <g id="content">
    <text id="same">Alpha</text>
    <text id="same">Beta</text>
    <text id="orphan_button_text">Apply</text>
  </g>
</svg>
""",
    )

    decorative_doc = gui_mode.parse_svg(decorative_svg)
    fallback_model = gui_mode.build_model([decorative_doc], "GUI-001", "generic-gui")
    duplicate_model = gui_mode.build_model([gui_mode.parse_svg(duplicate_svg)], "GUI-001", "generic-gui")

    assert fallback_model["widgets"] == [
        {
            "id": "content_label",
            "type": "label",
            "label": "GUI content",
            "parent": "footer_log",
            "responsibility": "画面内容を表示する",
            "source": "GUI_decorative.svg",
        }
    ]
    assert "relationships:\n  []" in gui_mode.render_semantic_yaml(fallback_model)
    assert gui_mode.infer_area_role("footer_log") == "information_area"
    assert gui_mode.infer_area_role("misc") == "content_area"
    assert [widget["id"] for widget in duplicate_model["widgets"]] == ["same", "same_2", "orphan_button_text"]
    assert duplicate_model["widgets"][-1]["type"] == "button"
    assert duplicate_model["relationships"][0]["from"] == "orphan_button_text"
    assert gui_mode.infer_mode("SYS-1", "feature-development") == "feature-development"
    assert gui_mode.infer_responsibility("unknown", "Decoration").endswith("表示する")


def test_gui_mode_input_init_inspect_and_claim_edge_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo_root, work_dir = make_work(tmp_path, "SYS-500")
    inbox = repo_root / "work" / "requirements" / "svg-input"

    init_result = gui_mode.run_init_input(
        argparse.Namespace(repo_root=str(repo_root), svg_input_dir=None, force=False)
    )
    readme = repo_root / init_result["readme"]
    readme.write_text("custom\n", encoding="utf-8")
    gui_mode.run_init_input(argparse.Namespace(repo_root=str(repo_root), svg_input_dir=None, force=False))
    assert readme.read_text(encoding="utf-8") == "custom\n"
    gui_mode.run_init_input(argparse.Namespace(repo_root=str(repo_root), svg_input_dir=None, force=True))
    assert "GUI SVG Input Inbox" in readme.read_text(encoding="utf-8-sig")

    write_svg(inbox / "SYS_console.svg")
    write_svg(inbox / "FEAT_console.svg")
    write_svg(inbox / "WEB_SYS_console.svg")
    (inbox / "note.txt").write_text("ignore\n", encoding="utf-8")
    inspection = gui_mode.run_inspect_input(argparse.Namespace(repo_root=str(repo_root), svg_input_dir=str(inbox)))

    assert inspection["status"] == "pass"
    assert inspection["file_count"] == 3
    assert any(warning.startswith("same-screen-name:console:") for warning in inspection["warnings"])
    assert gui_mode.discover_inbox_svg_files(repo_root / "missing", "SYS") == []
    assert gui_mode.svg_prefix(Path("plain.svg")) == ""
    not_svg = tmp_path / "not-svg.xml"
    not_svg.write_text("<not-svg />", encoding="utf-8")
    assert gui_mode.validate_svg_xml(not_svg) == (False, "root element is not svg: not-svg")

    existing = write_svg(work_dir / "input" / "gui" / "SYS_existing.svg")
    claimed, source_paths = gui_mode.claim_svg_inputs(repo_root, work_dir, inbox, "SYS")
    assert claimed == [existing]
    assert source_paths == []

    destination_work = repo_root / "work" / "SYS-501"
    (destination_work / "input" / "gui").mkdir(parents=True)
    write_svg(inbox / "SYS_conflict.svg")
    write_svg(destination_work / "input" / "gui" / "SYS_conflict.svg")
    monkeypatch.setattr(gui_mode, "discover_svg_files", lambda work_dir_arg: [])
    with pytest.raises(FileExistsError, match="Cannot claim SVG"):
        gui_mode.claim_svg_inputs(repo_root, destination_work, inbox, "SYS")

    assert gui_mode.input_prefix_for_mode("generic-gui") == "GUI"
    assert gui_mode.resolve_work_dir(repo_root, "SYS-1", None) == repo_root / "work" / "SYS-1"
    assert gui_mode.resolve_work_dir(repo_root, "SYS-1", str(work_dir)) == work_dir.resolve()
    assert gui_mode.resolve_svg_input_dir(repo_root, None) == inbox
    assert gui_mode.resolve_svg_input_dir(repo_root, str(inbox)) == inbox.resolve()

    code = gui_mode.main(["inspect-input", "--repo-root", str(repo_root), "--svg-input-dir", str(inbox)])
    captured = capsys.readouterr()
    assert code == 0
    assert '"allowed_prefixes"' in captured.out


def test_gui_mode_validate_detects_policy_syntax_qtest_and_state_errors(tmp_path: Path) -> None:
    _, work_dir = make_work(tmp_path, "FIX-500")
    output_dir = work_dir / "gac-uac"
    pyqt_path = output_dir / "generated" / "pyqt6" / "main_window.py"
    test_path = output_dir / "generated" / "tests" / "test_gui_smoke.py"
    pyqt_path.parent.mkdir(parents=True)
    test_path.parent.mkdir(parents=True)
    pyqt_path.write_text("def broken(:\n", encoding="utf-8")
    test_path.write_text("def test_missing_helpers():\n    assert True\n", encoding="utf-8")
    (output_dir / "gui-mode-state.json").write_text("{bad json", encoding="utf-8")

    result = gui_mode.validate_outputs(work_dir)

    assert result["status"] == "fail"
    assert any(error.startswith("missing:") for error in result["errors"])
    assert any(error.startswith("syntax:main_window.py") for error in result["errors"])
    assert "qtest:QApplication-missing" in result["errors"]
    assert any(error.startswith("state-json:") for error in result["errors"])

    pyqt_path.write_text("class Window:\n    def setup(self):\n        self.setGeometry(1, 2, 3, 4)\n", encoding="utf-8")
    (output_dir / "gui-mode-state.json").write_text(
        json.dumps({"parent_workflow_return": {"ready": False}}),
        encoding="utf-8",
    )

    result = gui_mode.validate_outputs(work_dir)

    assert "policy:setGeometry" in result["errors"]
    assert "policy:objectName-missing" in result["errors"]
    assert "signal:no-action-signal" in result["warnings"]
    assert "state:parent-workflow-return-not-ready" in result["errors"]


def test_gui_mode_run_generate_complete_force_validation_error_and_self_test(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root, work_dir = make_work(tmp_path, "FEAT-600")
    inbox = repo_root / "work" / "requirements" / "svg-input"
    write_svg(inbox / "FEAT_console.svg")

    state = gui_mode.run_generate(
        argparse.Namespace(
            issue_id="FEAT-600",
            work_dir=str(work_dir),
            repo_root=str(repo_root),
            svg_input_dir=str(inbox),
            mode="auto",
            force=False,
            input_prefix=None,
            skip_context_check=True,
        )
    )

    assert state["status"] == "complete"
    assert state["validation"]["status"] == "pass"
    assert state["parent_workflow_return"]["ready"] is True
    assert (work_dir / "context" / "artifact-index.json").exists()

    write_svg(inbox / "FEAT_new.svg")
    with pytest.raises(FileExistsError, match="GUI mode outputs already exist"):
        gui_mode.run_generate(
            argparse.Namespace(
                issue_id="FEAT-600",
                work_dir=str(work_dir),
                repo_root=str(repo_root),
                svg_input_dir=str(inbox),
                mode="auto",
                force=False,
                input_prefix=None,
                skip_context_check=True,
            )
        )

    failure_work = repo_root / "work" / "FEAT-601"
    (failure_work / "context").mkdir(parents=True)
    write_svg(inbox / "FEAT_failure.svg")
    monkeypatch.setattr(gui_mode, "validate_outputs", lambda work_dir_arg: {"status": "fail", "errors": ["boom"]})
    with pytest.raises(RuntimeError, match="failed validation"):
        gui_mode.run_generate(
            argparse.Namespace(
                issue_id="FEAT-601",
                work_dir=str(failure_work),
                repo_root=str(repo_root),
                svg_input_dir=str(inbox),
                mode="auto",
                force=False,
                input_prefix=None,
                skip_context_check=True,
            )
        )

    monkeypatch.undo()
    assert gui_mode.run_self_test(argparse.Namespace())["checks"] == [
        "skip-without-svg",
        "prefix-isolation",
        "generate-and-validate",
        "existing-output-guard",
    ]
    with pytest.raises(AssertionError, match="fail message"):
        gui_mode.assert_self_test(False, "fail message")
    assert gui_mode.make_self_test_args(repo_root, "SYS-999").skip_context_check is True


def test_gui_mode_main_run_and_self_test_error_boundary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo_root, work_dir = make_work(tmp_path, "GUI-700")
    inbox = repo_root / "work" / "requirements" / "svg-input"
    write_svg(inbox / "GUI_console.svg")

    code = gui_mode.main(
        [
            "run",
            "--issue-id",
            "GUI-700",
            "--work-dir",
            str(work_dir),
            "--repo-root",
            str(repo_root),
            "--svg-input-dir",
            str(inbox),
            "--mode",
            "generic-gui",
            "--input-prefix",
            "GUI",
            "--skip-context-check",
        ]
    )
    captured = capsys.readouterr()
    assert code == 0
    assert '"status": "complete"' in captured.out

    monkeypatch.setattr(gui_mode, "run_self_test", lambda args: {"status": "fail", "checks": []})
    assert gui_mode.main(["self-test"]) == 1
    assert '"status": "fail"' in capsys.readouterr().out

    monkeypatch.setattr(gui_mode, "run_self_test", lambda args: (_ for _ in ()).throw(RuntimeError("boom")))
    assert gui_mode.main(["self-test"]) == 1
    assert "ERROR: boom" in capsys.readouterr().err


def test_gui_mode_run_generate_skips_when_no_svg_and_main_prints_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo_root, work_dir = make_work(tmp_path, "SYS-400")

    skipped = gui_mode.run_generate(
        argparse.Namespace(
            issue_id="SYS-400",
            work_dir=str(work_dir),
            repo_root=str(repo_root),
            svg_input_dir=str(repo_root / "work" / "requirements" / "svg-input"),
            mode="auto",
            force=False,
            input_prefix=None,
            skip_context_check=True,
        )
    )

    code = gui_mode.main(
        [
            "validate",
            "--issue-id",
            "SYS-400",
            "--work-dir",
            str(work_dir),
            "--repo-root",
            str(repo_root),
        ]
    )
    captured = capsys.readouterr()

    assert skipped["status"] == "skipped"
    assert code == 1
    assert '"status": "fail"' in captured.out


def test_web_svg_mode_parse_model_render_and_validate_outputs(tmp_path: Path) -> None:
    repo_root, work_dir = make_work(tmp_path, "WEB_SYS-100")
    svg_input_dir = repo_root / "work" / "requirements" / "svg-input"
    svg_path = write_svg(work_dir / "input" / "web-ui" / "WEB_SYS_dashboard.svg", WEB_SVG_TEXT)

    document = web_svg_layout_mode.parse_svg(svg_path)
    model = web_svg_layout_mode.build_model([document], "WEB_SYS-100", "new-app")
    state = web_svg_layout_mode.write_artifacts(
        repo_root,
        work_dir,
        "WEB_SYS-100",
        "new-app",
        [svg_path],
        ["work/requirements/svg-input/WEB_SYS_dashboard.svg"],
        svg_input_dir,
        "WEB_SYS",
        [document],
        model,
    )
    validation = web_svg_layout_mode.validate_outputs(work_dir)

    assert document.title == "Dashboard"
    assert {component["type"] for component in model["components"]} >= {"button", "input", "select", "checkbox", "metric", "data_region", "text"}
    assert state["parent_workflow_return"]["ready"] is True
    assert validation["status"] == "pass"
    assert (work_dir / "web-ui" / "generated" / "web" / "SvgLayoutCandidate.tsx").exists()


def test_web_svg_mode_helpers_cover_prefix_discovery_claim_and_modes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo_root, work_dir = make_work(tmp_path, "WEB_FEAT-200")
    inbox = repo_root / "work" / "requirements" / "svg-input"
    write_svg(inbox / "NEXT_FEAT_dashboard.svg", WEB_SVG_TEXT)
    write_svg(inbox / "WEB_FEAT_dashboard.svg", WEB_SVG_TEXT)
    write_svg(inbox / "WEB_FIX_other.svg", WEB_SVG_TEXT)

    pending = web_svg_layout_mode.discover_inbox_svg_files(inbox, "WEB_FEAT")
    claimed, sources = web_svg_layout_mode.claim_svg_inputs(work_dir, inbox, "WEB_FEAT", repo_root)

    assert [path.name for path in pending] == ["NEXT_FEAT_dashboard.svg", "WEB_FEAT_dashboard.svg"]
    assert [path.name for path in claimed] == ["NEXT_FEAT_dashboard.svg", "WEB_FEAT_dashboard.svg"]
    assert sources == [
        "work/requirements/svg-input/NEXT_FEAT_dashboard.svg",
        "work/requirements/svg-input/WEB_FEAT_dashboard.svg",
    ]
    assert web_svg_layout_mode.infer_mode("SYS-1", "auto") == "new-app"
    assert web_svg_layout_mode.infer_mode("WEB_SYS-1", "auto") == "generic-web-ui"
    assert web_svg_layout_mode.infer_mode("NEXTFEAT-1", "auto") == "existing-app-feature"
    assert web_svg_layout_mode.infer_mode("FIX-1", "auto") == "corrective-fix"
    assert web_svg_layout_mode.infer_mode("OTHER-1", "auto") == "generic-web-ui"
    assert web_svg_layout_mode.infer_mode("WEB_FIX-1", "corrective-fix") == "corrective-fix"
    assert web_svg_layout_mode.pascal_case("header-toolbar") == "HeaderToolbar"
    assert web_svg_layout_mode.input_prefix_for_mode("generic-web-ui") == "WEB"
    assert web_svg_layout_mode.discover_inbox_svg_files(repo_root / "missing", "WEB") == []

    generic_inbox = repo_root / "generic-inbox"
    generic_inbox.mkdir()
    write_svg(generic_inbox / "NEXT_generic.svg", WEB_SVG_TEXT)
    write_svg(generic_inbox / "WEB_generic.svg", WEB_SVG_TEXT)
    assert [path.name for path in web_svg_layout_mode.discover_inbox_svg_files(generic_inbox, "WEB")] == [
        "NEXT_generic.svg",
        "WEB_generic.svg",
    ]

    existing = write_svg(work_dir / "input" / "web-ui" / "WEB_FEAT_existing.svg", WEB_SVG_TEXT)
    claimed_existing, existing_sources = web_svg_layout_mode.claim_svg_inputs(work_dir, inbox, "WEB_FEAT", repo_root)
    assert existing in claimed_existing
    assert existing_sources == []

    conflict_work = repo_root / "work" / "WEB_FEAT-201"
    (conflict_work / "input" / "web-ui").mkdir(parents=True)
    write_svg(inbox / "WEB_FEAT_conflict.svg", WEB_SVG_TEXT)
    write_svg(conflict_work / "input" / "web-ui" / "WEB_FEAT_conflict.svg", WEB_SVG_TEXT)
    monkeypatch.setattr(web_svg_layout_mode, "discover_svg_files", lambda work_dir_arg: [])
    with pytest.raises(FileExistsError, match="Cannot claim SVG"):
        web_svg_layout_mode.claim_svg_inputs(conflict_work, inbox, "WEB_FEAT", repo_root)


def test_web_svg_mode_renderers_and_failure_paths(tmp_path: Path) -> None:
    _, work_dir = make_work(tmp_path, "WEB_FIX-300")
    svg_path = write_svg(work_dir / "input" / "web-ui" / "WEB_FIX_dashboard.svg", WEB_SVG_TEXT)
    document = web_svg_layout_mode.parse_svg(svg_path)
    model = web_svg_layout_mode.build_model([document], "WEB_FIX-300", "corrective-fix")

    assert web_svg_layout_mode.parse_style("fill: red; ignored; stroke: blue") == {"fill": "red", "stroke": "blue"}
    assert web_svg_layout_mode.safe_identifier("123 bad id", "fallback") == "item_123_bad_id"
    assert web_svg_layout_mode.html_element("unknown") == "div"
    assert web_svg_layout_mode.html_element("checkbox") == "input"
    assert web_svg_layout_mode.infer_section_role("nav_sidebar") == "navigation"
    assert web_svg_layout_mode.infer_section_role("footer_status") == "status"
    assert "移動" in web_svg_layout_mode.infer_responsibility("navigation", "Menu")
    assert "# Web SVG Analysis" in web_svg_layout_mode.render_svg_analysis([document], "WEB_FIX-300", "corrective-fix")
    assert "screen:" in web_svg_layout_mode.render_yaml(model)
    assert "# Component Mapping" in web_svg_layout_mode.render_component_mapping(model, "WEB_FIX-300", "corrective-fix")
    assert "# Responsive Layout Spec" in web_svg_layout_mode.render_responsive_spec(model, "WEB_FIX-300", "corrective-fix")
    assert "React Generation Plan" in web_svg_layout_mode.render_generation_plan("WEB_FIX-300", "corrective-fix", "react")
    assert "Playwright Generation Plan" in web_svg_layout_mode.render_generation_plan("WEB_FIX-300", "corrective-fix", "playwright")
    assert "export function SvgLayoutCandidate" in web_svg_layout_mode.render_tsx(model)
    assert "@playwright/test" in web_svg_layout_mode.render_playwright(model)
    assert "human-review-required" in web_svg_layout_mode.render_review("WEB_FIX-300", "corrective-fix", [svg_path])
    assert "SVG Input Inbox" in web_svg_layout_mode.input_readme()

    with pytest.raises(ValueError, match="Invalid SVG XML"):
        web_svg_layout_mode.parse_svg(write_svg(tmp_path / "bad-web.svg", "<svg><g></svg>"))


def test_web_svg_mode_model_fallbacks_duplicate_ids_and_component_edges(tmp_path: Path) -> None:
    _, work_dir = make_work(tmp_path, "WEB_MISC-301")
    decorative_svg = write_svg(
        work_dir / "input" / "web-ui" / "WEB_decorative.svg",
        """\
<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
  <g id="content"><path id="shape" d="M0,0 L10,10"/></g>
</svg>
""",
    )
    rich_svg = write_svg(
        work_dir / "input" / "web-ui" / "WEB_rich.svg",
        """\
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <g id="nav_sidebar">
    <rect id="nav_menu" class="menu" width="100" height="30"/>
    <rect id="panel_card" class="panel" width="100" height="30"/>
    <text id="same">Apply</text>
    <text id="same">Plain Label</text>
  </g>
</svg>
""",
    )

    fallback_model = web_svg_layout_mode.build_model(
        [web_svg_layout_mode.parse_svg(decorative_svg)],
        "WEB_MISC-301",
        "generic-web-ui",
    )
    rich_model = web_svg_layout_mode.build_model(
        [web_svg_layout_mode.parse_svg(rich_svg)],
        "WEB_MISC-301",
        "generic-web-ui",
    )

    assert fallback_model["components"] == [
        {
            "id": "content_region",
            "type": "section",
            "label": "Content",
            "section": "content",
            "responsibility": "画面の主要内容を表示する",
            "source": "WEB_decorative.svg",
        }
    ]
    assert {component["type"] for component in rich_model["components"]} >= {"navigation", "section", "button", "text"}
    assert [component["id"] for component in rich_model["components"] if component["id"].startswith("same")] == [
        "same",
        "same_2",
    ]
    button = next(component for component in rich_model["components"] if component["id"] == "same")
    assert button["type"] == "button"
    assert button["label"] == "Apply"


def test_web_svg_validate_detects_policy_react_playwright_and_state_errors(tmp_path: Path) -> None:
    _, work_dir = make_work(tmp_path, "WEB_FIX-350")
    output_dir = work_dir / "web-ui"
    component_path = output_dir / "generated" / "web" / "SvgLayoutCandidate.tsx"
    test_path = output_dir / "generated" / "tests" / "svg-layout.spec.ts"
    component_path.parent.mkdir(parents=True)
    test_path.parent.mkdir(parents=True)
    component_path.write_text(
        "export function Broken(){ return <div dangerouslySetInnerHTML={{__html: ''}} /> }",
        encoding="utf-8",
    )
    test_path.write_text("test('x', async()=>{})", encoding="utf-8")
    (output_dir / "web-svg-layout-state.json").write_text("{bad json", encoding="utf-8")

    result = web_svg_layout_mode.validate_outputs(work_dir)

    assert result["status"] == "fail"
    assert any(error.startswith("missing:") for error in result["errors"])
    assert "policy:dangerouslySetInnerHTML" in result["errors"]
    assert "react:data-testid-missing" in result["errors"]
    assert "react:SvgLayoutCandidate-missing" in result["errors"]
    assert "react:onAction-missing" in result["errors"]
    assert "playwright:@playwright/test-missing" in result["errors"]
    assert "playwright:getByTestId-missing" in result["errors"]
    assert "playwright:toBeVisible-missing" in result["errors"]
    assert any(error.startswith("state-json:") for error in result["errors"])

    component_path.write_text(
        "export function SvgLayoutCandidate(){ return <div data-testid='x' style={{position: \"absolute\"}}>x</div> }",
        encoding="utf-8",
    )
    (output_dir / "web-svg-layout-state.json").write_text(
        json.dumps({"parent_workflow_return": {"ready": False}}),
        encoding="utf-8",
    )
    result = web_svg_layout_mode.validate_outputs(work_dir)
    assert 'policy:position: "absolute"' in result["errors"]
    assert "state:parent-workflow-return-not-ready" in result["errors"]


def test_web_svg_init_input_and_resolvers(tmp_path: Path) -> None:
    repo_root, work_dir = make_work(tmp_path, "WEB_SYS-360")
    inbox = repo_root / "work" / "requirements" / "svg-input"

    result = web_svg_layout_mode.run_init_input(
        argparse.Namespace(repo_root=str(repo_root), svg_input_dir=None, force=False)
    )
    readme = repo_root / result["readme"]
    readme.write_text("custom\n", encoding="utf-8")
    web_svg_layout_mode.run_init_input(argparse.Namespace(repo_root=str(repo_root), svg_input_dir=None, force=False))
    assert readme.read_text(encoding="utf-8") == "custom\n"
    web_svg_layout_mode.run_init_input(argparse.Namespace(repo_root=str(repo_root), svg_input_dir=None, force=True))
    assert "SVG Input Inbox" in readme.read_text(encoding="utf-8-sig")
    assert web_svg_layout_mode.resolve_work_dir(repo_root, "WEB_SYS-360", None) == work_dir
    assert web_svg_layout_mode.resolve_work_dir(repo_root, "WEB_SYS-360", str(work_dir)) == work_dir.resolve()
    assert web_svg_layout_mode.resolve_svg_input_dir(repo_root, None) == inbox
    assert web_svg_layout_mode.resolve_svg_input_dir(repo_root, str(inbox)) == inbox.resolve()


def test_web_svg_run_generate_complete_force_and_validation_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root, work_dir = make_work(tmp_path, "WEB_FEAT-600")
    inbox = repo_root / "work" / "requirements" / "svg-input"
    write_svg(inbox / "WEB_FEAT_dashboard.svg", WEB_SVG_TEXT)

    state = web_svg_layout_mode.run_generate(
        argparse.Namespace(
            issue_id="WEB_FEAT-600",
            work_dir=str(work_dir),
            repo_root=str(repo_root),
            svg_input_dir=str(inbox),
            mode="auto",
            force=False,
            input_prefix=None,
            skip_context_check=True,
        )
    )

    assert state["status"] == "complete"
    assert state["validation"]["status"] == "pass"
    assert state["parent_workflow_return"]["ready"] is True
    assert (work_dir / "context" / "artifact-index.json").exists()
    assert (work_dir / "context" / "context-manifest.json").exists()

    write_svg(inbox / "WEB_FEAT_new.svg", WEB_SVG_TEXT)
    with pytest.raises(FileExistsError, match="Web SVG layout outputs already exist"):
        web_svg_layout_mode.run_generate(
            argparse.Namespace(
                issue_id="WEB_FEAT-600",
                work_dir=str(work_dir),
                repo_root=str(repo_root),
                svg_input_dir=str(inbox),
                mode="auto",
                force=False,
                input_prefix=None,
                skip_context_check=True,
            )
        )

    forced = web_svg_layout_mode.run_generate(
        argparse.Namespace(
            issue_id="WEB_FEAT-600",
            work_dir=str(work_dir),
            repo_root=str(repo_root),
            svg_input_dir=str(inbox),
            mode="auto",
            force=True,
            input_prefix=None,
            skip_context_check=True,
        )
    )
    assert forced["status"] == "complete"

    failure_work = repo_root / "work" / "WEB_FEAT-601"
    (failure_work / "context").mkdir(parents=True)
    write_svg(inbox / "WEB_FEAT_failure.svg", WEB_SVG_TEXT)
    monkeypatch.setattr(web_svg_layout_mode, "validate_outputs", lambda work_dir_arg: {"status": "fail", "errors": ["boom"]})
    with pytest.raises(RuntimeError, match="failed validation"):
        web_svg_layout_mode.run_generate(
            argparse.Namespace(
                issue_id="WEB_FEAT-601",
                work_dir=str(failure_work),
                repo_root=str(repo_root),
                svg_input_dir=str(inbox),
                mode="auto",
                force=False,
                input_prefix=None,
                skip_context_check=True,
            )
        )


def test_web_svg_main_run_and_error_boundary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo_root, work_dir = make_work(tmp_path, "WEB-700")
    inbox = repo_root / "work" / "requirements" / "svg-input"
    write_svg(inbox / "WEB_console.svg", WEB_SVG_TEXT)

    code = web_svg_layout_mode.main(
        [
            "run",
            "--issue-id",
            "WEB-700",
            "--work-dir",
            str(work_dir),
            "--repo-root",
            str(repo_root),
            "--svg-input-dir",
            str(inbox),
            "--mode",
            "generic-web-ui",
            "--input-prefix",
            "WEB",
            "--skip-context-check",
        ]
    )
    captured = capsys.readouterr()
    assert code == 0
    assert '"status": "complete"' in captured.out

    monkeypatch.setattr(web_svg_layout_mode, "run_validate", lambda args: {"status": "fail"})
    assert web_svg_layout_mode.main(["validate", "--issue-id", "WEB-700", "--repo-root", str(repo_root)]) == 1
    assert '"status": "fail"' in capsys.readouterr().out

    monkeypatch.setattr(web_svg_layout_mode, "run_validate", lambda args: (_ for _ in ()).throw(RuntimeError("boom")))
    assert web_svg_layout_mode.main(["validate", "--issue-id", "WEB-700", "--repo-root", str(repo_root)]) == 1
    assert "ERROR: boom" in capsys.readouterr().err


def test_web_svg_run_generate_skips_when_no_svg_and_main_prints_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo_root, work_dir = make_work(tmp_path, "WEB_SYS-400")

    skipped = web_svg_layout_mode.run_generate(
        argparse.Namespace(
            issue_id="WEB_SYS-400",
            work_dir=str(work_dir),
            repo_root=str(repo_root),
            svg_input_dir=str(repo_root / "work" / "requirements" / "svg-input"),
            mode="auto",
            force=False,
            input_prefix=None,
            skip_context_check=True,
        )
    )

    code = web_svg_layout_mode.main(
        [
            "validate",
            "--issue-id",
            "WEB_SYS-400",
            "--work-dir",
            str(work_dir),
            "--repo-root",
            str(repo_root),
        ]
    )
    captured = capsys.readouterr()

    assert skipped["status"] == "skipped"
    assert code == 1
    assert '"status": "fail"' in captured.out
