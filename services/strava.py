import os
import requests
from dotenv import load_dotenv

load_dotenv()

STRAVA_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")

BASE_URL = "https://www.strava.com/api/v3"


def get_activities(per_page: int = 5):
    url = f"{BASE_URL}/athlete/activities"

    headers = {
        "Authorization": f"Bearer {STRAVA_TOKEN}"
    }

    params = {
        "per_page": per_page
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Strava API error: {response.text}")

    return response.json()