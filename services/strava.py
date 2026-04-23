import os
import requests
from dotenv import load_dotenv

load_dotenv()

STRAVA_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
BASE_URL = "https://www.strava.com/api/v3"


def _headers():
    return {"Authorization": f"Bearer {STRAVA_TOKEN}"}


def get_activities(per_page: int = 5):
    url = f"{BASE_URL}/athlete/activities"
    response = requests.get(url, headers=_headers(), params={"per_page": per_page})

    if response.status_code != 200:
        raise Exception(f"Strava API error: {response.text}")

    return response.json()


def get_athlete():
    """Fetch the authenticated athlete's profile."""
    url = f"{BASE_URL}/athlete"
    response = requests.get(url, headers=_headers())

    if response.status_code != 200:
        raise Exception(f"Strava API error: {response.text}")

    return response.json()


def get_activity(activity_id: int):
    """Fetch a single activity by ID."""
    url = f"{BASE_URL}/activities/{activity_id}"
    response = requests.get(url, headers=_headers())

    if response.status_code != 200:
        raise Exception(f"Strava API error: {response.text}")

    return response.json()