from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    find_repo_root,
    load_artifact_index,
    relative_to_repo,
    upsert_artifact,
    utc_now_iso,
    write_json,
    write_markdown_bom,
)
from runtime.constants.schemas import GUI_MODE_STATE_SCHEMA  # noqa: E402
from runtime.constants.workspace import (  # noqa: E402
    context_file,
    resolve_work_dir as workspace_resolve_work_dir,
    svg_input_dir,
    work_dir_for_id,
)
from runtime.workflow.context_first import register_context, require_environment_selection  # noqa: E402


MODE_BY_PREFIX = {
    "SYS": "system-development",
    "FEAT": "feature-development",
    "FIX": "corrective-improvement",
}
SVG_INBOX_PREFIXES = {
    "SYS": "ariadne-new-system / GaC-UaC GUI",
    "FEAT": "ariadne-feature-maintenance / GaC-UaC GUI",
    "FIX": "corrective-action-fix / GaC-UaC GUI",
    "WEB_SYS": "ariadne-new-system / Web SVG Layout",
    "WEB_FEAT": "ariadne-feature-maintenance / Web SVG Layout",
    "WEB_FIX": "corrective-action-fix / Web SVG Layout",
}
INPUT_PREFIX_BY_MODE = {
    "system-development": "SYS",
    "feature-development": "FEAT",
    "corrective-improvement": "FIX",
    "generic-gui": "GUI",
}
MODE_FOCUS = {
    "system-development": "初期アーキテクチャ、責務分離、拡張性、将来の画面追加余地",
    "feature-development": "既存GUIとの整合、差分実装、結合点、既存テスト破壊防止",
    "corrective-improvement": "最小変更、既存挙動維持、固定座標排除、回帰防止",
    "generic-gui": "論理レイアウト、責務分離、外部I/O分離、QTest容易性",
}
REQUIRED_OUTPUTS = [
    "svg-analysis.md",
    "semantic-layout-graph.yaml",
    "widget-mapping.md",
    "layout-spec.md",
    "pyqt6-generation-plan.md",
    "qtest-generation-plan.md",
    "generated/pyqt6/main_window.py",
    "generated/pyqt6/widgets/__init__.py",
    "generated/tests/test_gui_smoke.py",
    "review/gac-uac-review.md",
    "gui-mode-state.json",
]
SHAPE_TAGS = {"rect", "text", "line", "circle", "ellipse", "path", "polygon", "polyline"}
BUTTON_WORDS = {
    "connect",
    "disconnect",
    "start",
    "stop",
    "save",
    "cancel",
    "apply",
    "open",
    "close",
    "send",
    "reset",
    "接続",
    "切断",
    "開始",
    "停止",
    "保存",
    "取消",
    "適用",
    "送信",
    "リセット",
}


@dataclass
class SvgElement:
    source: str
    tag: str
    element_id: str
    class_name: str
    text: str
    parent_group: str
    attributes: dict[str, str] = field(default_factory=dict)
    style: dict[str, str] = field(default_factory=dict)


@dataclass
class SvgDocument:
    path: Path
    width: str
    height: str
    view_box: str
    title: str
    groups: list[str]
    elements: list[SvgElement]


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_style(raw: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in raw.split(";"):
        if ":" not in item:
            continue
        key, value = item.split(":", 1)
        if key.strip():
            result[key.strip()] = value.strip()
    return result


def safe_identifier(value: str, fallback: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z_]+", "_", value.strip()).strip("_").lower()
    if not normalized:
        normalized = fallback
    if normalized[0].isdigit():
        normalized = f"item_{normalized}"
    return normalized


def parse_svg(path: Path) -> SvgDocument:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"Invalid SVG XML: {path}: {exc}") from exc

    groups: list[str] = []
    elements: list[SvgElement] = []
    counters: dict[str, int] = {}
    title = ""

    def walk(node: ET.Element, group_stack: list[str]) -> None:
        nonlocal title
        tag = local_name(node.tag)
        if tag == "title" and not title:
            title = clean_text("".join(node.itertext()))

        next_stack = group_stack
        if tag == "g":
            group_id = safe_identifier(
                node.attrib.get("id", ""),
                f"group_{len(groups) + 1}",
            )
            groups.append(group_id)
            next_stack = [*group_stack, group_id]

        if tag in SHAPE_TAGS:
            counters[tag] = counters.get(tag, 0) + 1
            element_id = safe_identifier(
                node.attrib.get("id", ""),
                f"{tag}_{counters[tag]}",
            )
            attributes = {
                key: value
                for key, value in node.attrib.items()
                if key
                in {
                    "x",
                    "y",
                    "width",
                    "height",
                    "x1",
                    "y1",
                    "x2",
                    "y2",
                    "cx",
                    "cy",
                    "r",
                    "rx",
                    "ry",
                    "d",
                    "points",
                    "fill",
                    "stroke",
                }
            }
            elements.append(
                SvgElement(
                    source=path.name,
                    tag=tag,
                    element_id=element_id,
                    class_name=node.attrib.get("class", ""),
                    text=clean_text("".join(node.itertext())) if tag == "text" else "",
                    parent_group=next_stack[-1] if next_stack else "content",
                    attributes=attributes,
                    style=parse_style(node.attrib.get("style", "")),
                )
            )

        for child in node:
            walk(child, next_stack)

    walk(root, [])
    return SvgDocument(
        path=path,
        width=root.attrib.get("width", ""),
        height=root.attrib.get("height", ""),
        view_box=root.attrib.get("viewBox", ""),
        title=title,
        groups=list(dict.fromkeys(groups)),
        elements=elements,
    )


def infer_mode(issue_id: str, requested_mode: str) -> str:
    if requested_mode != "auto":
        return requested_mode
    prefix = issue_id.split("-", 1)[0].upper()
    return MODE_BY_PREFIX.get(prefix, "generic-gui")


def infer_widget_type(element: SvgElement) -> str:
    haystack = " ".join(
        [element.element_id, element.class_name, element.text]
    ).lower()
    if any(word in haystack for word in ("button", "btn")):
        return "button"
    if clean_text(element.text).lower() in BUTTON_WORDS:
        return "button"
    if any(word in haystack for word in ("input", "lineedit", "textbox", "search")):
        return "line_edit"
    if any(word in haystack for word in ("combo", "select", "dropdown")):
        return "combo_box"
    if any(word in haystack for word in ("check", "toggle")):
        return "check_box"
    if "slider" in haystack:
        return "slider"
    if any(word in haystack for word in ("video", "canvas", "display", "viewport")):
        return "display"
    if element.tag == "text":
        return "label"
    return "decorative"


def build_model(documents: list[SvgDocument], issue_id: str, mode: str) -> dict[str, Any]:
    all_groups = [group for document in documents for group in document.groups]
    area_ids = list(dict.fromkeys(all_groups)) or ["content"]
    widgets: list[dict[str, str]] = []
    used_ids: set[str] = set()

    for document in documents:
        for element in document.elements:
            widget_type = infer_widget_type(element)
            if widget_type == "decorative":
                continue
            if widget_type == "button" and element.tag == "text":
                existing_button = next(
                    (
                        widget
                        for widget in reversed(widgets)
                        if widget["type"] == "button"
                        and widget["parent"] == element.parent_group
                        and widget["source"] == element.source
                    ),
                    None,
                )
                if existing_button is not None:
                    existing_button["label"] = element.text or existing_button["label"]
                    existing_button["responsibility"] = infer_responsibility(
                        "button",
                        existing_button["label"],
                    )
                    continue
            base_id = safe_identifier(element.element_id, f"widget_{len(widgets) + 1}")
            widget_id = base_id
            suffix = 2
            while widget_id in used_ids:
                widget_id = f"{base_id}_{suffix}"
                suffix += 1
            used_ids.add(widget_id)
            widgets.append(
                {
                    "id": widget_id,
                    "type": widget_type,
                    "label": element.text or widget_id.replace("_", " ").title(),
                    "parent": element.parent_group if element.parent_group in area_ids else area_ids[0],
                    "responsibility": infer_responsibility(widget_type, element.text or widget_id),
                    "source": element.source,
                }
            )

    if not widgets:
        widgets = [
            {
                "id": "content_label",
                "type": "label",
                "label": "GUI content",
                "parent": area_ids[0],
                "responsibility": "画面内容を表示する",
                "source": documents[0].path.name,
            }
        ]

    relationships = [
        {
            "from": widget["id"],
            "to": "injected_controller",
            "event": "clicked",
        }
        for widget in widgets
        if widget["type"] == "button"
    ]
    title = next(
        (
            document.title
            for document in documents
            if document.title
        ),
        f"{issue_id} GUI",
    )
    return {
        "screen": {
            "id": "main_window",
            "title": title,
            "purpose": f"{issue_id} のSVG画面意図を論理レイアウトへ変換したPyQt6候補",
        },
        "areas": [
            {
                "id": area_id,
                "role": infer_area_role(area_id),
                "description": f"{area_id} に属するGUI要素を配置する領域",
            }
            for area_id in area_ids
        ],
        "widgets": widgets,
        "relationships": relationships,
        "layout_hints": [
            "固定座標ではなくQVBoxLayout/QHBoxLayout/QGridLayoutを使用する",
            "resize可能な構成にする",
            "外部I/Oはcontroller注入境界の外側に置く",
            f"mode={mode}: {MODE_FOCUS[mode]}",
        ],
        "test_targets": [
            {
                "widget_id": widget["id"],
                "checks": ["findChild", "objectName", "initial_state"]
                + (["clicked_signal"] if widget["type"] == "button" else []),
            }
            for widget in widgets
        ],
    }


def infer_area_role(area_id: str) -> str:
    lowered = area_id.lower()
    if any(word in lowered for word in ("header", "status", "top")):
        return "status_area"
    if any(word in lowered for word in ("control", "operation", "command")):
        return "operation_area"
    if any(word in lowered for word in ("video", "display", "view", "content")):
        return "display_area"
    if any(word in lowered for word in ("footer", "log", "event")):
        return "information_area"
    return "content_area"


def infer_responsibility(widget_type: str, label: str) -> str:
    if widget_type == "button":
        return f"{label} 操作要求をsignalとして通知する"
    if widget_type == "label":
        return f"{label} に関する状態または説明を表示する"
    if widget_type in {"line_edit", "combo_box", "check_box", "slider"}:
        return f"{label} のユーザー入力を保持する"
    if widget_type == "display":
        return f"{label} の表示領域を提供する"
    return f"{label} を表示する"


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_semantic_yaml(model: dict[str, Any]) -> str:
    screen = model["screen"]
    lines = [
        "screen:",
        f"  id: {yaml_string(screen['id'])}",
        f"  title: {yaml_string(screen['title'])}",
        f"  purpose: {yaml_string(screen['purpose'])}",
        "",
        "areas:",
    ]
    for area in model["areas"]:
        lines.extend(
            [
                f"  - id: {yaml_string(area['id'])}",
                f"    role: {yaml_string(area['role'])}",
                f"    description: {yaml_string(area['description'])}",
            ]
        )
    lines.extend(["", "widgets:"])
    for widget in model["widgets"]:
        lines.extend(
            [
                f"  - id: {yaml_string(widget['id'])}",
                f"    type: {yaml_string(widget['type'])}",
                f"    label: {yaml_string(widget['label'])}",
                f"    parent: {yaml_string(widget['parent'])}",
                f"    responsibility: {yaml_string(widget['responsibility'])}",
                f"    source: {yaml_string(widget['source'])}",
            ]
        )
    lines.extend(["", "relationships:"])
    if model["relationships"]:
        for relationship in model["relationships"]:
            lines.extend(
                [
                    f"  - from: {yaml_string(relationship['from'])}",
                    f"    to: {yaml_string(relationship['to'])}",
                    f"    event: {yaml_string(relationship['event'])}",
                ]
            )
    else:
        lines.append("  []")
    lines.extend(["", "layout_hints:"])
    lines.extend(f"  - {yaml_string(item)}" for item in model["layout_hints"])
    lines.extend(["", "test_targets:"])
    for target in model["test_targets"]:
        lines.append(f"  - widget_id: {yaml_string(target['widget_id'])}")
        lines.append("    checks:")
        lines.extend(f"      - {yaml_string(check)}" for check in target["checks"])
    return "\n".join(lines) + "\n"


def front_matter(issue_id: str, mode: str, phase: str, status: str = "draft") -> str:
    return (
        "---\n"
        "language: ja-JP\n"
        f"issue_id: {issue_id}\n"
        "workflow: gac-uac-gui-mode\n"
        f"mode: {mode}\n"
        f"phase: {phase}\n"
        f"status: {status}\n"
        "---\n\n"
    )


def render_svg_analysis(
    documents: list[SvgDocument],
    issue_id: str,
    mode: str,
) -> str:
    lines = [
        front_matter(issue_id, mode, "svg-analysis"),
        "# SVG Analysis",
        "",
        "## 画面概要",
        "",
        f"- 対象Issue: `{issue_id}`",
        f"- GUIモード: `{mode}`",
        f"- 変換方針: {MODE_FOCUS[mode]}",
        "- SVG座標の完全再現ではなく、論理レイアウトとWidget責務への変換を優先する。",
        "",
        "## SVGファイル",
        "",
        "| File | Width | Height | viewBox | Groups | Elements |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for document in documents:
        lines.append(
            f"| `{document.path.name}` | {document.width or '-'} | "
            f"{document.height or '-'} | `{document.view_box or '-'}` | "
            f"{len(document.groups)} | {len(document.elements)} |"
        )

    lines.extend(
        [
            "",
            "## 領域一覧",
            "",
            "| SVG | Group | 推定責務 |",
            "| --- | --- | --- |",
        ]
    )
    for document in documents:
        for group in document.groups or ["content"]:
            lines.append(
                f"| `{document.path.name}` | `{group}` | {infer_area_role(group)} |"
            )

    lines.extend(
        [
            "",
            "## SVG要素一覧",
            "",
            "| SVG | Tag | ID | Class | Text | Parent | Coordinates / Style | 推定GUI要素 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for document in documents:
        for element in document.elements:
            details = {**element.attributes, **element.style}
            compact = ", ".join(f"{key}={value}" for key, value in details.items())
            lines.append(
                f"| `{element.source}` | `{element.tag}` | `{element.element_id}` | "
                f"`{element.class_name or '-'}` | {element.text or '-'} | "
                f"`{element.parent_group}` | {compact or '-'} | "
                f"`{infer_widget_type(element)}` |"
            )

    lines.extend(
        [
            "",
            "## GUI要素・責務推定",
            "",
            "- `text` と命名規則からlabel、button、入力部品、display領域を推定する。",
            "- groupは画面領域候補として扱い、最終的なWidget責務はLayout Specで確定する。",
            "- line/path/circle等の装飾要素は、そのままWidget化せず意味がある場合だけ統合する。",
            "",
            "## 不明点",
            "",
            "- SVGだけではsignalの業務意味、controller API、状態遷移、validation条件は確定できない。",
            "- 色や図形が状態表現か装飾かは、親ワークフローの要件・既存実装と照合する。",
            "",
            "## PyQt化時の注意点",
            "",
            "- `setGeometry`による座標転写を避ける。",
            "- 外部I/OをMainWindow生成処理へ直結しない。",
            "- 全テスト対象Widgetへ`objectName`を設定する。",
            "- generated配下は候補であり、既存sourceへ無条件上書きしない。",
        ]
    )
    return "\n".join(lines)


def qt_widget_name(widget_type: str) -> str:
    return {
        "button": "QPushButton",
        "label": "QLabel",
        "line_edit": "QLineEdit",
        "combo_box": "QComboBox",
        "check_box": "QCheckBox",
        "slider": "QSlider",
        "display": "QFrame",
    }.get(widget_type, "QWidget")


def render_widget_mapping(model: dict[str, Any], issue_id: str, mode: str) -> str:
    lines = [
        front_matter(issue_id, mode, "widget-mapping"),
        "# Widget Mapping",
        "",
        "| SLG ID | Role / Type | PyQt6 Widget | Class Candidate | Parent | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
        "| `main_window` | root | `QMainWindow` | `MainWindow` | - | controller注入境界 |",
    ]
    for area in model["areas"]:
        class_name = "".join(part.title() for part in area["id"].split("_"))
        lines.append(
            f"| `{area['id']}` | `{area['role']}` | `QGroupBox/QWidget` | "
            f"`{class_name}Panel` | `main_window` | 論理領域 |"
        )
    for widget in model["widgets"]:
        lines.append(
            f"| `{widget['id']}` | `{widget['type']}` | `{qt_widget_name(widget['type'])}` | "
            f"- | `{widget['parent']}` | {widget['responsibility']} |"
        )
    lines.extend(
        [
            "",
            "## 推奨クラス分割",
            "",
            "- `MainWindow`: 画面領域の組み立てとUI signalの公開。",
            "- 領域別Panel: 複数Widgetまたは独立責務を持つ領域だけ分割する。",
            "- Controller: 外部I/Oと業務処理を保持し、MainWindowへ注入する。",
            "",
            "## Signal / Slot候補",
            "",
        ]
    )
    if model["relationships"]:
        for relationship in model["relationships"]:
            lines.append(
                f"- `{relationship['from']}.{relationship['event']}` "
                f"-> `{relationship['to']}`。GUI側は操作要求signalだけを公開する。"
            )
    else:
        lines.append("- SVGから明示的な操作Widgetを推定できないため、親ワークフローで確定する。")
    lines.extend(
        [
            "",
            "## 状態管理候補",
            "",
            "- 表示状態はUIモデルまたはcontrollerから受け取り、外部I/O状態をWidget自身に持たせない。",
            "- enabled/disabled、status text、validation errorを明示的な更新methodに分ける。",
            "",
            "## 既存GUI統合時の注意点",
            "",
            f"- `{mode}` 方針として、{MODE_FOCUS[mode]}を優先する。",
            "- 既存のsignal/slot命名、Widget factory、style、test fixtureを先に確認する。",
            "- generatedコードを丸ごとコピーせず、差分単位で採用する。",
            "",
            "## QTest対象Widget一覧",
            "",
        ]
    )
    lines.extend(
        f"- `{widget['id']}`: findChild / objectName / initial state"
        + (" / clicked signal" if widget["type"] == "button" else "")
        for widget in model["widgets"]
    )
    return "\n".join(lines)


def render_layout_spec(model: dict[str, Any], issue_id: str, mode: str) -> str:
    lines = [
        front_matter(issue_id, mode, "layout-spec"),
        "# Layout Spec",
        "",
        "## Screen",
        "",
        f"- Name: `{model['screen']['id']}`",
        f"- Title: {model['screen']['title']}",
        f"- Purpose: {model['screen']['purpose']}",
        "- Base Class: `QMainWindow`",
        "- Root Layout: `QVBoxLayout`",
        f"- Mode Policy: {MODE_FOCUS[mode]}",
        "",
        "## Areas",
        "",
        "| Area | Layout | Children | Responsibility |",
        "| --- | --- | --- | --- |",
    ]
    for area in model["areas"]:
        children = ", ".join(
            f"`{widget['id']}`"
            for widget in model["widgets"]
            if widget["parent"] == area["id"]
        ) or "-"
        lines.append(
            f"| `{area['id']}` | `QVBoxLayout` | {children} | {area['description']} |"
        )
    lines.extend(
        [
            "",
            "## Widgets",
            "",
            "| Widget ID | Type | Text | Parent | Behavior | Test Target |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for widget in model["widgets"]:
        behavior = (
            "操作要求signalを発火"
            if widget["type"] == "button"
            else widget["responsibility"]
        )
        lines.append(
            f"| `{widget['id']}` | `{qt_widget_name(widget['type'])}` | "
            f"{widget['label']} | `{widget['parent']}` | {behavior} | Yes |"
        )
    lines.extend(
        [
            "",
            "## Layout Policy",
            "",
            "- 固定座標を避ける。",
            "- resize可能な構成にする。",
            "- 外部I/Oを直接持たせない。",
            "- 表示と制御を分離する。",
            "- QTestで生成・探索可能にする。",
            "- 全対象Widgetに安定した`objectName`を設定する。",
            "",
            "## Integration Notes",
            "",
            "- 既存sourceへ反映する候補: `generated/pyqt6/`を差分資料として確認する。",
            "- 既存testsへ反映する候補: `generated/tests/test_gui_smoke.py`を既存fixtureへ適合させる。",
            "- 影響範囲: MainWindow構成、領域Widget、signal/slot、GUI smoke test。",
            "- generated配下は候補であり、親ワークフローのreviewなしにsourceへ上書きしない。",
        ]
    )
    return "\n".join(lines)


def render_generation_plan(issue_id: str, mode: str, kind: str) -> str:
    if kind == "pyqt6":
        body = [
            "# PyQt6 Generation Plan",
            "",
            "- `QMainWindow` + layout classで画面候補を生成する。",
            "- `setGeometry`を使わず、領域ごとにlayoutへWidgetを追加する。",
            "- controllerはconstructor injectionとし、未指定でも画面生成可能にする。",
            "- button操作は`action_requested(str)` signalへ変換する。",
            "- 全Widgetへ`objectName`を設定する。",
            "- 既存sourceへ直接上書きしない。",
        ]
        phase = "pyqt6-generation"
    else:
        body = [
            "# QTest Generation Plan",
            "",
            "- `QT_QPA_PLATFORM=offscreen`でCI実行可能にする。",
            "- `QApplication`を共有生成し、MainWindowのshow/closeを確認する。",
            "- `findChild`で主要Widgetを探索する。",
            "- buttonがある場合は`QTest.mouseClick`と`QSignalSpy`でsignalを確認する。",
            "- 実network、camera、device controller、外部processを起動しない。",
        ]
        phase = "qtest-generation"
    return front_matter(issue_id, mode, phase) + "\n".join(body)


def python_string(value: str) -> str:
    return repr(value)


def render_pyqt6(model: dict[str, Any]) -> str:
    imports = {
        "QApplication",
        "QCheckBox",
        "QComboBox",
        "QFrame",
        "QGroupBox",
        "QLabel",
        "QLineEdit",
        "QMainWindow",
        "QPushButton",
        "QSlider",
        "QVBoxLayout",
        "QWidget",
    }
    lines = [
        '"""Generated PyQt6 layout candidate. Review before integrating into source."""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "from PyQt6.QtCore import Qt, pyqtSignal",
        f"from PyQt6.QtWidgets import {', '.join(sorted(imports))}",
        "",
        "",
        "class MainWindow(QMainWindow):",
        '    """I/O-free GUI candidate generated from SVG semantics."""',
        "",
        "    action_requested = pyqtSignal(str)",
        "",
        "    def __init__(self, controller: Any | None = None) -> None:",
        "        super().__init__()",
        "        self._controller = controller",
        f"        self.setWindowTitle({python_string(model['screen']['title'])})",
        '        self.setObjectName("main_window")',
        "",
        "        central_widget = QWidget(self)",
        '        central_widget.setObjectName("central_widget")',
        "        root_layout = QVBoxLayout(central_widget)",
        "        self.setCentralWidget(central_widget)",
        "",
    ]
    area_layouts: dict[str, str] = {}
    for area in model["areas"]:
        area_id = area["id"]
        variable = safe_identifier(area_id, "content")
        layout_var = f"{variable}_layout"
        area_layouts[area_id] = layout_var
        lines.extend(
            [
                f"        self.{variable} = QGroupBox({python_string(area_id.replace('_', ' ').title())})",
                f'        self.{variable}.setObjectName({python_string(area_id)})',
                f"        {layout_var} = QVBoxLayout(self.{variable})",
                f"        root_layout.addWidget(self.{variable})",
                "",
            ]
        )
    for widget in model["widgets"]:
        widget_id = widget["id"]
        widget_type = widget["type"]
        widget_class = qt_widget_name(widget_type)
        label = widget["label"]
        layout_var = area_layouts.get(widget["parent"], next(iter(area_layouts.values())))
        if widget_type in {"button", "label", "line_edit", "check_box"}:
            constructor = f"{widget_class}({python_string(label)})"
        elif widget_type == "slider":
            constructor = "QSlider(Qt.Orientation.Horizontal)"
        else:
            constructor = f"{widget_class}()"
        lines.extend(
            [
                f"        self.{widget_id} = {constructor}",
                f"        self.{widget_id}.setObjectName({python_string(widget_id)})",
            ]
        )
        if widget_type == "display":
            lines.append(f"        self.{widget_id}.setFrameShape(QFrame.Shape.StyledPanel)")
        if widget_type == "button":
            lines.append(
                f"        self.{widget_id}.clicked.connect("
                f"lambda checked=False, action={python_string(widget_id)}: self._request_action(action))"
            )
        lines.extend([f"        {layout_var}.addWidget(self.{widget_id})", ""])
    lines.extend(
        [
            "    def _request_action(self, action: str) -> None:",
            "        self.action_requested.emit(action)",
            '        handler = getattr(self._controller, "handle_action", None)',
            "        if callable(handler):",
            "            handler(action)",
            "",
            "",
            "def create_window(controller: Any | None = None) -> MainWindow:",
            "    return MainWindow(controller=controller)",
            "",
        ]
    )
    return "\n".join(lines)


def render_qtest(model: dict[str, Any]) -> str:
    widgets = model["widgets"]
    buttons = [widget for widget in widgets if widget["type"] == "button"]
    lines = [
        '"""Generated QTest smoke candidate. Adapt paths and fixtures before integration."""',
        "",
        "from __future__ import annotations",
        "",
        "import os",
        "import sys",
        "import unittest",
        "from pathlib import Path",
        "",
        'os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")',
        "GENERATED_ROOT = Path(__file__).resolve().parents[1] / \"pyqt6\"",
        "sys.path.insert(0, str(GENERATED_ROOT))",
        "",
        "from PyQt6.QtCore import Qt  # noqa: E402",
        "from PyQt6.QtTest import QSignalSpy, QTest  # noqa: E402",
        "from PyQt6.QtWidgets import QApplication, QWidget  # noqa: E402",
        "from main_window import MainWindow  # noqa: E402",
        "",
        "",
        "class GuiSmokeTest(unittest.TestCase):",
        "    @classmethod",
        "    def setUpClass(cls) -> None:",
        "        cls.app = QApplication.instance() or QApplication([])",
        "",
        "    def setUp(self) -> None:",
        "        self.window = MainWindow()",
        "        self.window.show()",
        "        self.app.processEvents()",
        "",
        "    def tearDown(self) -> None:",
        "        self.window.close()",
        "        self.app.processEvents()",
        "",
        "    def test_main_window_and_widgets_are_created(self) -> None:",
        '        self.assertEqual(self.window.objectName(), "main_window")',
    ]
    for widget in widgets:
        lines.extend(
            [
                f"        widget = self.window.findChild(QWidget, {python_string(widget['id'])})",
                f"        self.assertIsNotNone(widget, {python_string(widget['id'])})",
            ]
        )
    if buttons:
        button = buttons[0]
        lines.extend(
            [
                "",
                "    def test_button_emits_action_signal(self) -> None:",
                "        spy = QSignalSpy(self.window.action_requested)",
                f"        button = self.window.findChild(QWidget, {python_string(button['id'])})",
                "        self.assertIsNotNone(button)",
                "        QTest.mouseClick(button, Qt.MouseButton.LeftButton)",
                "        self.assertEqual(len(spy), 1)",
                f"        self.assertEqual(spy[0][0], {python_string(button['id'])})",
            ]
        )
    lines.extend(["", "", 'if __name__ == "__main__":', "    unittest.main()", ""])
    return "\n".join(lines)


def render_review(issue_id: str, mode: str, svg_files: list[Path]) -> str:
    return front_matter(issue_id, mode, "gui-review", "in-review") + "\n".join(
        [
            "# GaC / UaC Review",
            "",
            "## Review Status",
            "",
            "- Status: `human-review-required`",
            f"- SVG inputs: {', '.join(f'`{path.name}`' for path in svg_files)}",
            f"- Mode: `{mode}`",
            "",
            "## 必須確認",
            "",
            "- [ ] SVGの画面意図が領域・Widget・責務へ正しく変換されている。",
            "- [ ] 固定座標の転写ではなく論理Layoutになっている。",
            "- [ ] 既存sourceとの差分と統合点が確認されている。",
            "- [ ] 外部I/Oが生成GUIへ直結していない。",
            "- [ ] objectNameとQTest候補が要件・Issue scopeに紐づいている。",
            "- [ ] generated配下を無条件上書きせず、採用差分がレビューされている。",
            "",
            "## 親ワークフローへの返却",
            "",
            "レビュー後、`layout-spec.md`、`widget-mapping.md`、`generated/pyqt6/`、"
            "`generated/tests/`を通常の実装・レビュー・試験工程へ渡す。",
        ]
    )


def input_readme() -> str:
    return "\n".join(
        [
            "# GUI SVG Input Inbox",
            "",
            "Issue作成前に、GUIレイアウト意図を表すSVGをこのdirectoryへ配置します。",
            "",
            "```text",
            "work/requirements/svg-input/SYS_<name>.svg",
            "work/requirements/svg-input/FEAT_<name>.svg",
            "work/requirements/svg-input/FIX_<name>.svg",
            "```",
            "",
            "プレフィックス:",
            "",
            "- `SYS_`: 新システム開発",
            "- `FEAT_`: 新機能・保守開発",
            "- `FIX_`: 改修改善",
            "",
            "ルール:",
            "",
            "- SVGは完成画像ではなく、論理Layout、Widget責務、signal、QTest候補を抽出する入力です。",
            "- `id`と`class`には可能な限り意味のある名前を付けます。",
            "- 外部I/Oや業務処理はSVGへ埋め込まず、親ワークフローの要件で定義します。",
            "- Issue作成後、対応プレフィックスのSVGはIssue作業領域の`input/gui/`へ移動されます。",
            "- 同じプレフィックスの複数SVGは、同一Issueの複数画面入力としてまとめて取り込まれます。",
            "- 対応SVGが無い場合、GUIモードは`skipped`となり親ワークフローを継続します。",
        ]
    )


def resolve_work_dir(repo_root: Path, issue_id: str, raw_work_dir: str | None) -> Path:
    return workspace_resolve_work_dir(repo_root, issue_id, raw_work_dir or "")


def resolve_svg_input_dir(repo_root: Path, raw_input_dir: str | None) -> Path:
    return (
        Path(raw_input_dir).resolve()
        if raw_input_dir
        else svg_input_dir(repo_root)
    )


def input_prefix_for_mode(mode: str) -> str:
    return INPUT_PREFIX_BY_MODE[mode]


def discover_inbox_svg_files(svg_input_dir: Path, input_prefix: str) -> list[Path]:
    if not svg_input_dir.exists():
        return []
    prefix = f"{input_prefix.upper()}_"
    return sorted(
        path
        for path in svg_input_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".svg"
        and path.name.upper().startswith(prefix)
    )


def discover_svg_files(work_dir: Path) -> list[Path]:
    gui_input = work_dir / "input" / "gui"
    if not gui_input.exists():
        return []
    return sorted(path for path in gui_input.glob("*.svg") if path.is_file())


def svg_prefix(path: Path) -> str:
    upper = path.name.upper()
    for prefix in sorted(SVG_INBOX_PREFIXES, key=len, reverse=True):
        if upper.startswith(f"{prefix}_"):
            return prefix
    return ""


def validate_svg_xml(path: Path) -> tuple[bool, str]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return False, str(exc)
    if local_name(root.tag).lower() != "svg":
        return False, f"root element is not svg: {local_name(root.tag)}"
    return True, ""


def inspect_svg_input_dir(repo_root: Path, svg_input_dir: Path) -> dict[str, Any]:
    files = sorted(path for path in svg_input_dir.glob("*.svg") if path.is_file()) if svg_input_dir.exists() else []
    items: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []
    stems: dict[str, list[str]] = {}
    for path in files:
        prefix = svg_prefix(path)
        ok, parse_error = validate_svg_xml(path)
        route = SVG_INBOX_PREFIXES.get(prefix, "")
        item = {
            "path": relative_to_repo(repo_root, path),
            "prefix": prefix or "unknown",
            "route": route or "unrouted",
            "valid_svg": ok,
            "error": parse_error,
        }
        items.append(item)
        if not prefix:
            errors.append(f"unknown-prefix:{relative_to_repo(repo_root, path)}")
        if not ok:
            errors.append(f"invalid-svg:{relative_to_repo(repo_root, path)}:{parse_error}")
        stem_key = path.stem.split("_", 1)[-1].lower() if "_" in path.stem else path.stem.lower()
        stems.setdefault(stem_key, []).append(path.name)
    for stem, names in sorted(stems.items()):
        if len(names) > 1:
            warnings.append(f"same-screen-name:{stem}:{','.join(sorted(names))}")
    return {
        "status": "pass" if not errors else "fail",
        "input_dir": relative_to_repo(repo_root, svg_input_dir),
        "file_count": len(files),
        "items": items,
        "errors": errors,
        "warnings": warnings,
        "allowed_prefixes": SVG_INBOX_PREFIXES,
    }


def claim_svg_inputs(
    repo_root: Path,
    work_dir: Path,
    svg_input_dir: Path,
    input_prefix: str,
) -> tuple[list[Path], list[str]]:
    existing = discover_svg_files(work_dir)
    if existing:
        return existing, []

    pending = discover_inbox_svg_files(svg_input_dir, input_prefix)
    if not pending:
        return [], []

    destination_dir = work_dir / "input" / "gui"
    destination_dir.mkdir(parents=True, exist_ok=True)
    claimed: list[Path] = []
    source_paths: list[str] = []
    for source in pending:
        destination = destination_dir / source.name
        if destination.exists():
            raise FileExistsError(
                f"Cannot claim SVG because destination already exists: {destination}"
            )
        source_paths.append(relative_to_repo(repo_root, source))
        shutil.move(str(source), str(destination))
        claimed.append(destination)
    return claimed, source_paths


def existing_outputs(output_dir: Path) -> list[Path]:
    return [
        output_dir / relative
        for relative in REQUIRED_OUTPUTS
        if (output_dir / relative).exists()
    ]


def write_artifacts(
    repo_root: Path,
    work_dir: Path,
    issue_id: str,
    mode: str,
    svg_files: list[Path],
    input_source_files: list[str],
    svg_input_dir: Path,
    input_prefix: str,
    documents: list[SvgDocument],
    model: dict[str, Any],
) -> dict[str, Any]:
    output_dir = work_dir / "gac-uac"
    generated_pyqt = output_dir / "generated" / "pyqt6"
    generated_widgets = generated_pyqt / "widgets"
    generated_tests = output_dir / "generated" / "tests"
    review_dir = output_dir / "review"
    generated_widgets.mkdir(parents=True, exist_ok=True)
    generated_tests.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)

    write_markdown_bom(
        output_dir / "svg-analysis.md",
        render_svg_analysis(documents, issue_id, mode),
    )
    (output_dir / "semantic-layout-graph.yaml").write_text(
        render_semantic_yaml(model),
        encoding="utf-8",
    )
    write_markdown_bom(
        output_dir / "widget-mapping.md",
        render_widget_mapping(model, issue_id, mode),
    )
    write_markdown_bom(
        output_dir / "layout-spec.md",
        render_layout_spec(model, issue_id, mode),
    )
    write_markdown_bom(
        output_dir / "pyqt6-generation-plan.md",
        render_generation_plan(issue_id, mode, "pyqt6"),
    )
    write_markdown_bom(
        output_dir / "qtest-generation-plan.md",
        render_generation_plan(issue_id, mode, "qtest"),
    )
    (generated_pyqt / "main_window.py").write_text(
        render_pyqt6(model),
        encoding="utf-8",
    )
    (generated_pyqt / "__init__.py").write_text(
        "from .main_window import MainWindow, create_window\n",
        encoding="utf-8",
    )
    (generated_widgets / "__init__.py").write_text(
        '"""Generated custom widget candidates belong in this package."""\n',
        encoding="utf-8",
    )
    (generated_tests / "test_gui_smoke.py").write_text(
        render_qtest(model),
        encoding="utf-8",
    )
    write_markdown_bom(
        review_dir / "gac-uac-review.md",
        render_review(issue_id, mode, svg_files),
    )

    now = utc_now_iso()
    state = {
        "schema_version": "1.0",
        "issue_id": issue_id,
        "issue_prefix": issue_id.split("-", 1)[0].upper(),
        "mode": mode,
        "status": "complete",
        "enabled": True,
        "work_dir": relative_to_repo(repo_root, work_dir),
        "svg_files": [relative_to_repo(repo_root, path) for path in svg_files],
        "input_source_files": input_source_files,
        "svg_input_dir": relative_to_repo(repo_root, svg_input_dir),
        "input_prefix": input_prefix,
        "existing_source_dir": relative_to_repo(repo_root, work_dir / "source"),
        "existing_tests_dir": relative_to_repo(repo_root, work_dir / "tests"),
        "generated_at": now,
        "artifacts": [
            relative_to_repo(repo_root, output_dir / relative)
            for relative in REQUIRED_OUTPUTS
        ],
        "parent_workflow_return": {
            "ready": True,
            "required_artifacts": [
                "gac-uac/layout-spec.md",
                "gac-uac/widget-mapping.md",
                "gac-uac/generated/pyqt6",
                "gac-uac/generated/tests",
            ],
            "integration_policy": "review-generated-candidates-before-copy",
        },
    }
    write_json(output_dir / "gui-mode-state.json", state)
    write_json(context_file(work_dir, "gui-mode-state.json"), state)

    artifact_index = load_artifact_index(work_dir, issue_id, "gac-uac-gui-mode")
    artifact_definitions = [
        ("GUI-ANALYSIS", "SVG Analysis", "svg-analysis.md", "design"),
        ("GUI-SLG", "Semantic Layout Graph", "semantic-layout-graph.yaml", "design"),
        ("GUI-MAPPING", "Widget Mapping", "widget-mapping.md", "design"),
        ("GUI-LAYOUT", "Layout Spec", "layout-spec.md", "design"),
        ("GUI-PYQT", "Generated PyQt6 Candidate", "generated/pyqt6/main_window.py", "other"),
        ("GUI-QTEST", "Generated QTest Candidate", "generated/tests/test_gui_smoke.py", "test"),
        ("GUI-REVIEW", "GaC UaC Review", "review/gac-uac-review.md", "review"),
        ("GUI-STATE", "GUI Mode State", "gui-mode-state.json", "other"),
    ]
    for artifact_id, title, relative, artifact_type in artifact_definitions:
        upsert_artifact(
            artifact_index,
            {
                "id": artifact_id,
                "title": title,
                "path": relative_to_repo(repo_root, output_dir / relative),
                "type": artifact_type,
                "status": "in-review" if artifact_id == "GUI-REVIEW" else "draft",
                "owner_agent": "gac-uac-gui-mode",
                "created_at": now,
                "updated_at": now,
                "depends_on": [relative_to_repo(repo_root, path) for path in svg_files],
                "consumed_by": ["parent-workflow", "ariadne-tester-agent"],
                "summary": "SVGから生成したGUI設計または実装候補。",
                "unresolved_items": ["Human review is required before source integration."],
            },
        )
    write_json(context_file(work_dir, "artifact-index.json"), artifact_index)
    return state


def validate_outputs(work_dir: Path) -> dict[str, Any]:
    output_dir = work_dir / "gac-uac"
    missing = [
        relative
        for relative in REQUIRED_OUTPUTS
        if not (output_dir / relative).exists()
    ]
    errors: list[str] = []
    warnings: list[str] = []
    if missing:
        errors.extend(f"missing:{relative}" for relative in missing)

    pyqt_path = output_dir / "generated" / "pyqt6" / "main_window.py"
    test_path = output_dir / "generated" / "tests" / "test_gui_smoke.py"
    for path in (pyqt_path, test_path):
        if path.exists():
            text = path.read_text(encoding="utf-8-sig")
            try:
                ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                errors.append(f"syntax:{path.name}:{exc}")
    if pyqt_path.exists():
        text = pyqt_path.read_text(encoding="utf-8-sig")
        if "setGeometry(" in text:
            errors.append("policy:setGeometry")
        if "setObjectName(" not in text:
            errors.append("policy:objectName-missing")
        if "action_requested" not in text:
            warnings.append("signal:no-action-signal")
    if test_path.exists():
        text = test_path.read_text(encoding="utf-8-sig")
        for required in ("QApplication", "findChild", "QT_QPA_PLATFORM"):
            if required not in text:
                errors.append(f"qtest:{required}-missing")

    state_path = output_dir / "gui-mode-state.json"
    state = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            errors.append(f"state-json:{exc}")
    if state and not state.get("parent_workflow_return", {}).get("ready"):
        errors.append("state:parent-workflow-return-not-ready")

    return {
        "status": "pass" if not errors else "fail",
        "work_dir": str(work_dir),
        "errors": errors,
        "warnings": warnings,
        "checked_outputs": REQUIRED_OUTPUTS,
    }


def run_init_input(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    svg_input_dir = resolve_svg_input_dir(repo_root, args.svg_input_dir)
    svg_input_dir.mkdir(parents=True, exist_ok=True)
    readme = svg_input_dir / "README.md"
    if not readme.exists() or args.force:
        write_markdown_bom(readme, input_readme())
    return {
        "status": "ready",
        "input_dir": relative_to_repo(repo_root, svg_input_dir),
        "readme": relative_to_repo(repo_root, readme),
    }


def run_inspect_input(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    svg_input_dir = resolve_svg_input_dir(repo_root, args.svg_input_dir)
    return inspect_svg_input_dir(repo_root, svg_input_dir)


def run_generate(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = resolve_work_dir(repo_root, args.issue_id, args.work_dir)
    if not getattr(args, "skip_context_check", False):
        require_environment_selection(repo_root, work_dir, expected_environment="gui-mode")
    mode = infer_mode(args.issue_id, args.mode)
    input_prefix = args.input_prefix or input_prefix_for_mode(mode)
    svg_input_dir = resolve_svg_input_dir(repo_root, args.svg_input_dir)
    output_dir = work_dir / "gac-uac"
    existing = existing_outputs(output_dir)
    if existing and not args.force:
        names = ", ".join(str(path.relative_to(work_dir)) for path in existing)
        raise FileExistsError(
            "GUI mode outputs already exist. Review them or rerun with --force: "
            f"{names}"
        )
    svg_files, input_source_files = claim_svg_inputs(
        repo_root=repo_root,
        work_dir=work_dir,
        svg_input_dir=svg_input_dir,
        input_prefix=input_prefix,
    )
    if not svg_files:
        state = {
            "schema_version": "1.0",
            "issue_id": args.issue_id,
            "issue_prefix": args.issue_id.split("-", 1)[0].upper(),
            "mode": mode,
            "status": "skipped",
            "enabled": False,
            "work_dir": relative_to_repo(repo_root, work_dir),
            "svg_files": [],
            "input_source_files": [],
            "svg_input_dir": relative_to_repo(repo_root, svg_input_dir),
            "input_prefix": input_prefix,
            "existing_source_dir": relative_to_repo(repo_root, work_dir / "source"),
            "existing_tests_dir": relative_to_repo(repo_root, work_dir / "tests"),
            "generated_at": utc_now_iso(),
            "artifacts": [],
            "reason": (
                f"No {input_prefix}_*.svg files found under "
                f"{relative_to_repo(repo_root, svg_input_dir)}."
            ),
            "return_to_parent_workflow": True,
            "parent_workflow_return": {
                "ready": True,
                "required_artifacts": [],
                "integration_policy": "review-generated-candidates-before-copy",
            },
        }
        state_path = context_file(work_dir, "gui-mode-state.json")
        write_json(state_path, state)
        register_context(
            repo_root,
            work_dir,
            work_id=args.issue_id,
            context_type="gui-mode-state",
            path=state_path,
            required=False,
            generated_by="gui-mode",
            owner="workflow",
            schema=GUI_MODE_STATE_SCHEMA,
            status="skipped",
        )
        return state

    documents = [parse_svg(path) for path in svg_files]
    model = build_model(documents, args.issue_id, mode)
    state = write_artifacts(
        repo_root=repo_root,
        work_dir=work_dir,
        issue_id=args.issue_id,
        mode=mode,
        svg_files=svg_files,
        input_source_files=input_source_files,
        svg_input_dir=svg_input_dir,
        input_prefix=input_prefix,
        documents=documents,
        model=model,
    )
    validation = validate_outputs(work_dir)
    if validation["status"] != "pass":
        raise RuntimeError(f"Generated GUI mode artifacts failed validation: {validation['errors']}")
    state["validation"] = validation
    write_json(output_dir / "gui-mode-state.json", state)
    state_path = context_file(work_dir, "gui-mode-state.json")
    write_json(state_path, state)
    register_context(
        repo_root,
        work_dir,
        work_id=args.issue_id,
        context_type="gui-mode-state",
        path=state_path,
        required=False,
        generated_by="gui-mode",
        owner="workflow",
        schema=GUI_MODE_STATE_SCHEMA,
    )
    return state


def run_validate(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = resolve_work_dir(repo_root, args.issue_id, args.work_dir)
    return validate_outputs(work_dir)


SELF_TEST_SVG = """\
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


def make_self_test_args(repo_root: Path, issue_id: str, mode: str = "auto") -> argparse.Namespace:
    return argparse.Namespace(
        repo_root=str(repo_root),
        work_dir=None,
        issue_id=issue_id,
        mode=mode,
        force=False,
        svg_input_dir=None,
        input_prefix=None,
        skip_context_check=True,
    )


def assert_self_test(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_self_test(args: argparse.Namespace) -> dict[str, Any]:
    checks: list[str] = []
    with tempfile.TemporaryDirectory(prefix="gui-mode-self-test-") as raw_root:
        repo_root = Path(raw_root)

        (work_dir_for_id(repo_root, "SYS-0001")).mkdir(parents=True)
        skipped = run_generate(make_self_test_args(repo_root, "SYS-0001"))
        assert_self_test(skipped["status"] == "skipped", "missing SVG should skip")
        assert_self_test(
            (work_dir_for_id(repo_root, "SYS-0001") / "context" / "gui-mode-state.json").exists(),
            "skipped state should be written",
        )
        checks.append("skip-without-svg")

        svg_input = svg_input_dir(repo_root)
        svg_input.mkdir(parents=True)
        other_flow_svg = svg_input / "FEAT_other-flow.svg"
        other_flow_svg.write_text(SELF_TEST_SVG, encoding="utf-8")
        skipped_sys = run_generate(make_self_test_args(repo_root, "SYS-0002"))
        assert_self_test(skipped_sys["status"] == "skipped", "SYS should ignore FEAT SVG")
        assert_self_test(other_flow_svg.exists(), "unmatched SVG must stay in inbox")
        checks.append("prefix-isolation")

        source_svg = svg_input / "FEAT_robot-console.svg"
        source_svg.write_text(SELF_TEST_SVG, encoding="utf-8")
        generated = run_generate(make_self_test_args(repo_root, "FEAT-0001"))
        assert_self_test(generated["status"] == "complete", "FEAT SVG should generate")
        assert_self_test(generated["mode"] == "feature-development", "FEAT mode mismatch")
        assert_self_test(generated["input_prefix"] == "FEAT", "FEAT input prefix mismatch")
        assert_self_test(not source_svg.exists(), "claimed SVG should be moved from inbox")
        issue_svg = work_dir_for_id(repo_root, "FEAT-0001") / "input" / "gui" / "FEAT_robot-console.svg"
        assert_self_test(issue_svg.exists(), "claimed SVG should exist under issue input/gui")
        output_dir = work_dir_for_id(repo_root, "FEAT-0001") / "gac-uac"
        assert_self_test((output_dir / "layout-spec.md").exists(), "layout spec missing")
        assert_self_test(
            (output_dir / "generated" / "pyqt6" / "widgets" / "__init__.py").exists(),
            "generated widgets package missing",
        )
        pyqt_source = (output_dir / "generated" / "pyqt6" / "main_window.py").read_text(
            encoding="utf-8"
        )
        assert_self_test("setGeometry(" not in pyqt_source, "generated source must not use setGeometry")
        assert_self_test("connect_button_text =" not in pyqt_source, "button text should merge into button")
        assert_self_test(
            validate_outputs(work_dir_for_id(repo_root, "FEAT-0001"))["status"] == "pass",
            "generated outputs should validate",
        )
        checks.append("generate-and-validate")

        later_svg = svg_input / "FEAT_later-screen.svg"
        later_svg.write_text(SELF_TEST_SVG, encoding="utf-8")
        try:
            run_generate(make_self_test_args(repo_root, "FEAT-0001"))
        except FileExistsError:
            pass
        else:
            raise AssertionError("existing outputs should require --force")
        assert_self_test(later_svg.exists(), "existing-output guard should not claim new SVG")
        checks.append("existing-output-guard")

    return {
        "status": "pass",
        "checks": checks,
    }


def add_work_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--issue-id", required=True, help="Issue/work ID such as SYS-0001, FEAT-0001, or FIX-0001.")
    parser.add_argument("--work-dir", help="Explicit work directory. Default: work/<issue-id>.")
    parser.add_argument("--repo-root", help="Workflow repository root.")
    parser.add_argument(
        "--svg-input-dir",
        help="Shared SVG inbox. Default: work/requirements/svg-input.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dispatch SVG-based GaC/UaC GUI mode as a parent-workflow extension."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init-input",
        help="Create work/requirements/svg-input/ and its naming guide.",
    )
    init_parser.add_argument("--repo-root", help="Workflow repository root.")
    init_parser.add_argument(
        "--svg-input-dir",
        help="Shared SVG inbox. Default: work/requirements/svg-input.",
    )
    init_parser.add_argument("--force", action="store_true", help="Replace the input README.")
    init_parser.set_defaults(handler=run_init_input)

    inspect_parser = subparsers.add_parser(
        "inspect-input",
        help="Validate shared SVG inbox prefixes and XML without claiming files.",
    )
    inspect_parser.add_argument("--repo-root", help="Workflow repository root.")
    inspect_parser.add_argument(
        "--svg-input-dir",
        help="Shared SVG inbox. Default: work/requirements/svg-input.",
    )
    inspect_parser.set_defaults(handler=run_inspect_input)

    run_parser = subparsers.add_parser("run", help="Generate GUI design, PyQt6, and QTest candidates when SVG exists.")
    add_work_arguments(run_parser)
    run_parser.add_argument(
        "--mode",
        default="auto",
        choices=[
            "auto",
            "system-development",
            "feature-development",
            "corrective-improvement",
            "generic-gui",
        ],
    )
    run_parser.add_argument("--force", action="store_true", help="Regenerate existing GUI mode outputs.")
    run_parser.add_argument(
        "--input-prefix",
        choices=["SYS", "FEAT", "FIX", "GUI"],
        help="Override the SVG filename prefix selected from the GUI mode.",
    )
    run_parser.add_argument(
        "--skip-context-check",
        action="store_true",
        help="Skip Context First environment-selection gate. Intended for runtime self-tests only.",
    )
    run_parser.set_defaults(handler=run_generate)

    validate_parser = subparsers.add_parser("validate", help="Validate GUI mode completion and generated source policies.")
    add_work_arguments(validate_parser)
    validate_parser.set_defaults(handler=run_validate)

    self_test_parser = subparsers.add_parser(
        "self-test",
        help="Run deterministic GUI mode runtime checks without requiring PyQt6.",
    )
    self_test_parser.set_defaults(handler=run_self_test)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") not in {"fail"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
