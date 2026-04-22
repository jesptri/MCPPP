from services.strava import get_activities


def list_activities_tool(input_data: dict):
    per_page = input_data.get("per_page", 5)

    activities = get_activities(per_page)

    # Optionnel : simplifier la réponse
    return [
        {
            "name": a["name"],
            "distance_km": round(a["distance"] / 1000, 2),
            "moving_time_min": round(a["moving_time"] / 60, 1)
        }
        for a in activities
    ]


TOOL_DEFINITION = {
    "name": "list_activities",
    "description": "Retourne les dernières activités Strava",
    "input_schema": {
        "type": "object",
        "properties": {
            "per_page": {"type": "number"}
        }
    }
}