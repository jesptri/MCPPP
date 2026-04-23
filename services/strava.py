import os
import time
import requests
from dotenv import load_dotenv, set_key

ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(ENV_PATH)

BASE_URL = "https://www.strava.com/api/v3"
TOKEN_URL = "https://www.strava.com/oauth/token"


# Scopes needed for this MCP server
STRAVA_SCOPES = "read,activity:read_all,profile:read_all"
AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"

_token_store = {
    "access_token": os.getenv("STRAVA_ACCESS_TOKEN", ""),
    "refresh_token": os.getenv("STRAVA_REFRESH_TOKEN", ""),
    "expires_at": int(os.getenv("STRAVA_EXPIRES_AT", "0")),
    "client_id": os.getenv("STRAVA_CLIENT_ID", ""),
    "client_secret": os.getenv("STRAVA_CLIENT_SECRET", ""),
}


def _refresh_token():
    """Exchange the refresh token for a new access token via Strava OAuth."""
    response = requests.post(TOKEN_URL, data={
        "client_id": _token_store["client_id"],
        "client_secret": _token_store["client_secret"],
        "grant_type": "refresh_token",
        "refresh_token": _token_store["refresh_token"],
    })

    if response.status_code != 200:
        raise Exception(f"Token refresh failed: {response.text}")

    data = response.json()
    _token_store["access_token"] = data["access_token"]
    _token_store["refresh_token"] = data["refresh_token"]
    _token_store["expires_at"] = data["expires_at"]

    # Persist to .env so tokens survive restarts
    abs_env = os.path.abspath(ENV_PATH)
    set_key(abs_env, "STRAVA_ACCESS_TOKEN", data["access_token"])
    set_key(abs_env, "STRAVA_REFRESH_TOKEN", data["refresh_token"])
    set_key(abs_env, "STRAVA_EXPIRES_AT", str(data["expires_at"]))


def _get_access_token():
    """Return a valid access token, refreshing if expired."""
    # Refresh 60s before actual expiry to avoid race conditions
    if time.time() >= (_token_store["expires_at"] - 60):
        _refresh_token()
    return _token_store["access_token"]


def get_authorize_url(redirect_uri: str) -> str:
    """Build the Strava OAuth authorization URL with required scopes."""
    return (
        f"{AUTHORIZE_URL}"
        f"?client_id={_token_store['client_id']}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope={STRAVA_SCOPES}"
        f"&approval_prompt=force"
    )


def exchange_code(code: str):
    """Exchange an authorization code for tokens and persist them."""
    response = requests.post(TOKEN_URL, data={
        "client_id": _token_store["client_id"],
        "client_secret": _token_store["client_secret"],
        "code": code,
        "grant_type": "authorization_code",
    })

    if response.status_code != 200:
        raise Exception(f"Code exchange failed: {response.text}")

    data = response.json()
    _token_store["access_token"] = data["access_token"]
    _token_store["refresh_token"] = data["refresh_token"]
    _token_store["expires_at"] = data["expires_at"]

    abs_env = os.path.abspath(ENV_PATH)
    set_key(abs_env, "STRAVA_ACCESS_TOKEN", data["access_token"])
    set_key(abs_env, "STRAVA_REFRESH_TOKEN", data["refresh_token"])
    set_key(abs_env, "STRAVA_EXPIRES_AT", str(data["expires_at"]))

    return data


def _headers():
    return {"Authorization": f"Bearer {_get_access_token()}"}


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


def get_athlete_stats(athlete_id: int):
    """Fetch all-time, YTD, and recent activity stats for an athlete."""
    url = f"{BASE_URL}/athletes/{athlete_id}/stats"
    response = requests.get(url, headers=_headers())

    if response.status_code != 200:
        raise Exception(f"Strava API error: {response.text}")

    return response.json()


def get_activity_laps(activity_id: int):
    """Fetch laps for an activity."""
    url = f"{BASE_URL}/activities/{activity_id}/laps"
    response = requests.get(url, headers=_headers())

    if response.status_code != 200:
        raise Exception(f"Strava API error: {response.text}")

    return response.json()


def get_activity_zones(activity_id: int):
    """Fetch HR/power zone distribution for an activity."""
    url = f"{BASE_URL}/activities/{activity_id}/zones"
    response = requests.get(url, headers=_headers())

    if response.status_code != 200:
        raise Exception(f"Strava API error: {response.text}")

    return response.json()


def get_athlete_clubs(per_page: int = 30):
    """Fetch clubs the authenticated athlete belongs to."""
    url = f"{BASE_URL}/athlete/clubs"
    response = requests.get(url, headers=_headers(), params={"per_page": per_page})

    if response.status_code != 200:
        raise Exception(f"Strava API error: {response.text}")

    return response.json()


def explore_segments(bounds: str, activity_type: str = "riding"):
    """Explore segments in a geographic area.

    Args:
        bounds: comma-separated: south_lat,west_lng,north_lat,east_lng
        activity_type: 'riding' or 'running'
    """
    url = f"{BASE_URL}/segments/explore"
    response = requests.get(url, headers=_headers(), params={
        "bounds": bounds,
        "activity_type": activity_type,
    })

    if response.status_code != 200:
        raise Exception(f"Strava API error: {response.text}")

    return response.json()