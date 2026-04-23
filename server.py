import re

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from tools.activities import list_activities_tool, TOOL_DEFINITION
from tools.stats import get_athlete_stats_tool, TOOL_DEFINITION as STATS_TOOL_DEF
from tools.laps import get_activity_laps_tool, TOOL_DEFINITION as LAPS_TOOL_DEF
from tools.zones import get_activity_zones_tool, TOOL_DEFINITION as ZONES_TOOL_DEF
from tools.clubs import get_athlete_clubs_tool, TOOL_DEFINITION as CLUBS_TOOL_DEF
from tools.segments import explore_segments_tool, TOOL_DEFINITION as SEGMENTS_TOOL_DEF
from services.strava import get_authorize_url, exchange_code
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
    },
    "get_athlete_stats": {
        "definition": STATS_TOOL_DEF,
        "handler": get_athlete_stats_tool
    },
    "get_activity_laps": {
        "definition": LAPS_TOOL_DEF,
        "handler": get_activity_laps_tool
    },
    "get_activity_zones": {
        "definition": ZONES_TOOL_DEF,
        "handler": get_activity_zones_tool
    },
    "get_athlete_clubs": {
        "definition": CLUBS_TOOL_DEF,
        "handler": get_athlete_clubs_tool
    },
    "explore_segments": {
        "definition": SEGMENTS_TOOL_DEF,
        "handler": explore_segments_tool
    },
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


# ── OAuth Authorization Flow ──
# 1. Visit /auth         → redirects to Strava with correct scopes
# 2. User approves       → Strava redirects to /auth/callback?code=...
# 3. Server exchanges code for tokens and persists them

@app.get("/auth")
def auth_redirect(request: Request):
    """Redirect to Strava OAuth with the required scopes."""
    callback_url = str(request.url_for("auth_callback"))
    return RedirectResponse(get_authorize_url(callback_url))


@app.get("/auth/callback")
def auth_callback(code: str = "", error: str = ""):
    """Handle the OAuth callback from Strava."""
    if error:
        return HTMLResponse(f"<h2>Authorization denied</h2><p>{error}</p>", status_code=400)

    if not code:
        return HTMLResponse("<h2>Missing authorization code</h2>", status_code=400)

    try:
        data = exchange_code(code)
        athlete = data.get("athlete", {})
        name = f"{athlete.get('firstname', '')} {athlete.get('lastname', '')}".strip()
        return HTMLResponse(
            f"<h2>Authorization successful</h2>"
            f"<p>Athlete: {name or 'OK'}</p>"
            f"<p>Scopes granted. Tokens saved to .env.</p>"
            f"<p>You can close this page and use the MCP server.</p>"
        )
    except Exception as e:
        return HTMLResponse(f"<h2>Token exchange failed</h2><pre>{e}</pre>", status_code=500)


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