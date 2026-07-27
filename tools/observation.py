from services.meteofrance import get_observation


def get_observation_tool(input_data: dict):
    latitude = input_data.get("latitude")
    longitude = input_data.get("longitude")
    if latitude is None or longitude is None:
        raise ValueError("latitude and longitude are required")

    return get_observation(float(latitude), float(longitude))


TOOL_DEFINITION = {
    "name": "get_observation",
    "description": (
        "Returns the most recent weather observation for a GPS position. "
        "Includes temperature, wind speed and direction, and weather description."
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
