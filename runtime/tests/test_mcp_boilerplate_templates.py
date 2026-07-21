from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BOILERPLATES = REPO_ROOT / "templates" / "boilerplates"


def test_mcp_layered_boilerplates_have_required_template_contract() -> None:
    expected = {
        "mcp-server-template": [
            "README.md",
            "pyproject.toml",
            "config/server.example.yaml",
            "config/capabilities.example.yaml",
            "config/prompts.example.yaml",
            "config/resources.example.yaml",
            "config/tools.example.yaml",
            "Dockerfile",
            "compose.yaml",
            "src/local_model_mcp/bootstrap.py",
            "src/local_model_mcp/server.py",
            "src/local_model_mcp/application/dto/requests.py",
            "src/local_model_mcp/application/dto/responses.py",
            "src/local_model_mcp/application/ports/inbound/use_case_port.py",
            "src/local_model_mcp/application/ports/outbound/model_port.py",
            "src/local_model_mcp/application/ports/outbound/workspace_port.py",
            "src/local_model_mcp/application/use_cases/local_model_capabilities.py",
            "src/local_model_mcp/adapters/inbound/fastmcp/server.py",
            "src/local_model_mcp/adapters/inbound/fastmcp/mappers/request_mapper.py",
            "src/local_model_mcp/adapters/inbound/fastmcp/mappers/response_mapper.py",
            "src/local_model_mcp/adapters/inbound/fastmcp/mappers/error_mapper.py",
            "src/local_model_mcp/adapters/outbound/workspace/repository.py",
            "src/local_model_mcp/tool_policy.py",
            "src/local_model_mcp/audit.py",
            "src/local_model_mcp/http_security.py",
            "src/local_model_mcp/config_loader.py",
            "src/local_model_mcp/ollama_adapter.py",
            "src/local_model_mcp/stdio_dispatch.py",
            "docs/prompt-migration-guide.md",
            "docs/security-guidelines.md",
            "docs/ollama-integration.md",
            "docs/dependency-rules.md",
            "docs/adding-a-tool.md",
            "docs/adding-an-adapter.md",
            "docs/deployment.md",
            "docs/fastmcp-adapter-separation-report.md",
            "scripts/inspect.sh",
            "tests/test_local_model_mcp_server.py",
            "scripts/run.sh",
            "scripts/run.ps1",
            "scripts/test.sh",
            "scripts/test.ps1",
            "scripts/validate.sh",
            "evidence/.gitkeep",
        ],
        "mcp-client-template": [
            "README.md",
            "pyproject.toml",
            "config/client.example.yaml",
            "config/servers.example.yaml",
            "config/retry.example.yaml",
            "config/observability.example.yaml",
            "src/reusable_mcp_client/client.py",
            "src/reusable_mcp_client/retry.py",
            "src/reusable_mcp_client/audit.py",
            "src/reusable_mcp_client/credentials.py",
            "src/reusable_mcp_client/notifications.py",
            "src/reusable_mcp_client/transports.py",
            "docs/retry-and-reconnect.md",
            "docs/security-guidelines.md",
            "docs/transport-selection.md",
            "tests/test_mcp_client.py",
            "scripts/validate.sh",
            "evidence/.gitkeep",
        ],
        "ai-agent-runtime-template": [
            "README.md",
            "pyproject.toml",
            "config/runtime.example.yaml",
            "config/mcp-servers.example.yaml",
            "config/workflows.example.yaml",
            "src/local_agent_runtime/runtime.py",
            "src/local_agent_runtime/completion.py",
            "src/local_agent_runtime/runtime_clock.py",
            "src/local_agent_runtime/retry.py",
            "src/local_agent_runtime/commands.py",
            "src/local_agent_runtime/evidence.py",
            "src/local_agent_runtime/storage.py",
            "src/local_agent_runtime/worker.py",
            "docs/checkpoint-policy.md",
            "docs/mcp-integration.md",
            "docs/storage.md",
            "docs/worker-lease.md",
            "tests/test_agent_runtime.py",
            "workflows/repository-analysis.yaml",
            "scripts/validate.sh",
            "evidence/.gitkeep",
        ],
        "discord-gateway-template": [
            "README.md",
            "pyproject.toml",
            "config/gateway.example.yaml",
            "config/discord.example.yaml",
            "config/commands.example.yaml",
            "config/authorization.example.yaml",
            "config/runtime.example.yaml",
            "config/security.example.yaml",
            "src/discord_agent_gateway/gateway.py",
            "src/discord_agent_gateway/mapping.py",
            "src/discord_agent_gateway/authorization.py",
            "src/discord_agent_gateway/runtime_client.py",
            "src/discord_agent_gateway/human_check.py",
            "src/discord_agent_gateway/state.py",
            "docs/responsibility-boundary.md",
            "docs/human-check-ui.md",
            "tests/test_discord_gateway.py",
            "scripts/register-commands.sh",
            "scripts/run-gateway.sh",
            "scripts/validate.sh",
            "evidence/.gitkeep",
        ],
    }

    missing: list[str] = []
    for template_name, relative_paths in expected.items():
        for relative_path in relative_paths:
            path = BOILERPLATES / "mcp" / template_name / relative_path
            if not path.exists():
                missing.append(str(path.relative_to(REPO_ROOT)))

    assert missing == []


def test_boilerplate_index_lists_mcp_layered_templates() -> None:
    index = (BOILERPLATES / "README.md").read_text(encoding="utf-8")
    reference = (REPO_ROOT / "docs" / "reference" / "templates.md").read_text(encoding="utf-8")

    for template_name in [
        "mcp-server-template/",
        "mcp-client-template/",
        "ai-agent-runtime-template/",
        "discord-gateway-template/",
    ]:
        assert template_name in index
        assert template_name in reference


def test_opentelemetry_collector_boilerplate_has_required_template_contract() -> None:
    template = BOILERPLATES / "infrastructure" / "opentelemetry-collector-template"
    required = [
        "README.md",
        "VERSION",
        ".env.example",
        "Makefile",
        "config/base.yaml",
        "distribution/builder-config.yaml",
        "manifests/catalog.yaml",
        "manifests/component.schema.json",
        "manifests/selection.schema.json",
        "receivers/otlp/manifest.yaml",
        "processors/memory-limiter/manifest.yaml",
        "processors/batch/manifest.yaml",
        "exporters/debug/manifest.yaml",
        "extensions/health-check/manifest.yaml",
        "examples/minimal/selection.yaml",
        "terraform/versions.tf",
        "terraform/main.tf",
        "terraform/modules/collector/main.tf",
        "scripts/otel_template.py",
        "tests/unit/test_template_contract.py",
        "docs/security.md",
    ]

    missing = [relative_path for relative_path in required if not (template / relative_path).exists()]

    assert missing == []
    base_config = (template / "config" / "base.yaml").read_text(encoding="utf-8")
    for term in ["otlp", "memory_limiter", "batch", "debug", "health_check", "pipelines"]:
        assert term in base_config
