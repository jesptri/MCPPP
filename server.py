import re

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from tools.activities import list_activities_tool, TOOL_DEFINITION
from resources.athlete import RESOURCE_DEFINITION as ATHLETE_RESOURCE, read_athlete_profile
from resources.activity import RESOURCE_TEMPLATE as ACTIVITY_TEMPLATE, read_activity
from prompts.weekly_summary import (
    PROMPT_DEFINITION as WEEKLY_PROMPT,
    get_weekly_summary_messages,
)
from prompts.activity_analysis import (
    PROMPT_DEFINITION as ACTIVITY_PROMPT,
    get_activity_analysis_messages,
)


class NgrokMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["ngrok-skip-browser-warning"] = "true"
        return response


app = FastAPI(redirect_slashes=False)
app.add_middleware(NgrokMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


TOOLS = {
    "list_activities": {
        "definition": TOOL_DEFINITION,
        "handler": list_activities_tool
    }
}

# --- Resources ---
# Static resources have a fixed URI; templates have a uriTemplate with placeholders.
RESOURCES = [ATHLETE_RESOURCE]
RESOURCE_TEMPLATES = [ACTIVITY_TEMPLATE]

# URI pattern for matching strava://activities/{id}
ACTIVITY_URI_PATTERN = re.compile(r"^strava://activities/(\d+)$")


def resolve_resource(uri: str):
    """Route a resource URI to the correct handler."""
    if uri == ATHLETE_RESOURCE["uri"]:
        return read_athlete_profile()

    match = ACTIVITY_URI_PATTERN.match(uri)
    if match:
        return read_activity(int(match.group(1)))

    return None


# --- Prompts ---
PROMPTS = {
    "weekly_summary": {
        "definition": WEEKLY_PROMPT,
        "handler": get_weekly_summary_messages,
    },
    "activity_analysis": {
        "definition": ACTIVITY_PROMPT,
        "handler": get_activity_analysis_messages,
    },
}


@app.get("/.well-known/mcp/server-card")
@app.get("/.well-known/mcp/server-card/")
def server_card():
    return {
        "name": "strava-mcp",
        "version": "1.0",
        "description": "Serveur MCP pour accéder aux données Strava",
        "capabilities": { "tools": True, "resources": True, "prompts": True }
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
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {},
                },
                "serverInfo": {"name": "strava-mcp", "version": "2.0"}
            }
        }

    # ── Notifications (no response expected) ──
    if method == "notifications/initialized":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    # ── Tools ──

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [t["definition"] for t in TOOLS.values()]
            }
        }

    if method == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in TOOLS:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Outil inconnu : '{tool_name}'"}
            }

        try:
            result = TOOLS[tool_name]["handler"](arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": str(result)}]}
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(e)}
            }

    # ── Resources ──

    if method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"resources": RESOURCES}
        }

    if method == "resources/templates/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"resourceTemplates": RESOURCE_TEMPLATES}
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
                    "error": {"code": -32602, "message": f"Ressource inconnue : '{uri}'"}
                }
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"contents": [content]}
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(e)}
            }

    # ── Prompts ──

    if method == "prompts/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "prompts": [p["definition"] for p in PROMPTS.values()]
            }
        }

    if method == "prompts/get":
        params = body.get("params", {})
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})

        if prompt_name not in PROMPTS:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": f"Prompt inconnu : '{prompt_name}'"}
            }

        try:
            result = PROMPTS[prompt_name]["handler"](arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(e)}
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Méthode inconnue : '{method}'"}
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
        return {"error": f"Outil inconnu : '{tool_name}'"}

    try:
        result = TOOLS[tool_name]["handler"](arguments)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}