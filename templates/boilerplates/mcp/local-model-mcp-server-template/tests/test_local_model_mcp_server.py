from __future__ import annotations

from pathlib import Path

from local_model_mcp import LocalModelMCPServer, ServerConfig
from local_model_mcp.config_loader import load_config_from_env
from local_model_mcp.ollama_adapter import OllamaAdapter
from local_model_mcp.stdio_dispatch import StdioDispatcher


def make_server(tmp_path: Path) -> LocalModelMCPServer:
    config = ServerConfig(input_root=tmp_path / "input", output_root=tmp_path / "output").resolved(tmp_path)
    return LocalModelMCPServer(config)


def test_capabilities_are_discoverable(tmp_path: Path) -> None:
    server = make_server(tmp_path)

    assert "workflow_instruction" in server.list_prompts()
    assert "model://information" in server.list_resources()
    assert "invoke_local_model" in server.list_tools()
    assert server.call_tool("health_check")["status"] == "ok"


def test_workspace_read_and_write_are_bounded(tmp_path: Path) -> None:
    server = make_server(tmp_path)
    input_file = server.config.input_root / "docs" / "note.md"
    input_file.parent.mkdir(parents=True)
    input_file.write_text("hello", encoding="utf-8")

    assert server.call_tool("read_workspace_file", {"relative_path": "docs/note.md"})["content"] == "hello"
    assert server.call_tool("read_workspace_file", {"relative_path": "../outside.txt"})["error_code"] == "security_policy_violation"

    result = server.call_tool("write_output_artifact", {"relative_path": "reports/out.md", "content": "done"})
    assert result == {"status": "ok", "relative_path": "reports/out.md"}
    assert (server.config.output_root / "reports" / "out.md").read_text(encoding="utf-8") == "done"


def test_secret_like_files_are_denied(tmp_path: Path) -> None:
    server = make_server(tmp_path)
    assert server.call_tool("read_workspace_file", {"relative_path": ".env"})["error_code"] == "security_policy_violation"


def test_model_invocation_uses_adapter(tmp_path: Path) -> None:
    server = make_server(tmp_path)
    result = server.call_tool("invoke_local_model", {"prompt": "summarize", "max_tokens": 10})

    assert result["status"] == "ok"
    assert result["model_id"] == "mock-local-model"
    assert "summarize" in result["text"]


def test_phase2_policy_audit_and_binary_rejection(tmp_path: Path) -> None:
    server = make_server(tmp_path)
    binary_file = server.config.input_root / "image.bin"
    binary_file.write_bytes(b"\x00not text")

    denied = server.call_tool("delete_file", {"relative_path": "anything"})
    binary = server.call_tool("read_workspace_file", {"relative_path": "image.bin"})
    written = server.call_tool("write_output_artifact", {"relative_path": "reports/audit.md", "content": "ok"})

    assert denied["error_code"] == "security_policy_violation"
    assert binary["error_code"] == "security_policy_violation"
    assert written["status"] == "ok"
    assert any(record["action"] == "write_output_artifact" for record in server.audit.records)


def test_phase3_env_config_ollama_request_and_stdio_dispatch(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("LOCAL_MODEL_MCP_INPUT_ROOT", "inbox")
    monkeypatch.setenv("LOCAL_MODEL_MCP_OUTPUT_ROOT", "outbox")
    monkeypatch.setenv("LOCAL_MODEL_MCP_MODEL_ID", "llama-local")
    config = load_config_from_env(tmp_path)

    assert config.input_root == (tmp_path / "inbox").resolve()
    assert config.output_root == (tmp_path / "outbox").resolve()
    assert config.model_id == "llama-local"

    request = OllamaAdapter(endpoint="http://localhost:11434/api/generate").build_request("hello", model_id="llama3")
    assert request.endpoint.endswith("/api/generate")
    assert b'"model": "llama3"' in request.body()

    server = make_server(tmp_path)
    response = StdioDispatcher(server).dispatch({"id": 1, "method": "tools/call", "params": {"name": "health_check"}})
    assert response["id"] == 1
    assert response["result"]["status"] == "ok"
