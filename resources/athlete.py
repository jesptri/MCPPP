import json
from services.strava import get_athlete

RESOURCE_DEFINITION = {
    "uri": "strava://athlete/profile",
    "name": "Athlete Profile",
    "description": "Profil de l'athlete Strava connecte (nom, ville, stats, etc.)",
    "mimeType": "application/json"
}


def read_athlete_profile():
    """Called when the client does resources/read with uri=strava://athlete/profile."""
    athlete = get_athlete()
    profile = {
        "id": athlete.get("id"),
        "firstname": athlete.get("firstname"),
        "lastname": athlete.get("lastname"),
        "city": athlete.get("city"),
        "country": athlete.get("country"),
        "sex": athlete.get("sex"),
        "weight": athlete.get("weight"),
        "profile_picture": athlete.get("profile"),
        "follower_count": athlete.get("follower_count"),
        "friend_count": athlete.get("friend_count"),
        "bikes": [
            {"id": b["id"], "name": b["name"], "distance_km": round(b.get("distance", 0) / 1000, 2)}
            for b in athlete.get("bikes", [])
        ],
        "shoes": [
            {"id": s["id"], "name": s["name"], "distance_km": round(s.get("distance", 0) / 1000, 2)}
            for s in athlete.get("shoes", [])
        ],
    }
    return {
        "uri": RESOURCE_DEFINITION["uri"],
        "mimeType": "application/json",
        "text": json.dumps(profile, indent=2)
    }
