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


def test_web_svg_mode_helpers_cover_prefix_discovery_claim_and_modes(tmp_path: Path) -> None:
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
    assert web_svg_layout_mode.pascal_case("header-toolbar") == "HeaderToolbar"


def test_web_svg_mode_renderers_and_failure_paths(tmp_path: Path) -> None:
    _, work_dir = make_work(tmp_path, "WEB_FIX-300")
    svg_path = write_svg(work_dir / "input" / "web-ui" / "WEB_FIX_dashboard.svg", WEB_SVG_TEXT)
    document = web_svg_layout_mode.parse_svg(svg_path)
    model = web_svg_layout_mode.build_model([document], "WEB_FIX-300", "corrective-fix")

    assert web_svg_layout_mode.parse_style("fill: red; ignored; stroke: blue") == {"fill": "red", "stroke": "blue"}
    assert web_svg_layout_mode.safe_identifier("123 bad id", "fallback") == "item_123_bad_id"
    assert web_svg_layout_mode.html_element("unknown") == "div"
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
