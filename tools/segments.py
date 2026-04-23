from services.strava import explore_segments


def explore_segments_tool(input_data: dict):
    bounds = input_data.get("bounds")
    if not bounds:
        raise ValueError("bounds is required (format: south_lat,west_lng,north_lat,east_lng)")

    activity_type = input_data.get("activity_type", "riding")
    data = explore_segments(bounds, activity_type)

    segments = data.get("segments", [])
    return [
        {
            "id": s.get("id"),
            "name": s.get("name"),
            "climb_category": s.get("climb_category"),
            "avg_grade": s.get("avg_grade"),
            "distance_km": round(s.get("distance", 0) / 1000, 2),
            "elev_difference_m": s.get("elev_difference"),
            "start_latlng": s.get("start_latlng"),
            "end_latlng": s.get("end_latlng"),
        }
        for s in segments
    ]


TOOL_DEFINITION = {
    "name": "explore_segments",
    "description": "Explore les segments Strava dans une zone geographique donnee. Utile pour decouvrir des parcours populaires.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "bounds": {
                "type": "string",
                "description": "Coordonnees de la zone : sud_lat,ouest_lng,nord_lat,est_lng (ex: 48.8,2.3,48.9,2.4 pour Paris)"
            },
            "activity_type": {
                "type": "string",
                "enum": ["riding", "running"],
                "description": "Type d'activite (defaut: riding)",
                "default": "riding"
            }
        },
        "required": ["bounds"]
    }
}
