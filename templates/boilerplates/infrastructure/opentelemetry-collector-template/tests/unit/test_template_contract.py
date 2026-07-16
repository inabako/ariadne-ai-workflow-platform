from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_required_template_files_exist() -> None:
    required = [
        "README.md",
        "VERSION",
        ".env.example",
        "Makefile",
        "config/base.yaml",
        "manifests/catalog.yaml",
        "distribution/builder-config.yaml",
        "terraform/versions.tf",
        "terraform/main.tf",
        "examples/minimal/selection.yaml",
        "scripts/otel_template.py",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert missing == []


def test_minimal_collector_config_enables_components() -> None:
    config = (ROOT / "config" / "base.yaml").read_text(encoding="utf-8")
    for term in ["otlp", "memory_limiter", "batch", "debug", "health_check", "pipelines"]:
        assert term in config
