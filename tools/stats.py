from services.strava import get_athlete_stats, get_athlete


def get_athlete_stats_tool(input_data: dict):
    # Stats endpoint requires the athlete ID — fetch it automatically if not provided
    athlete_id = input_data.get("athlete_id")
    if not athlete_id:
        athlete = get_athlete()
        athlete_id = athlete["id"]

    stats = get_athlete_stats(int(athlete_id))

    def format_totals(totals):
        return {
            "count": totals.get("count", 0),
            "distance_km": round(totals.get("distance", 0) / 1000, 2),
            "moving_time_hours": round(totals.get("moving_time", 0) / 3600, 1),
            "elevation_gain_m": round(totals.get("elevation_gain", 0), 1),
        }

    return {
        "biggest_ride_distance_km": round(stats.get("biggest_ride_distance", 0) / 1000, 2),
        "biggest_climb_elevation_gain_m": round(stats.get("biggest_climb_elevation_gain", 0), 1),
        "recent_ride_totals": format_totals(stats.get("recent_ride_totals", {})),
        "recent_run_totals": format_totals(stats.get("recent_run_totals", {})),
        "recent_swim_totals": format_totals(stats.get("recent_swim_totals", {})),
        "ytd_ride_totals": format_totals(stats.get("ytd_ride_totals", {})),
        "ytd_run_totals": format_totals(stats.get("ytd_run_totals", {})),
        "ytd_swim_totals": format_totals(stats.get("ytd_swim_totals", {})),
        "all_ride_totals": format_totals(stats.get("all_ride_totals", {})),
        "all_run_totals": format_totals(stats.get("all_run_totals", {})),
        "all_swim_totals": format_totals(stats.get("all_swim_totals", {})),
    }


TOOL_DEFINITION = {
    "name": "get_athlete_stats",
    "description": "Retourne les statistiques de l'athlete : totaux recents, YTD et all-time pour velo, course et natation.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "athlete_id": {
                "type": "integer",
                "description": "ID de l'athlete (optionnel, utilise l'athlete connecte par defaut)"
            }
        },
        "required": []
    }
}
