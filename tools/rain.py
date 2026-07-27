from services.meteofrance import get_rain


def get_rain_tool(input_data: dict):
    latitude = input_data.get("latitude")
    longitude = input_data.get("longitude")
    if latitude is None or longitude is None:
        raise ValueError("latitude and longitude are required")

    return get_rain(float(latitude), float(longitude))


TOOL_DEFINITION = {
    "name": "get_rain",
    "description": (
        "Returns the rain forecast for the next hour "
        "at a GPS position (available in metropolitan France). "
        "Indicates when the next rain is expected."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "latitude": {
                "type": "number",
                "description": "Latitude in degrees (e.g. 48.8566 for Paris)",
            },
            "longitude": {
                "type": "number",
                "description": "Longitude in degrees (e.g. 2.3522 for Paris)",
            },
        },
        "required": ["latitude", "longitude"],
    },
}
