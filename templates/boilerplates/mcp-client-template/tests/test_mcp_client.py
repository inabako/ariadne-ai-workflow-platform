from __future__ import annotations

import asyncio

import pytest

from reusable_mcp_client import MCPClient, ServerDescriptor
from reusable_mcp_client.errors import SecurityPolicyError, SessionNotConnectedError
from reusable_mcp_client.transports import StdioTransport, TransportFactory, run_with_timeout


def test_connect_caches_capabilities() -> None:
    async def scenario() -> None:
        client = MCPClient()
        client.register_server(ServerDescriptor(server_id="mock"))

        result = await client.connect("mock")

        assert result["status"] == "connected"
        assert await client.list_prompts("mock") == ["summary"]
        assert await client.list_resources("mock") == ["mock://status"]
        assert await client.list_tools("mock") == ["health_check"]

    asyncio.run(scenario())


def test_operations_require_connected_session() -> None:
    async def scenario() -> None:
        client = MCPClient()
        client.register_server(ServerDescriptor(server_id="mock"))

        with pytest.raises(SessionNotConnectedError):
            await client.list_tools("mock")

    asyncio.run(scenario())


def test_prompt_resource_and_tool_calls_are_explicit() -> None:
    async def scenario() -> None:
        client = MCPClient()
        client.register_server(ServerDescriptor(server_id="mock"))
        await client.connect("mock")

        assert await client.get_prompt("mock", "summary", {"topic": "tests"}) == "Summarize tests"
        assert await client.read_resource("mock", "mock://status") == {"status": "ready"}
        assert (await client.call_tool("mock", "health_check", {"trace_id": "T1"}))["status"] == "ok"

    asyncio.run(scenario())


def test_resource_uri_is_not_local_path() -> None:
    async def scenario() -> None:
        client = MCPClient()
        client.register_server(ServerDescriptor(server_id="mock"))
        await client.connect("mock")

        with pytest.raises(SecurityPolicyError):
            await client.read_resource("mock", "file:///etc/passwd")

    asyncio.run(scenario())


def test_disconnect_invalidates_session() -> None:
    async def scenario() -> None:
        client = MCPClient()
        client.register_server(ServerDescriptor(server_id="mock"))
        await client.connect("mock")
        await client.disconnect("mock")

        with pytest.raises(SessionNotConnectedError):
            await client.list_tools("mock")

    asyncio.run(scenario())


def test_phase2_retry_audit_notification_and_secret_masking() -> None:
    async def scenario() -> None:
        client = MCPClient()
        client.register_server(ServerDescriptor(server_id="mock"))
        await client.connect("mock")
        await client.call_tool("mock", "health_check", {"token": "plain-secret", "trace_id": "T1"})
        client.handle_notification("mock", "tools/list_changed", {"reason": "test"})

        assert client.retry_policy.should_retry("timeout", attempt=1) is True
        assert client.retry_policy.should_retry("validation_error", attempt=1) is False
        assert client.audit.records[-1]["arguments"]["token"] == "***"
        assert client.notifications.events == [
            {"server_id": "mock", "event_type": "tools/list_changed", "payload": {"reason": "test"}}
        ]

    asyncio.run(scenario())


def test_phase3_transport_factory_stdio_request_and_timeout() -> None:
    transport = TransportFactory().create(ServerDescriptor(server_id="stdio-server", transport="stdio", command="python -m server"))
    assert isinstance(transport, StdioTransport)
    assert transport.build_request(7, "tools/list") == '{"id": 7, "method": "tools/list", "params": {}}'

    async def scenario() -> None:
        result = await run_with_timeout(asyncio.sleep(0, result="ok"), timeout_seconds=1)
        assert result == "ok"

    asyncio.run(scenario())
