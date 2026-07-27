from services.meteofrance import get_forecast


def get_forecast_tool(input_data: dict):
    latitude = input_data.get("latitude")
    longitude = input_data.get("longitude")
    if latitude is None or longitude is None:
        raise ValueError("latitude and longitude are required")

    return get_forecast(float(latitude), float(longitude))


TOOL_DEFINITION = {
    "name": "get_forecast",
    "description": (
        "Returns the weather forecast (hourly and daily) "
        "for a given GPS position. Includes temperature, wind, "
        "precipitation and event probabilities."
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
