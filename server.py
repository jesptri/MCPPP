from fastapi import FastAPI
from tools.activities import list_activities_tool, TOOL_DEFINITION

app = FastAPI()

# Registre de tools
TOOLS = {
    "list_activities": list_activities_tool
}


@app.get("/tools")
def list_tools():
    return [TOOL_DEFINITION]


@app.post("/tools/{tool_name}")
def call_tool(tool_name: str, payload: dict):
    if tool_name not in TOOLS:
        return {"error": "Tool not found"}

    try:
        result = TOOLS[tool_name](payload)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}