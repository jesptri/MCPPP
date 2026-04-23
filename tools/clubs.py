from services.strava import get_athlete_clubs


def get_athlete_clubs_tool(input_data: dict):
    per_page = input_data.get("per_page", 30)
    clubs = get_athlete_clubs(per_page)

    return [
        {
            "id": c.get("id"),
            "name": c.get("name"),
            "sport_type": c.get("sport_type"),
            "city": c.get("city"),
            "state": c.get("state"),
            "country": c.get("country"),
            "member_count": c.get("member_count"),
            "private": c.get("private"),
            "url": c.get("url"),
        }
        for c in clubs
    ]


TOOL_DEFINITION = {
    "name": "get_athlete_clubs",
    "description": "Retourne la liste des clubs auxquels l'athlete connecte appartient.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "per_page": {
                "type": "integer",
                "description": "Nombre de clubs a retourner (defaut: 30)",
                "default": 30
            }
        },
        "required": []
    }
}
