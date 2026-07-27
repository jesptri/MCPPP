from services.meteofrance import get_warnings


def get_warnings_tool(input_data: dict):
    domain = input_data.get("domain", "france")
    return get_warnings(domain=domain)


TOOL_DEFINITION = {
    "name": "get_warnings",
    "description": (
        "Returns current weather alerts (vigilance) for France "
        "or a specific department. Shows alert level per "
        "phenomenon: wind, rain, thunderstorms, snow, heatwave, etc."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": (
                    "Vigilance domain: 'france' for national level, "
                    "or a 2-digit department number (e.g. '75' for Paris, '33' for Gironde)"
                ),
                "default": "france",
            }
        },
        "required": [],
    },
}
