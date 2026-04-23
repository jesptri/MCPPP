from services.strava import get_activity_laps


def get_activity_laps_tool(input_data: dict):
    activity_id = input_data.get("activity_id")
    if not activity_id:
        raise ValueError("activity_id is required")

    laps = get_activity_laps(int(activity_id))

    return [
        {
            "lap_index": lap.get("lap_index"),
            "name": lap.get("name"),
            "distance_km": round(lap.get("distance", 0) / 1000, 2),
            "moving_time_min": round(lap.get("moving_time", 0) / 60, 1),
            "elapsed_time_min": round(lap.get("elapsed_time", 0) / 60, 1),
            "elevation_gain_m": lap.get("total_elevation_gain", 0),
            "average_speed_kmh": round(lap.get("average_speed", 0) * 3.6, 1),
            "max_speed_kmh": round(lap.get("max_speed", 0) * 3.6, 1),
            "average_watts": lap.get("average_watts"),
            "average_cadence": lap.get("average_cadence"),
        }
        for lap in laps
    ]


TOOL_DEFINITION = {
    "name": "get_activity_laps",
    "description": "Retourne les laps (tours) d'une activite Strava avec temps, distance, vitesse et puissance par lap.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "activity_id": {
                "type": "integer",
                "description": "L'identifiant de l'activite Strava"
            }
        },
        "required": ["activity_id"]
    }
}
