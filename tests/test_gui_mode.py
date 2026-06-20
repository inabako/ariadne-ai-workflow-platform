from __future__ import annotations

import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from runtime.intake.intake_requirements import id_prefix_for_workflow
from runtime.workflow.gui_mode import run_generate, validate_outputs


SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="480" viewBox="0 0 800 480">
  <title>Robot Console</title>
  <g id="header">
    <text id="status_label" x="20" y="30">READY</text>
    <rect id="connect_button" x="650" y="10" width="120" height="40" fill="#336699"/>
    <text id="connect_button_text" x="680" y="35">Connect</text>
  </g>
  <g id="video_panel">
    <rect id="video_display" x="20" y="70" width="500" height="360" fill="#111111"/>
  </g>
  <g id="control_panel">
    <text id="speed_label" x="560" y="100">Speed</text>
  </g>
</svg>
"""


class GuiModeRuntimeTest(unittest.TestCase):
    def make_args(self, repo_root: Path, issue_id: str, mode: str = "auto") -> Namespace:
        return Namespace(
            repo_root=str(repo_root),
            work_dir=None,
            issue_id=issue_id,
            mode=mode,
            force=False,
            svg_input_dir=None,
            input_prefix=None,
        )

    def test_run_skips_when_svg_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            repo_root = Path(raw_root)
            (repo_root / "work" / "SYS-0001").mkdir(parents=True)
            result = run_generate(self.make_args(repo_root, "SYS-0001"))
            self.assertEqual(result["status"], "skipped")
            self.assertTrue(result["return_to_parent_workflow"])
            self.assertTrue(
                (repo_root / "work" / "SYS-0001" / "context" / "gui-mode-state.json").exists()
            )

    def test_run_ignores_other_flow_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            repo_root = Path(raw_root)
            svg_input = repo_root / "work" / "requirements" / "svg-input"
            svg_input.mkdir(parents=True)
            feature_svg = svg_input / "FEAT_other-flow.svg"
            feature_svg.write_text(SVG, encoding="utf-8")

            result = run_generate(self.make_args(repo_root, "SYS-0001"))

            self.assertEqual(result["status"], "skipped")
            self.assertTrue(feature_svg.exists())

    def test_parent_workflows_use_gui_issue_prefixes(self) -> None:
        self.assertEqual(id_prefix_for_workflow("new-robotics-system-development"), "SYS")
        self.assertEqual(id_prefix_for_workflow("robotics-new-system-iac"), "SYS")
        self.assertEqual(id_prefix_for_workflow("robotics-maintenance-development"), "FEAT")

    def test_run_generates_and_validates_gui_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            repo_root = Path(raw_root)
            gui_input = repo_root / "work" / "requirements" / "svg-input"
            gui_input.mkdir(parents=True)
            source_svg = gui_input / "FEAT_robot-console.svg"
            source_svg.write_text(SVG, encoding="utf-8")

            result = run_generate(self.make_args(repo_root, "FEAT-0001"))

            self.assertEqual(result["status"], "complete")
            self.assertEqual(result["mode"], "feature-development")
            self.assertEqual(result["input_prefix"], "FEAT")
            self.assertFalse(source_svg.exists())
            output_dir = repo_root / "work" / "FEAT-0001" / "gac-uac"
            self.assertTrue(
                (
                    repo_root
                    / "work"
                    / "FEAT-0001"
                    / "input"
                    / "gui"
                    / "FEAT_robot-console.svg"
                ).exists()
            )
            self.assertTrue((output_dir / "layout-spec.md").exists())
            self.assertTrue(
                (output_dir / "generated" / "pyqt6" / "widgets" / "__init__.py").exists()
            )
            generated = (output_dir / "generated" / "pyqt6" / "main_window.py").read_text(
                encoding="utf-8"
            )
            self.assertRegex(generated, r"setObjectName\(['\"]connect_button['\"]\)")
            self.assertNotIn("connect_button_text =", generated)
            self.assertNotIn("setGeometry(", generated)
            self.assertEqual(validate_outputs(repo_root / "work" / "FEAT-0001")["status"], "pass")
            later_svg = gui_input / "FEAT_later-screen.svg"
            later_svg.write_text(SVG, encoding="utf-8")
            with self.assertRaises(FileExistsError):
                run_generate(self.make_args(repo_root, "FEAT-0001"))
            self.assertTrue(later_svg.exists())


if __name__ == "__main__":
    unittest.main()
