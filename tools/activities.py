from services.strava import get_activities


def list_activities_tool(input_data: dict):
    per_page = input_data.get("per_page", 5)
    activities = get_activities(per_page)

    return [
        {
            "name": a["name"],
            "type": a.get("type", "Unknown"),
            "distance_km": round(a["distance"] / 1000, 2),
            "moving_time_min": round(a["moving_time"] / 60, 1),
            "date": a["start_date_local"][:10]
        }
        for a in activities
    ]


TOOL_DEFINITION = {
    "name": "list_activities",
    "description": "Retourne les dernières activités Strava de l'athlète.",
    "inputSchema": {                          # ← inputSchema (camelCase) pour MCP
        "type": "object",
        "properties": {
            "per_page": {
                "type": "integer",
                "description": "Nombre d'activités à retourner (défaut: 5, max: 30)",
                "default": 5
            }
        },
        "required": []
    }
}