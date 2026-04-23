from services.strava import get_activity_zones


def get_activity_zones_tool(input_data: dict):
    activity_id = input_data.get("activity_id")
    if not activity_id:
        raise ValueError("activity_id is required")

    zones = get_activity_zones(int(activity_id))

    result = []
    for zone in zones:
        buckets = zone.get("distribution_buckets", [])
        result.append({
            "type": zone.get("type"),
            "sensor_based": zone.get("sensor_based"),
            "points": zone.get("points"),
            "buckets": [
                {
                    "min": b.get("min"),
                    "max": b.get("max"),
                    "time_seconds": b.get("time"),
                }
                for b in buckets
            ] if isinstance(buckets, list) else []
        })

    return result


TOOL_DEFINITION = {
    "name": "get_activity_zones",
    "description": "Retourne la distribution des zones cardio et/ou puissance pour une activite (necessite Strava Summit).",
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
