"""Integration tests for the FastAPI MCP server -- JSON-RPC endpoints."""
import json
from unittest.mock import patch

import pytest
from httpx import AsyncClient, ASGITransport

from tests.conftest import (
    MOCK_PLACES,
    MOCK_FORECAST,
    MOCK_OBSERVATION,
    MOCK_WARNINGS,
)


def _rpc(method, params=None):
    """Build a JSON-RPC 2.0 request body."""
    body = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        body["params"] = params
    return body


# -- Server card & discovery --

@pytest.mark.anyio
async def test_server_card():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/.well-known/mcp/server-card")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "meteofrance-mcp"
    assert data["capabilities"]["tools"] is True
    assert data["capabilities"]["resources"] is True
    assert data["capabilities"]["prompts"] is True


@pytest.mark.anyio
async def test_root_get():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["protocol"] == "mcp"


# -- JSON-RPC: initialize --

@pytest.mark.anyio
async def test_rpc_initialize():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("initialize"))
    data = resp.json()
    assert data["jsonrpc"] == "2.0"
    assert data["result"]["protocolVersion"] == "2024-11-05"
    assert "tools" in data["result"]["capabilities"]
    assert "resources" in data["result"]["capabilities"]
    assert "prompts" in data["result"]["capabilities"]


@pytest.mark.anyio
async def test_rpc_notifications_initialized():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("notifications/initialized"))
    data = resp.json()
    assert "result" in data


# -- JSON-RPC: tools/list --

@pytest.mark.anyio
async def test_rpc_tools_list():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("tools/list"))
    data = resp.json()
    tools = data["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "search_places" in tool_names
    assert "get_forecast" in tool_names
    assert "get_observation" in tool_names
    assert "get_rain" in tool_names
    assert "get_warnings" in tool_names
    assert len(tools) == 5


# -- JSON-RPC: tools/call --

@pytest.mark.anyio
@patch("tools.search_places.search_places", return_value=MOCK_PLACES)
async def test_rpc_tools_call_search_places(mock):
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("tools/call", {
            "name": "search_places",
            "arguments": {"query": "Paris"}
        }))
    data = resp.json()
    assert "result" in data
    assert data["result"]["content"][0]["type"] == "text"


@pytest.mark.anyio
async def test_rpc_tools_call_unknown_tool():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("tools/call", {
            "name": "nonexistent_tool",
            "arguments": {}
        }))
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == -32601


# -- JSON-RPC: resources/list --

@pytest.mark.anyio
async def test_rpc_resources_list():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("resources/list"))
    data = resp.json()
    resources = data["result"]["resources"]
    assert len(resources) >= 1
    assert resources[0]["uri"] == "meteofrance://alerts/france"


@pytest.mark.anyio
async def test_rpc_resources_templates_list():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("resources/templates/list"))
    data = resp.json()
    templates = data["result"]["resourceTemplates"]
    assert len(templates) >= 1
    assert "latitude" in templates[0]["uriTemplate"]


# -- JSON-RPC: resources/read --

@pytest.mark.anyio
@patch("resources.alerts.get_warnings", return_value=MOCK_WARNINGS)
async def test_rpc_resources_read_alerts(mock):
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("resources/read", {
            "uri": "meteofrance://alerts/france"
        }))
    data = resp.json()
    assert "result" in data
    contents = data["result"]["contents"]
    assert len(contents) == 1
    assert contents[0]["uri"] == "meteofrance://alerts/france"
    parsed = json.loads(contents[0]["text"])
    assert parsed["domain"] == "france"


@pytest.mark.anyio
@patch("resources.forecast.get_forecast", return_value=MOCK_FORECAST)
async def test_rpc_resources_read_forecast(mock):
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("resources/read", {
            "uri": "meteofrance://forecast/48.8566/2.3522"
        }))
    data = resp.json()
    assert "result" in data
    assert data["result"]["contents"][0]["uri"] == "meteofrance://forecast/48.8566/2.3522"


@pytest.mark.anyio
async def test_rpc_resources_read_unknown_uri():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("resources/read", {
            "uri": "meteofrance://unknown/thing"
        }))
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == -32602


# -- JSON-RPC: prompts/list --

@pytest.mark.anyio
async def test_rpc_prompts_list():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("prompts/list"))
    data = resp.json()
    prompts = data["result"]["prompts"]
    prompt_names = [p["name"] for p in prompts]
    assert "weather_report" in prompt_names
    assert "alert_analysis" in prompt_names


# -- JSON-RPC: prompts/get --

@pytest.mark.anyio
@patch("prompts.alert_analysis.get_warnings", return_value=MOCK_WARNINGS)
async def test_rpc_prompts_get_alert_analysis(mock):
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("prompts/get", {
            "name": "alert_analysis",
            "arguments": {"domain": "france"}
        }))
    data = resp.json()
    assert "result" in data
    assert "messages" in data["result"]
    assert len(data["result"]["messages"]) >= 1


@pytest.mark.anyio
async def test_rpc_prompts_get_unknown():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("prompts/get", {
            "name": "nonexistent_prompt"
        }))
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == -32602


# -- JSON-RPC: unknown method --

@pytest.mark.anyio
async def test_rpc_unknown_method():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("unknown/method"))
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == -32601


# -- REST convenience endpoints --

@pytest.mark.anyio
async def test_rest_get_tools():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/tools")
    data = resp.json()
    assert "tools" in data
    assert len(data["tools"]) == 5


@pytest.mark.anyio
@patch("tools.search_places.search_places", return_value=MOCK_PLACES)
async def test_rest_post_tools(mock):
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/tools", json={
            "tool_name": "search_places",
            "arguments": {"query": "Paris"}
        })
    data = resp.json()
    assert "result" in data


@pytest.mark.anyio
async def test_rest_post_tools_unknown():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/tools", json={
            "tool_name": "fake_tool",
            "arguments": {}
        })
    data = resp.json()
    assert "error" in data
