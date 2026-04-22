from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from tools.activities import list_activities_tool, TOOL_DEFINITION


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


@app.get("/.well-known/mcp/server-card")
@app.get("/.well-known/mcp/server-card/")
def server_card():
    return {
        "name": "strava-mcp",
        "version": "1.0",
        "description": "Serveur MCP pour accéder aux données Strava",
        "capabilities": { "tools": True, "resources": False, "prompts": False }
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
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "strava-mcp", "version": "1.0"}
            }
        }

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