import re
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("meteofrance-mcp")

from tools.search_places import search_places_tool, TOOL_DEFINITION as PLACES_TOOL_DEF
from tools.forecast import get_forecast_tool, TOOL_DEFINITION as FORECAST_TOOL_DEF
from tools.observation import get_observation_tool, TOOL_DEFINITION as OBS_TOOL_DEF
from tools.rain import get_rain_tool, TOOL_DEFINITION as RAIN_TOOL_DEF
from tools.warnings import get_warnings_tool, TOOL_DEFINITION as WARN_TOOL_DEF
from resources.alerts import RESOURCE_DEFINITION as ALERTS_RESOURCE, read_alerts
from resources.forecast import RESOURCE_TEMPLATE as FORECAST_TEMPLATE, read_forecast
from prompts.weather_report import (
    PROMPT_DEFINITION as WEATHER_PROMPT,
    get_weather_report_messages,
)
from prompts.alert_analysis import (
    PROMPT_DEFINITION as ALERT_PROMPT,
    get_alert_analysis_messages,
)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(redirect_slashes=False)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Tools / Resources / Prompts registries
# ---------------------------------------------------------------------------

TOOLS = {
    "search_places": {"definition": PLACES_TOOL_DEF, "handler": search_places_tool},
    "get_forecast": {"definition": FORECAST_TOOL_DEF, "handler": get_forecast_tool},
    "get_observation": {"definition": OBS_TOOL_DEF, "handler": get_observation_tool},
    "get_rain": {"definition": RAIN_TOOL_DEF, "handler": get_rain_tool},
    "get_warnings": {"definition": WARN_TOOL_DEF, "handler": get_warnings_tool},
}

RESOURCES = [ALERTS_RESOURCE]
RESOURCE_TEMPLATES = [FORECAST_TEMPLATE]

FORECAST_URI_PATTERN = re.compile(
    r"^meteofrance://forecast/([-\d.]+)/([-\d.]+)$"
)


def resolve_resource(uri: str):
    if uri == ALERTS_RESOURCE["uri"]:
        return read_alerts()
    match = FORECAST_URI_PATTERN.match(uri)
    if match:
        return read_forecast(float(match.group(1)), float(match.group(2)))
    return None


PROMPTS = {
    "weather_report": {"definition": WEATHER_PROMPT, "handler": get_weather_report_messages},
    "alert_analysis": {"definition": ALERT_PROMPT, "handler": get_alert_analysis_messages},
}


# ---------------------------------------------------------------------------
# MCP Apps capability (SEP-1865) — session state
# ---------------------------------------------------------------------------

MCP_APP_MIME = "text/html;profile=mcp-app"
UI_EXTENSION_ID = "io.modelcontextprotocol/ui"

# Module-level flag: set to True after a client negotiates UI support.
# (Sufficient for single-client / demo usage. For multi-client production
# use, this should be stored per-session.)
_client_supports_ui: bool = False


def _check_client_ui_support(client_capabilities: dict) -> bool:
    """Return True if the client advertises MCP Apps support for HTML."""
    extensions = client_capabilities.get("extensions", {})
    ui_ext = extensions.get(UI_EXTENSION_ID, {})
    mime_types = ui_ext.get("mimeTypes", [])
    return MCP_APP_MIME in mime_types


# ===================================================================
# MCP Endpoints
# ===================================================================

@app.get("/.well-known/mcp/server-card")
@app.get("/.well-known/mcp/server-card/")
def server_card():
    return {
        "name": "meteofrance-mcp",
        "version": "1.0",
        "description": "MCP server for accessing Meteo-France weather data",
        "capabilities": {"tools": True, "resources": True, "prompts": True},
    }


@app.get("/.well-known/mcp/server-card/tools")
def server_card_tools():
    return {"tools": [t["definition"] for t in TOOLS.values()]}


@app.get("/")
def root_get():
    return {"protocol": "mcp", "version": "1.0", "status": "ok"}


@app.post("/")
async def rpc_handler(request: Request):
    body = await request.json()

    method = body.get("method")
    req_id = body.get("id")

    if method == "initialize":
        global _client_supports_ui
        client_params = body.get("params", {})
        client_caps = client_params.get("capabilities", {})
        _client_supports_ui = _check_client_ui_support(client_caps)
        logger.info(
            "initialize: client=%s, ui_support=%s",
            client_params.get("clientInfo", {}).get("name", "unknown"),
            _client_supports_ui,
        )

        server_caps = {
            "tools": {},
            "resources": {},
            "prompts": {},
        }
        if _client_supports_ui:
            server_caps["extensions"] = {
                UI_EXTENSION_ID: {
                    "mimeTypes": [MCP_APP_MIME],
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": server_caps,
                "serverInfo": {"name": "meteofrance-mcp", "version": "1.0"},
            },
        }

    if method == "notifications/initialized":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    # -- Tools --

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": [t["definition"] for t in TOOLS.values()]},
        }

    if method == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in TOOLS:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: '{tool_name}'"},
            }

        try:
            result = TOOLS[tool_name]["handler"](arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": str(result)}]},
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(e)},
            }

    # -- Resources --

    if method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"resources": RESOURCES},
        }

    if method == "resources/templates/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"resourceTemplates": RESOURCE_TEMPLATES},
        }

    if method == "resources/read":
        params = body.get("params", {})
        uri = params.get("uri", "")

        try:
            content = resolve_resource(uri)
            if content is None:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": f"Unknown resource: '{uri}'"},
                }
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"contents": [content]},
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(e)},
            }

    # -- Prompts --

    if method == "prompts/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"prompts": [p["definition"] for p in PROMPTS.values()]},
        }

    if method == "prompts/get":
        params = body.get("params", {})
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})

        if prompt_name not in PROMPTS:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": f"Unknown prompt: '{prompt_name}'"},
            }

        try:
            result = PROMPTS[prompt_name]["handler"](arguments)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(e)},
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: '{method}'"},
    }


@app.get("/tools")
def list_tools():
    return {"tools": [t["definition"] for t in TOOLS.values()]}


@app.post("/tools")
async def call_tool(request: Request):
    body = await request.json()
    tool_name = body.get("tool_name") or body.get("name")
    arguments = body.get("arguments") or body.get("parameters", {})

    if tool_name not in TOOLS:
        return {"error": f"Unknown tool: '{tool_name}'"}

    try:
        result = TOOLS[tool_name]["handler"](arguments)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
