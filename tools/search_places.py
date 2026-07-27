from services.meteofrance import search_places


def search_places_tool(input_data: dict):
    query = input_data.get("query")
    if not query:
        raise ValueError("query is required")

    latitude = input_data.get("latitude")
    longitude = input_data.get("longitude")

    return search_places(query, latitude=latitude, longitude=longitude)


TOOL_DEFINITION = {
    "name": "search_places",
    "description": (
        "Search for places (cities) by name or postal code. "
        "Returns GPS coordinates, department and INSEE code."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "City name or postal code (e.g. 'Paris', '75001')",
            },
            "latitude": {
                "type": "number",
                "description": "Reference latitude to sort results by proximity (optional)",
            },
            "longitude": {
                "type": "number",
                "description": "Reference longitude to sort results by proximity (optional)",
            },
        },
        "required": ["query"],
    },
}
