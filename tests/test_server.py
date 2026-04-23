"""Integration tests for the FastAPI MCP server — JSON-RPC endpoints."""
import time
from unittest.mock import patch

import pytest
from httpx import AsyncClient, ASGITransport

from tests.conftest import MOCK_ACTIVITIES, MOCK_ATHLETE, MOCK_ACTIVITY


# Patch token store before importing the app to avoid real API calls on import
@pytest.fixture(autouse=True)
def patch_token():
    with patch("services.strava._token_store", {
        "access_token": "test_token",
        "refresh_token": "test_refresh",
        "expires_at": int(time.time()) + 3600,
        "client_id": "test_id",
        "client_secret": "test_secret",
    }):
        yield


def _rpc(method, params=None):
    """Build a JSON-RPC 2.0 request body."""
    body = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        body["params"] = params
    return body


# ── Server card & discovery ──

@pytest.mark.anyio
async def test_server_card():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/.well-known/mcp/server-card")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "strava-mcp"
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


# ── JSON-RPC: initialize ──

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


# ── JSON-RPC: tools/list ──

@pytest.mark.anyio
async def test_rpc_tools_list():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("tools/list"))
    data = resp.json()
    tools = data["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "list_activities" in tool_names
    assert "get_athlete_stats" in tool_names
    assert "get_activity_laps" in tool_names
    assert "get_activity_zones" in tool_names
    assert "get_athlete_clubs" in tool_names
    assert "explore_segments" in tool_names
    assert len(tools) == 6


# ── JSON-RPC: tools/call ──

@pytest.mark.anyio
@patch("tools.activities.get_activities", return_value=MOCK_ACTIVITIES)
async def test_rpc_tools_call_list_activities(mock):
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("tools/call", {
            "name": "list_activities",
            "arguments": {"per_page": 2}
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


# ── JSON-RPC: resources/list ──

@pytest.mark.anyio
async def test_rpc_resources_list():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("resources/list"))
    data = resp.json()
    resources = data["result"]["resources"]
    assert len(resources) >= 1
    assert resources[0]["uri"] == "strava://athlete/profile"


@pytest.mark.anyio
async def test_rpc_resources_templates_list():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("resources/templates/list"))
    data = resp.json()
    templates = data["result"]["resourceTemplates"]
    assert len(templates) >= 1
    assert "activity_id" in templates[0]["uriTemplate"]


# ── JSON-RPC: resources/read ──

@pytest.mark.anyio
@patch("resources.athlete.get_athlete", return_value=MOCK_ATHLETE)
async def test_rpc_resources_read_athlete(mock):
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("resources/read", {
            "uri": "strava://athlete/profile"
        }))
    data = resp.json()
    assert "result" in data
    contents = data["result"]["contents"]
    assert len(contents) == 1
    assert contents[0]["uri"] == "strava://athlete/profile"


@pytest.mark.anyio
@patch("resources.activity.get_activity", return_value=MOCK_ACTIVITY)
async def test_rpc_resources_read_activity(mock):
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("resources/read", {
            "uri": "strava://activities/99001"
        }))
    data = resp.json()
    assert "result" in data
    assert data["result"]["contents"][0]["uri"] == "strava://activities/99001"


@pytest.mark.anyio
async def test_rpc_resources_read_unknown_uri():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("resources/read", {
            "uri": "strava://unknown/thing"
        }))
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == -32602


# ── JSON-RPC: prompts/list ──

@pytest.mark.anyio
async def test_rpc_prompts_list():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("prompts/list"))
    data = resp.json()
    prompts = data["result"]["prompts"]
    prompt_names = [p["name"] for p in prompts]
    assert "weekly_summary" in prompt_names
    assert "activity_analysis" in prompt_names


# ── JSON-RPC: prompts/get ──

@pytest.mark.anyio
@patch("prompts.weekly_summary.get_activities", return_value=MOCK_ACTIVITIES)
async def test_rpc_prompts_get_weekly_summary(mock):
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("prompts/get", {
            "name": "weekly_summary"
        }))
    data = resp.json()
    assert "result" in data
    assert "messages" in data["result"]
    assert len(data["result"]["messages"]) >= 1


@pytest.mark.anyio
@patch("prompts.activity_analysis.get_activity", return_value=MOCK_ACTIVITY)
async def test_rpc_prompts_get_activity_analysis(mock):
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("prompts/get", {
            "name": "activity_analysis",
            "arguments": {"activity_id": "99001"}
        }))
    data = resp.json()
    assert "result" in data
    assert "messages" in data["result"]


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


# ── JSON-RPC: unknown method ──

@pytest.mark.anyio
async def test_rpc_unknown_method():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/", json=_rpc("unknown/method"))
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == -32601


# ── REST convenience endpoints ──

@pytest.mark.anyio
async def test_rest_get_tools():
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/tools")
    data = resp.json()
    assert "tools" in data
    assert len(data["tools"]) == 6


@pytest.mark.anyio
@patch("tools.activities.get_activities", return_value=MOCK_ACTIVITIES)
async def test_rest_post_tools(mock):
    from server import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/tools", json={
            "tool_name": "list_activities",
            "arguments": {"per_page": 2}
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
