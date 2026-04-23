import json
from services.strava import get_activities

# --- MCP Prompt Definition ---
# A prompt template with no required arguments.
# The server fetches the data and builds a message array for the LLM.
# The client calls prompts/get and receives pre-built messages it can
# feed directly to the model.

PROMPT_DEFINITION = {
    "name": "weekly_summary",
    "description": "Genere un resume et une analyse des activites Strava de la semaine",
    "arguments": []
}


def get_weekly_summary_messages(arguments: dict):
    """Build the prompt messages for a weekly activity summary."""
    activities = get_activities(per_page=20)

    # Filter to last 7 days
    from datetime import datetime, timedelta
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
    recent = [
        a for a in activities
        if a.get("start_date_local", "") >= cutoff
    ]

    summary_data = [
        {
            "name": a["name"],
            "type": a.get("type", "Unknown"),
            "distance_km": round(a["distance"] / 1000, 2),
            "moving_time_min": round(a["moving_time"] / 60, 1),
            "elevation_gain_m": a.get("total_elevation_gain", 0),
            "date": a["start_date_local"][:10]
        }
        for a in recent
    ]

    return {
        "description": PROMPT_DEFINITION["description"],
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Voici mes activites Strava des 7 derniers jours :\n\n"
                        f"{json.dumps(summary_data, indent=2)}\n\n"
                        f"Fais-moi un resume complet : nombre total d'activites, "
                        f"distance totale, temps total, denivelé total. "
                        f"Puis donne-moi une analyse de ma semaine d'entrainement "
                        f"avec des conseils pour la semaine prochaine."
                    )
                }
            }
        ]
    }
