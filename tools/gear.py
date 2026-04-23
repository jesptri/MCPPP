from services.strava import get_gear


def get_gear_tool(input_data: dict):
    gear_id = input_data.get("gear_id")
    if not gear_id:
        raise ValueError("gear_id is required (e.g. 'b12345' for a bike, 'g12345' for shoes)")

    g = get_gear(str(gear_id))

    return {
        "id": g.get("id"),
        "name": g.get("name"),
        "primary": g.get("primary"),
        "brand_name": g.get("brand_name"),
        "model_name": g.get("model_name"),
        "description": g.get("description"),
        "distance_km": round(g.get("distance", 0) / 1000, 2),
        "frame_type": g.get("frame_type"),
        "weight_kg": g.get("weight"),
    }


TOOL_DEFINITION = {
    "name": "get_gear",
    "description": "Retourne les details d'un equipement Strava (velo, chaussures) par son identifiant.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "gear_id": {
                "type": "string",
                "description": "Identifiant de l'equipement (ex: 'b12345' pour un velo, 'g12345' pour des chaussures)"
            }
        },
        "required": ["gear_id"]
    }
}
