from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
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


MODE_BY_PREFIX = {
    "WEB_SYS": "new-app",
    "WEB_FEAT": "existing-app-feature",
    "WEB_FIX": "corrective-fix",
    "NEXT_SYS": "new-app",
    "NEXT_FEAT": "existing-app-feature",
    "NEXT_FIX": "corrective-fix",
}
INPUT_PREFIX_BY_MODE = {
    "new-app": "WEB_SYS",
    "existing-app-feature": "WEB_FEAT",
    "corrective-fix": "WEB_FIX",
    "generic-web-ui": "WEB",
}
MODE_FOCUS = {
    "new-app": "新規web appの初期route、layout、component責務、Playwright導線",
    "existing-app-feature": "既存routing、design system、component規約との整合と差分統合",
    "corrective-fix": "最小変更、既存画面挙動維持、visual regression防止",
    "generic-web-ui": "Web画面向けの論理layout、component責務、responsive構成",
}
REQUIRED_OUTPUTS = [
    "svg-analysis.md",
    "route-layout-map.yaml",
    "component-mapping.md",
    "responsive-layout-spec.md",
    "react-generation-plan.md",
    "playwright-generation-plan.md",
    "generated/web/SvgLayoutCandidate.tsx",
    "generated/tests/svg-layout.spec.ts",
    "review/web-svg-layout-review.md",
    "web-svg-layout-state.json",
]
SHAPE_TAGS = {"rect", "text", "line", "circle", "ellipse", "path", "polygon", "polyline"}
ACTION_WORDS = {
    "add",
    "apply",
    "cancel",
    "close",
    "connect",
    "create",
    "delete",
    "disconnect",
    "edit",
    "open",
    "reset",
    "save",
    "search",
    "send",
    "start",
    "stop",
    "submit",
    "update",
    "追加",
    "適用",
    "取消",
    "閉じる",
    "接続",
    "作成",
    "削除",
    "切断",
    "編集",
    "開く",
    "リセット",
    "保存",
    "検索",
    "送信",
    "開始",
    "停止",
    "登録",
    "更新",
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


def pascal_case(value: str) -> str:
    parts = re.split(r"[^0-9A-Za-z]+", value)
    result = "".join(part[:1].upper() + part[1:] for part in parts if part)
    return result or "Component"


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
            group_id = safe_identifier(node.attrib.get("id", ""), f"section_{len(groups) + 1}")
            groups.append(group_id)
            next_stack = [*group_stack, group_id]

        if tag in SHAPE_TAGS:
            counters[tag] = counters.get(tag, 0) + 1
            element_id = safe_identifier(node.attrib.get("id", ""), f"{tag}_{counters[tag]}")
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
    if prefix in {"SYS", "WEBSYS", "NEXTSYS"}:
        return "new-app"
    if prefix in {"FEAT", "WEBFEAT", "NEXTFEAT"}:
        return "existing-app-feature"
    if prefix in {"FIX", "WEBFIX", "NEXTFIX"}:
        return "corrective-fix"
    return "generic-web-ui"


def infer_component_type(element: SvgElement) -> str:
    haystack = " ".join([element.element_id, element.class_name, element.text]).lower()
    text = clean_text(element.text).lower()
    if any(word in haystack for word in ("button", "btn", "cta")) or text in ACTION_WORDS:
        return "button"
    if any(word in haystack for word in ("input", "field", "textbox", "search")):
        return "input"
    if any(word in haystack for word in ("select", "dropdown", "combo")):
        return "select"
    if any(word in haystack for word in ("toggle", "switch", "check")):
        return "checkbox"
    if any(word in haystack for word in ("table", "grid", "list")):
        return "data_region"
    if any(word in haystack for word in ("chart", "graph", "metric", "kpi")):
        return "metric"
    if any(word in haystack for word in ("nav", "menu", "tab", "sidebar")):
        return "navigation"
    if element.tag == "text":
        return "text"
    if element.tag in {"rect", "polygon", "polyline"} and any(
        word in haystack for word in ("card", "panel", "section", "region")
    ):
        return "section"
    return "decorative"


def infer_section_role(section_id: str) -> str:
    lowered = section_id.lower()
    if any(word in lowered for word in ("header", "top", "toolbar")):
        return "header"
    if any(word in lowered for word in ("nav", "menu", "sidebar", "rail")):
        return "navigation"
    if any(word in lowered for word in ("filter", "search", "form")):
        return "input"
    if any(word in lowered for word in ("metric", "summary", "kpi")):
        return "summary"
    if any(word in lowered for word in ("table", "list", "grid", "content")):
        return "content"
    if any(word in lowered for word in ("footer", "status", "log")):
        return "status"
    return "section"


def infer_responsibility(component_type: str, label: str) -> str:
    if component_type == "button":
        return f"{label} のユーザー操作をactionとして扱う"
    if component_type in {"input", "select", "checkbox"}:
        return f"{label} の入力状態を保持しvalidationへ渡す"
    if component_type in {"data_region", "metric"}:
        return f"{label} の業務データまたは状態を表示する"
    if component_type == "navigation":
        return f"{label} への移動または表示切替を提供する"
    return f"{label} を表示する"


def build_model(documents: list[SvgDocument], issue_id: str, mode: str) -> dict[str, Any]:
    section_ids = list(dict.fromkeys(group for document in documents for group in document.groups)) or ["content"]
    components: list[dict[str, str]] = []
    used_ids: set[str] = set()

    for document in documents:
        for element in document.elements:
            component_type = infer_component_type(element)
            if component_type == "decorative":
                continue
            if component_type == "button" and element.tag == "text":
                previous = next(
                    (
                        component
                        for component in reversed(components)
                        if component["type"] == "button"
                        and component["section"] == element.parent_group
                        and component["source"] == element.source
                    ),
                    None,
                )
                if previous is not None:
                    previous["label"] = element.text or previous["label"]
                    previous["responsibility"] = infer_responsibility("button", previous["label"])
                    continue
            component_id = safe_identifier(element.element_id, f"component_{len(components) + 1}")
            suffix = 2
            while component_id in used_ids:
                component_id = f"{component_id}_{suffix}"
                suffix += 1
            used_ids.add(component_id)
            label = element.text or component_id.replace("_", " ").title()
            components.append(
                {
                    "id": component_id,
                    "type": component_type,
                    "label": label,
                    "section": element.parent_group if element.parent_group in section_ids else section_ids[0],
                    "responsibility": infer_responsibility(component_type, label),
                    "source": element.source,
                }
            )

    if not components:
        components.append(
            {
                "id": "content_region",
                "type": "section",
                "label": "Content",
                "section": section_ids[0],
                "responsibility": "画面の主要内容を表示する",
                "source": documents[0].path.name,
            }
        )

    title = next((document.title for document in documents if document.title), f"{issue_id} Web UI")
    return {
        "screen": {
            "id": "svg_layout_candidate",
            "title": title,
            "purpose": f"{issue_id} のSVG画面意図をWeb画面向けの論理layoutへ変換する",
            "route_candidate": "/",
        },
        "sections": [
            {
                "id": section_id,
                "role": infer_section_role(section_id),
                "component": f"{pascal_case(section_id)}Section",
            }
            for section_id in section_ids
        ],
        "components": components,
        "responsive_rules": [
            "mobile: single-column layout with navigation collapsed or stacked",
            "tablet: two-column layout only when content remains readable",
            "desktop: use CSS grid/flex areas, not absolute SVG coordinates",
            "all: preserve accessible labels, focus order, loading/empty/error states",
            f"mode={mode}: {MODE_FOCUS[mode]}",
        ],
        "test_targets": [
            {
                "test_id": component["id"],
                "checks": ["visible", "accessible_label"]
                + (["click_action"] if component["type"] == "button" else []),
            }
            for component in components
        ],
    }


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_yaml(model: dict[str, Any]) -> str:
    lines = [
        "screen:",
        f"  id: {yaml_string(model['screen']['id'])}",
        f"  title: {yaml_string(model['screen']['title'])}",
        f"  purpose: {yaml_string(model['screen']['purpose'])}",
        f"  route_candidate: {yaml_string(model['screen']['route_candidate'])}",
        "",
        "sections:",
    ]
    for section in model["sections"]:
        lines.extend(
            [
                f"  - id: {yaml_string(section['id'])}",
                f"    role: {yaml_string(section['role'])}",
                f"    component: {yaml_string(section['component'])}",
            ]
        )
    lines.extend(["", "components:"])
    for component in model["components"]:
        lines.extend(
            [
                f"  - id: {yaml_string(component['id'])}",
                f"    type: {yaml_string(component['type'])}",
                f"    label: {yaml_string(component['label'])}",
                f"    section: {yaml_string(component['section'])}",
                f"    responsibility: {yaml_string(component['responsibility'])}",
                f"    source: {yaml_string(component['source'])}",
            ]
        )
    lines.extend(["", "responsive_rules:"])
    lines.extend(f"  - {yaml_string(item)}" for item in model["responsive_rules"])
    lines.extend(["", "test_targets:"])
    for target in model["test_targets"]:
        lines.append(f"  - test_id: {yaml_string(target['test_id'])}")
        lines.append("    checks:")
        lines.extend(f"      - {yaml_string(check)}" for check in target["checks"])
    return "\n".join(lines) + "\n"


def front_matter(issue_id: str, mode: str, phase: str, status: str = "draft") -> str:
    return (
        "---\n"
        "language: ja-JP\n"
        f"issue_id: {issue_id}\n"
        "workflow: web-svg-layout-mode\n"
        f"mode: {mode}\n"
        f"phase: {phase}\n"
        f"status: {status}\n"
        "---\n\n"
    )


def render_svg_analysis(documents: list[SvgDocument], issue_id: str, mode: str) -> str:
    lines = [
        front_matter(issue_id, mode, "svg-analysis"),
        "# Web SVG Analysis",
        "",
        "## 画面概要",
        "",
        f"- 対象Issue: `{issue_id}`",
        f"- Web UI mode: `{mode}`",
        f"- 変換方針: {MODE_FOCUS[mode]}",
        "- SVG座標の再現ではなく、route、section、component責務、responsive layoutへ変換する。",
        "",
        "## SVGファイル",
        "",
        "| File | Width | Height | viewBox | Groups | Elements |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for document in documents:
        lines.append(
            f"| `{document.path.name}` | {document.width or '-'} | {document.height or '-'} | "
            f"`{document.view_box or '-'}` | {len(document.groups)} | {len(document.elements)} |"
        )
    lines.extend(["", "## SVG要素一覧", "", "| SVG | Tag | ID | Class | Text | Parent | 推定component |", "| --- | --- | --- | --- | --- | --- | --- |"])
    for document in documents:
        for element in document.elements:
            lines.append(
                f"| `{element.source}` | `{element.tag}` | `{element.element_id}` | "
                f"`{element.class_name or '-'}` | {element.text or '-'} | "
                f"`{element.parent_group}` | `{infer_component_type(element)}` |"
            )
    lines.extend(
        [
            "",
            "## 不明点",
            "",
            "- SVGだけではAPI contract、loading / empty / error、auth、role、data freshnessは確定できない。",
            "- 色や図形が状態表現か装飾かは、要件、既存design system、実装対象appで確認する。",
        ]
    )
    return "\n".join(lines)


def html_element(component_type: str) -> str:
    return {
        "button": "button",
        "input": "input",
        "select": "select",
        "checkbox": "input",
        "data_region": "section",
        "metric": "article",
        "navigation": "nav",
        "text": "p",
        "section": "section",
    }.get(component_type, "div")


def render_component_mapping(model: dict[str, Any], issue_id: str, mode: str) -> str:
    lines = [
        front_matter(issue_id, mode, "component-mapping"),
        "# Component Mapping",
        "",
        "| ID | Type | Suggested HTML / React | Section | Responsibility | Test ID |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for component in model["components"]:
        lines.append(
            f"| `{component['id']}` | `{component['type']}` | `{html_element(component['type'])}` | "
            f"`{component['section']}` | {component['responsibility']} | `{component['id']}` |"
        )
    lines.extend(
        [
            "",
            "## 統合方針",
            "",
            "- 既存appでは既存component、design system、routing、CSS module / Tailwind / UI libraryの規約を優先する。",
            "- generated componentは候補であり、既存sourceへ自動コピーしない。",
            "- API request / response、auth、role、env境界はWebapp Implementation Prepの結果と照合する。",
        ]
    )
    return "\n".join(lines)


def render_responsive_spec(model: dict[str, Any], issue_id: str, mode: str) -> str:
    lines = [
        front_matter(issue_id, mode, "responsive-layout-spec"),
        "# Responsive Layout Spec",
        "",
        "## Route Candidate",
        "",
        f"- Route: `{model['screen']['route_candidate']}`",
        f"- Title: {model['screen']['title']}",
        "",
        "## Sections",
        "",
        "| Section | Role | Component |",
        "| --- | --- | --- |",
    ]
    for section in model["sections"]:
        lines.append(f"| `{section['id']}` | `{section['role']}` | `{section['component']}` |")
    lines.extend(["", "## Responsive Rules", ""])
    lines.extend(f"- {rule}" for rule in model["responsive_rules"])
    lines.extend(
        [
            "",
            "## Required UI States",
            "",
            "- loading",
            "- empty",
            "- error",
            "- success / updated",
            "- unauthorized / forbidden when auth is required",
        ]
    )
    return "\n".join(lines)


def render_generation_plan(issue_id: str, mode: str, kind: str) -> str:
    title = "React Generation Plan" if kind == "react" else "Playwright Generation Plan"
    checks = [
        "対象web frameworkのrouting方式を確認する。",
        "既存design systemとCSS規約を確認する。",
        "生成候補を既存sourceへ無条件コピーしない。",
    ]
    if kind == "playwright":
        checks.extend(
            [
                "route、auth fixture、API mock / real API方針を確認する。",
                "visual smokeはAPI contractやunit testの代替にしない。",
            ]
        )
    return front_matter(issue_id, mode, f"{kind}-generation-plan") + "\n".join(
        [
            f"# {title}",
            "",
            f"- Issue: `{issue_id}`",
            f"- Mode: `{mode}`",
            "",
            "## Checks",
            "",
            *[f"- {check}" for check in checks],
        ]
    )


def ts_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_tsx(model: dict[str, Any]) -> str:
    lines = [
        '"use client";',
        "",
        "type SvgLayoutCandidateProps = {",
        "  title?: string;",
        "  onAction?: (actionId: string) => void;",
        "};",
        "",
        "const sections = [",
    ]
    for section in model["sections"]:
        lines.append(
            f"  {{ id: {ts_string(section['id'])}, role: {ts_string(section['role'])}, label: {ts_string(section['component'])} }},"
        )
    lines.extend(
        [
            "] as const;",
            "",
            "const components = [",
        ]
    )
    for component in model["components"]:
        lines.append(
            "  { "
            f"id: {ts_string(component['id'])}, "
            f"type: {ts_string(component['type'])}, "
            f"label: {ts_string(component['label'])}, "
            f"section: {ts_string(component['section'])} "
            "},"
        )
    lines.extend(
        [
            "] as const;",
            "",
            "export function SvgLayoutCandidate({ title = \"SVG Layout Candidate\", onAction }: SvgLayoutCandidateProps) {",
            "  return (",
            "    <main className=\"svg-layout-candidate\" data-testid=\"svg-layout-candidate\">",
            "      <header className=\"svg-layout-candidate__header\">",
            "        <h1>{title}</h1>",
            "      </header>",
            "      <div className=\"svg-layout-candidate__grid\">",
            "        {sections.map((section) => (",
            "          <section key={section.id} className=\"svg-layout-candidate__section\" data-testid={section.id} aria-label={section.label}>",
            "            <h2>{section.label}</h2>",
            "            {components.filter((component) => component.section === section.id).map((component) => {",
            "              if (component.type === \"button\") {",
            "                return (",
            "                  <button key={component.id} type=\"button\" data-testid={component.id} onClick={() => onAction?.(component.id)}>",
            "                    {component.label}",
            "                  </button>",
            "                );",
            "              }",
            "              if (component.type === \"input\") {",
            "                return <input key={component.id} data-testid={component.id} aria-label={component.label} placeholder={component.label} />;",
            "              }",
            "              if (component.type === \"select\") {",
            "                return <select key={component.id} data-testid={component.id} aria-label={component.label}><option>{component.label}</option></select>;",
            "              }",
            "              if (component.type === \"checkbox\") {",
            "                return <label key={component.id}><input type=\"checkbox\" data-testid={component.id} />{component.label}</label>;",
            "              }",
            "              return <div key={component.id} data-testid={component.id}>{component.label}</div>;",
            "            })}",
            "          </section>",
            "        ))}",
            "      </div>",
            "    </main>",
            "  );",
            "}",
            "",
            "export default SvgLayoutCandidate;",
            "",
        ]
    )
    return "\n".join(lines)


def render_playwright(model: dict[str, Any]) -> str:
    first_target = model["test_targets"][0]["test_id"]
    lines = [
        "import { expect, test } from \"@playwright/test\";",
        "",
        "test.describe(\"SVG layout candidate\", () => {",
        "  test(\"renders candidate layout\", async ({ page }) => {",
        "    await page.goto(\"/\");",
        "    await expect(page.getByTestId(\"svg-layout-candidate\")).toBeVisible();",
    ]
    for target in model["test_targets"]:
        lines.append(f"    await expect(page.getByTestId({ts_string(target['test_id'])})).toBeVisible();")
    lines.extend(
        [
            "  });",
            "",
            "  test(\"keeps first inferred element reachable\", async ({ page }) => {",
            "    await page.goto(\"/\");",
            f"    await expect(page.getByTestId({ts_string(first_target)})).toBeVisible();",
            "  });",
            "});",
            "",
        ]
    )
    return "\n".join(lines)


def render_review(issue_id: str, mode: str, svg_files: list[Path]) -> str:
    return front_matter(issue_id, mode, "web-svg-layout-review", "in-review") + "\n".join(
        [
            "# Web SVG Layout Review",
            "",
            "## Review Status",
            "",
            "- Status: `human-review-required`",
            f"- SVG inputs: {', '.join(f'`{path.name}`' for path in svg_files)}",
            f"- Mode: `{mode}`",
            "",
            "## 必須確認",
            "",
            "- [ ] SVGの意図がroute、section、component責務へ正しく変換されている。",
            "- [ ] 固定座標や画像貼り付けではなくresponsive layoutになっている。",
            "- [ ] 既存web appのrouting、design system、test runnerと整合している。",
            "- [ ] API、auth、env、loading / empty / error stateを推測で固定していない。",
            "- [ ] generated配下を無条件上書きせず、採用差分がレビューされている。",
            "- [ ] Playwright候補が要件と画面契約に紐づいている。",
        ]
    )


def input_readme() -> str:
    return "\n".join(
        [
            "# SVG Input Inbox",
            "",
            "Issue作成前に、画面レイアウト意図を表すSVGをこのdirectoryへ配置します。",
            "",
            "Web画面向け:",
            "",
            "```text",
            "work/requirements/svg-input/WEB_SYS_<name>.svg",
            "work/requirements/svg-input/WEB_FEAT_<name>.svg",
            "work/requirements/svg-input/WEB_FIX_<name>.svg",
            "```",
            "",
            "既存互換として`NEXT_SYS_`、`NEXT_FEAT_`、`NEXT_FIX_`も取り込みます。",
            "",
            "PyQt / Qt向けの`SYS_`、`FEAT_`、`FIX_`とは分けます。",
            "",
            "ルール:",
            "",
            "- SVGは完成画像ではなく、route、section、component責務、responsive layout、Playwright候補を抽出する入力です。",
            "- 可能な限り`id`と`class`へ意味のある名前を付けます。",
            "- API、auth、env、業務状態はSVGへ埋め込まず、親workflowの要件とWeb画面準備reportで定義します。",
            "- Issue作成後、対応プレフィックスのSVGはIssue作業領域の`input/web-ui/`へ移動されます。",
        ]
    )


def resolve_work_dir(repo_root: Path, issue_id: str, raw_work_dir: str | None) -> Path:
    return Path(raw_work_dir).resolve() if raw_work_dir else repo_root / "work" / issue_id


def resolve_svg_input_dir(repo_root: Path, raw_input_dir: str | None) -> Path:
    return Path(raw_input_dir).resolve() if raw_input_dir else repo_root / "work" / "requirements" / "svg-input"


def input_prefix_for_mode(mode: str) -> str:
    return INPUT_PREFIX_BY_MODE[mode]


def discover_inbox_svg_files(svg_input_dir: Path, input_prefix: str) -> list[Path]:
    if not svg_input_dir.exists():
        return []
    prefixes = [input_prefix.upper()]
    if input_prefix.upper().startswith("WEB_"):
        prefixes.append(input_prefix.upper().replace("WEB_", "NEXT_", 1))
    if input_prefix.upper() == "WEB":
        prefixes.append("NEXT")
    return sorted(
        path
        for path in svg_input_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".svg"
        and any(path.name.upper().startswith(f"{prefix}_") for prefix in prefixes)
    )


def discover_svg_files(work_dir: Path) -> list[Path]:
    input_dir = work_dir / "input" / "web-ui"
    if not input_dir.exists():
        return []
    return sorted(path for path in input_dir.glob("*.svg") if path.is_file())


def claim_svg_inputs(
    work_dir: Path,
    svg_input_dir: Path,
    input_prefix: str,
    repo_root: Path,
) -> tuple[list[Path], list[str]]:
    existing = discover_svg_files(work_dir)
    if existing:
        return existing, []
    pending = discover_inbox_svg_files(svg_input_dir, input_prefix)
    if not pending:
        return [], []
    destination_dir = work_dir / "input" / "web-ui"
    destination_dir.mkdir(parents=True, exist_ok=True)
    claimed: list[Path] = []
    sources: list[str] = []
    for source in pending:
        destination = destination_dir / source.name
        if destination.exists():
            raise FileExistsError(f"Cannot claim SVG because destination already exists: {destination}")
        sources.append(relative_to_repo(repo_root, source))
        shutil.move(str(source), str(destination))
        claimed.append(destination)
    return claimed, sources


def existing_outputs(output_dir: Path) -> list[Path]:
    return [output_dir / relative for relative in REQUIRED_OUTPUTS if (output_dir / relative).exists()]


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
    output_dir = work_dir / "web-ui"
    generated_web = output_dir / "generated" / "web"
    generated_tests = output_dir / "generated" / "tests"
    review_dir = output_dir / "review"
    generated_web.mkdir(parents=True, exist_ok=True)
    generated_tests.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)

    write_markdown_bom(output_dir / "svg-analysis.md", render_svg_analysis(documents, issue_id, mode))
    (output_dir / "route-layout-map.yaml").write_text(render_yaml(model), encoding="utf-8")
    write_markdown_bom(output_dir / "component-mapping.md", render_component_mapping(model, issue_id, mode))
    write_markdown_bom(output_dir / "responsive-layout-spec.md", render_responsive_spec(model, issue_id, mode))
    write_markdown_bom(output_dir / "react-generation-plan.md", render_generation_plan(issue_id, mode, "react"))
    write_markdown_bom(output_dir / "playwright-generation-plan.md", render_generation_plan(issue_id, mode, "playwright"))
    (generated_web / "SvgLayoutCandidate.tsx").write_text(render_tsx(model), encoding="utf-8")
    (generated_tests / "svg-layout.spec.ts").write_text(render_playwright(model), encoding="utf-8")
    write_markdown_bom(review_dir / "web-svg-layout-review.md", render_review(issue_id, mode, svg_files))

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
        "generated_at": now,
        "artifacts": [relative_to_repo(repo_root, output_dir / relative) for relative in REQUIRED_OUTPUTS],
        "parent_workflow_return": {
            "ready": True,
            "required_artifacts": [
                "web-ui/responsive-layout-spec.md",
                "web-ui/component-mapping.md",
                "web-ui/generated/web",
                "web-ui/generated/tests",
            ],
            "integration_policy": "review-generated-candidates-before-copy",
        },
    }
    write_json(output_dir / "web-svg-layout-state.json", state)
    write_json(work_dir / "context" / "web-svg-layout-state.json", state)

    artifact_index = load_artifact_index(work_dir, issue_id, "web-svg-layout-mode")
    for artifact_id, title, relative, artifact_type in [
        ("WEBSVG-ANALYSIS", "Web SVG Analysis", "svg-analysis.md", "design"),
        ("WEBSVG-ROUTE", "Route Layout Map", "route-layout-map.yaml", "design"),
        ("WEBSVG-MAPPING", "Component Mapping", "component-mapping.md", "design"),
        ("WEBSVG-LAYOUT", "Responsive Layout Spec", "responsive-layout-spec.md", "design"),
        ("WEBSVG-REACT", "Generated React Candidate", "generated/web/SvgLayoutCandidate.tsx", "other"),
        ("WEBSVG-PLAYWRIGHT", "Generated Playwright Candidate", "generated/tests/svg-layout.spec.ts", "test"),
        ("WEBSVG-REVIEW", "Web SVG Layout Review", "review/web-svg-layout-review.md", "review"),
        ("WEBSVG-STATE", "Web SVG Layout State", "web-svg-layout-state.json", "other"),
    ]:
        upsert_artifact(
            artifact_index,
            {
                "id": artifact_id,
                "title": title,
                "path": relative_to_repo(repo_root, output_dir / relative),
                "type": artifact_type,
                "status": "in-review" if artifact_type == "review" else "draft",
                "owner_agent": "web-svg-layout-mode",
                "created_at": now,
                "updated_at": now,
                "depends_on": [relative_to_repo(repo_root, path) for path in svg_files],
                "consumed_by": ["parent-workflow", "webapp-implementation-prep"],
                "summary": "SVGから生成したWeb UI設計または実装候補。",
                "unresolved_items": ["Human review is required before source integration."],
            },
        )
    write_json(work_dir / "context" / "artifact-index.json", artifact_index)
    return state


def validate_outputs(work_dir: Path) -> dict[str, Any]:
    output_dir = work_dir / "web-ui"
    missing = [relative for relative in REQUIRED_OUTPUTS if not (output_dir / relative).exists()]
    errors = [f"missing:{relative}" for relative in missing]
    warnings: list[str] = []

    component_path = output_dir / "generated" / "web" / "SvgLayoutCandidate.tsx"
    test_path = output_dir / "generated" / "tests" / "svg-layout.spec.ts"
    if component_path.exists():
        text = component_path.read_text(encoding="utf-8-sig")
        for forbidden in ("dangerouslySetInnerHTML", "position: \"absolute\"", "position: 'absolute'"):
            if forbidden in text:
                errors.append(f"policy:{forbidden}")
        for required in ("data-testid", "SvgLayoutCandidate", "onAction"):
            if required not in text:
                errors.append(f"react:{required}-missing")
    if test_path.exists():
        text = test_path.read_text(encoding="utf-8-sig")
        for required in ("@playwright/test", "getByTestId", "toBeVisible"):
            if required not in text:
                errors.append(f"playwright:{required}-missing")
    state_path = output_dir / "web-svg-layout-state.json"
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            errors.append(f"state-json:{exc}")
        else:
            if not state.get("parent_workflow_return", {}).get("ready"):
                errors.append("state:parent-workflow-return-not-ready")
    else:
        warnings.append("state:not-written")
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
    readme = svg_input_dir / "WEB_README.md"
    if not readme.exists() or args.force:
        write_markdown_bom(readme, input_readme())
    return {"status": "ready", "input_dir": relative_to_repo(repo_root, svg_input_dir), "readme": relative_to_repo(repo_root, readme)}


def run_generate(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = resolve_work_dir(repo_root, args.issue_id, args.work_dir)
    mode = infer_mode(args.issue_id, args.mode)
    input_prefix = args.input_prefix or input_prefix_for_mode(mode)
    svg_input_dir = resolve_svg_input_dir(repo_root, args.svg_input_dir)
    output_dir = work_dir / "web-ui"
    existing = existing_outputs(output_dir)
    if existing and not args.force:
        names = ", ".join(str(path.relative_to(work_dir)) for path in existing)
        raise FileExistsError(f"Web SVG layout outputs already exist. Review them or rerun with --force: {names}")

    svg_files, input_source_files = claim_svg_inputs(work_dir, svg_input_dir, input_prefix, repo_root)
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
            "generated_at": utc_now_iso(),
            "artifacts": [],
            "reason": f"No {input_prefix}_*.svg files found under {relative_to_repo(repo_root, svg_input_dir)}.",
            "return_to_parent_workflow": True,
            "parent_workflow_return": {
                "ready": True,
                "required_artifacts": [],
                "integration_policy": "review-generated-candidates-before-copy",
            },
        }
        write_json(work_dir / "context" / "web-svg-layout-state.json", state)
        return state

    documents = [parse_svg(path) for path in svg_files]
    model = build_model(documents, args.issue_id, mode)
    state = write_artifacts(repo_root, work_dir, args.issue_id, mode, svg_files, input_source_files, svg_input_dir, input_prefix, documents, model)
    validation = validate_outputs(work_dir)
    if validation["status"] != "pass":
        raise RuntimeError(f"Generated Web SVG layout artifacts failed validation: {validation['errors']}")
    state["validation"] = validation
    write_json(output_dir / "web-svg-layout-state.json", state)
    write_json(work_dir / "context" / "web-svg-layout-state.json", state)
    return state


def run_validate(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = resolve_work_dir(repo_root, args.issue_id, args.work_dir)
    return validate_outputs(work_dir)


def add_work_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--issue-id", required=True, help="Issue/work ID such as SYS-0001, FEAT-0001, or FIX-0001.")
    parser.add_argument("--work-dir", help="Explicit work directory. Default: work/<issue-id>.")
    parser.add_argument("--repo-root", help="Workflow repository root.")
    parser.add_argument("--svg-input-dir", help="Shared SVG inbox. Default: work/requirements/svg-input.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dispatch SVG-based web layout mode as a parent-workflow extension.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-input", help="Create Web SVG inbox README.")
    init_parser.add_argument("--repo-root", help="Workflow repository root.")
    init_parser.add_argument("--svg-input-dir", help="Shared SVG inbox. Default: work/requirements/svg-input.")
    init_parser.add_argument("--force", action="store_true", help="Replace the input README.")
    init_parser.set_defaults(handler=run_init_input)

    run_parser = subparsers.add_parser("run", help="Generate web layout and browser test candidates when SVG exists.")
    add_work_arguments(run_parser)
    run_parser.add_argument(
        "--mode",
        default="auto",
        choices=["auto", "new-app", "existing-app-feature", "corrective-fix", "generic-web-ui"],
    )
    run_parser.add_argument("--force", action="store_true", help="Regenerate existing Web SVG layout outputs.")
    run_parser.add_argument(
        "--input-prefix",
        choices=["WEB_SYS", "WEB_FEAT", "WEB_FIX", "WEB", "NEXT_SYS", "NEXT_FEAT", "NEXT_FIX", "NEXT"],
        help="Override the SVG filename prefix selected from the Web mode.",
    )
    run_parser.set_defaults(handler=run_generate)

    validate_parser = subparsers.add_parser("validate", help="Validate Web SVG layout completion and generated source policies.")
    add_work_arguments(validate_parser)
    validate_parser.set_defaults(handler=run_validate)
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


