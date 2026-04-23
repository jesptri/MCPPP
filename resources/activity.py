import json
from services.strava import get_activity

RESOURCE_TEMPLATE = {
    "uriTemplate": "strava://activities/{activity_id}",
    "name": "Activity Detail",
    "description": "Detail complet d'une activite Strava par son ID",
    "mimeType": "application/json"
}


def read_activity(activity_id: int):
    """Called when the client does resources/read with uri=strava://activities/<id>."""
    a = get_activity(activity_id)
    detail = {
        "id": a.get("id"),
        "name": a.get("name"),
        "type": a.get("type"),
        "sport_type": a.get("sport_type"),
        "distance_km": round(a.get("distance", 0) / 1000, 2),
        "moving_time_min": round(a.get("moving_time", 0) / 60, 1),
        "elapsed_time_min": round(a.get("elapsed_time", 0) / 60, 1),
        "total_elevation_gain_m": a.get("total_elevation_gain"),
        "average_speed_kmh": round(a.get("average_speed", 0) * 3.6, 1),
        "max_speed_kmh": round(a.get("max_speed", 0) * 3.6, 1),
        "average_heartrate": a.get("average_heartrate"),
        "max_heartrate": a.get("max_heartrate"),
        "calories": a.get("calories"),
        "start_date": a.get("start_date_local"),
        "description": a.get("description"),
        "kudos_count": a.get("kudos_count"),
        "gear_id": a.get("gear_id"),
    }
    return {
        "uri": f"strava://activities/{activity_id}",
        "mimeType": "application/json",
        "text": json.dumps(detail, indent=2)
    }
