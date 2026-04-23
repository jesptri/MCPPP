import json
from services.strava import get_activity

# --- MCP Prompt Definition ---
# A prompt template WITH a required argument (activity_id).
# This shows how prompts can accept parameters that change
# the generated messages.

PROMPT_DEFINITION = {
    "name": "activity_analysis",
    "description": "Analyse detaillee d'une activite Strava specifique",
    "arguments": [
        {
            "name": "activity_id",
            "description": "L'identifiant de l'activite Strava a analyser",
            "required": True
        }
    ]
}


def get_activity_analysis_messages(arguments: dict):
    """Build the prompt messages for analyzing a specific activity."""
    activity_id = arguments.get("activity_id")
    if not activity_id:
        raise ValueError("activity_id is required")

    a = get_activity(int(activity_id))

    detail = {
        "name": a.get("name"),
        "type": a.get("type"),
        "distance_km": round(a.get("distance", 0) / 1000, 2),
        "moving_time_min": round(a.get("moving_time", 0) / 60, 1),
        "elapsed_time_min": round(a.get("elapsed_time", 0) / 60, 1),
        "elevation_gain_m": a.get("total_elevation_gain"),
        "average_speed_kmh": round(a.get("average_speed", 0) * 3.6, 1),
        "max_speed_kmh": round(a.get("max_speed", 0) * 3.6, 1),
        "average_heartrate": a.get("average_heartrate"),
        "max_heartrate": a.get("max_heartrate"),
        "calories": a.get("calories"),
        "date": a.get("start_date_local"),
        "description": a.get("description"),
    }

    return {
        "description": PROMPT_DEFINITION["description"],
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Voici les donnees d'une activite Strava :\n\n"
                        f"{json.dumps(detail, indent=2)}\n\n"
                        f"Analyse cette activite en detail : performance, "
                        f"rythme, effort cardiaque (si disponible), "
                        f"et donne-moi des conseils pour m'ameliorer "
                        f"sur ce type d'activite."
                    )
                }
            }
        ]
    }
