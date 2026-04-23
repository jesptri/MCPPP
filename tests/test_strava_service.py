"""Unit tests for services/strava.py — all API calls mocked."""
import time
from unittest.mock import patch, MagicMock

import pytest

from tests.conftest import (
    MockResponse,
    MOCK_ATHLETE,
    MOCK_ACTIVITIES,
    MOCK_ACTIVITY,
    MOCK_STATS,
    MOCK_LAPS,
    MOCK_ZONES,
    MOCK_CLUBS,
    MOCK_SEGMENTS_RESPONSE,
    MOCK_TOKEN_RESPONSE,
)


# Force a valid token so _get_access_token() doesn't trigger a refresh
@pytest.fixture(autouse=True)
def patch_token_store():
    with patch("services.strava._token_store", {
        "access_token": "test_token",
        "refresh_token": "test_refresh",
        "expires_at": int(time.time()) + 3600,
        "client_id": "test_id",
        "client_secret": "test_secret",
    }):
        yield


# ── get_activities ──

@patch("services.strava.requests.get")
def test_get_activities_success(mock_get):
    from services.strava import get_activities

    mock_get.return_value = MockResponse(MOCK_ACTIVITIES)
    result = get_activities(per_page=2)

    assert len(result) == 2
    assert result[0]["name"] == "Morning Run"
    mock_get.assert_called_once()
    assert "per_page" in str(mock_get.call_args)


@patch("services.strava.requests.get")
def test_get_activities_api_error(mock_get):
    from services.strava import get_activities

    mock_get.return_value = MockResponse({"message": "Unauthorized"}, status_code=401)

    with pytest.raises(Exception, match="Strava API error"):
        get_activities()


# ── get_athlete ──

@patch("services.strava.requests.get")
def test_get_athlete_success(mock_get):
    from services.strava import get_athlete

    mock_get.return_value = MockResponse(MOCK_ATHLETE)
    result = get_athlete()

    assert result["id"] == 123456
    assert result["firstname"] == "Jules"


@patch("services.strava.requests.get")
def test_get_athlete_api_error(mock_get):
    from services.strava import get_athlete

    mock_get.return_value = MockResponse({"message": "Forbidden"}, status_code=403)

    with pytest.raises(Exception, match="Strava API error"):
        get_athlete()


# ── get_activity ──

@patch("services.strava.requests.get")
def test_get_activity_success(mock_get):
    from services.strava import get_activity

    mock_get.return_value = MockResponse(MOCK_ACTIVITY)
    result = get_activity(99001)

    assert result["id"] == 99001
    assert result["name"] == "Morning Run"
    assert "activities/99001" in str(mock_get.call_args)


@patch("services.strava.requests.get")
def test_get_activity_not_found(mock_get):
    from services.strava import get_activity

    mock_get.return_value = MockResponse({"message": "Not Found"}, status_code=404)

    with pytest.raises(Exception, match="Strava API error"):
        get_activity(999999)


# ── get_athlete_stats ──

@patch("services.strava.requests.get")
def test_get_athlete_stats_success(mock_get):
    from services.strava import get_athlete_stats

    mock_get.return_value = MockResponse(MOCK_STATS)
    result = get_athlete_stats(123456)

    assert result["biggest_ride_distance"] == 120000.0
    assert result["recent_ride_totals"]["count"] == 3
    assert "athletes/123456/stats" in str(mock_get.call_args)


@patch("services.strava.requests.get")
def test_get_athlete_stats_error(mock_get):
    from services.strava import get_athlete_stats

    mock_get.return_value = MockResponse({"message": "Unauthorized"}, status_code=401)

    with pytest.raises(Exception, match="Strava API error"):
        get_athlete_stats(123456)


# ── get_activity_laps ──

@patch("services.strava.requests.get")
def test_get_activity_laps_success(mock_get):
    from services.strava import get_activity_laps

    mock_get.return_value = MockResponse(MOCK_LAPS)
    result = get_activity_laps(99001)

    assert len(result) == 2
    assert result[0]["lap_index"] == 1
    assert "activities/99001/laps" in str(mock_get.call_args)


@patch("services.strava.requests.get")
def test_get_activity_laps_error(mock_get):
    from services.strava import get_activity_laps

    mock_get.return_value = MockResponse({"message": "Not Found"}, status_code=404)

    with pytest.raises(Exception, match="Strava API error"):
        get_activity_laps(999999)


# ── get_activity_zones ──

@patch("services.strava.requests.get")
def test_get_activity_zones_success(mock_get):
    from services.strava import get_activity_zones

    mock_get.return_value = MockResponse(MOCK_ZONES)
    result = get_activity_zones(99001)

    assert len(result) == 1
    assert result[0]["type"] == "heartrate"
    assert "activities/99001/zones" in str(mock_get.call_args)


@patch("services.strava.requests.get")
def test_get_activity_zones_error(mock_get):
    from services.strava import get_activity_zones

    mock_get.return_value = MockResponse({"message": "Payment Required"}, status_code=402)

    with pytest.raises(Exception, match="Strava API error"):
        get_activity_zones(99001)


# ── get_athlete_clubs ──

@patch("services.strava.requests.get")
def test_get_athlete_clubs_success(mock_get):
    from services.strava import get_athlete_clubs

    mock_get.return_value = MockResponse(MOCK_CLUBS)
    result = get_athlete_clubs(per_page=10)

    assert len(result) == 1
    assert result[0]["name"] == "Paris Runners"


@patch("services.strava.requests.get")
def test_get_athlete_clubs_error(mock_get):
    from services.strava import get_athlete_clubs

    mock_get.return_value = MockResponse({"message": "Unauthorized"}, status_code=401)

    with pytest.raises(Exception, match="Strava API error"):
        get_athlete_clubs()


# ── explore_segments ──

@patch("services.strava.requests.get")
def test_explore_segments_success(mock_get):
    from services.strava import explore_segments

    mock_get.return_value = MockResponse(MOCK_SEGMENTS_RESPONSE)
    result = explore_segments("48.8,2.3,48.9,2.4", activity_type="riding")

    assert "segments" in result
    assert result["segments"][0]["name"] == "Champs-Elysees Sprint"


@patch("services.strava.requests.get")
def test_explore_segments_error(mock_get):
    from services.strava import explore_segments

    mock_get.return_value = MockResponse({"message": "Bad Request"}, status_code=400)

    with pytest.raises(Exception, match="Strava API error"):
        explore_segments("invalid")


# ── Token refresh ──

@patch("services.strava.set_key")
@patch("services.strava.requests.post")
def test_refresh_token_success(mock_post, mock_set_key):
    from services.strava import _refresh_token, _token_store

    mock_post.return_value = MockResponse(MOCK_TOKEN_RESPONSE)
    _refresh_token()

    assert _token_store["access_token"] == "new_access_token_123"
    assert _token_store["refresh_token"] == "new_refresh_token_456"
    assert mock_set_key.call_count == 3  # access, refresh, expires_at


@patch("services.strava.requests.post")
def test_refresh_token_failure(mock_post):
    from services.strava import _refresh_token

    mock_post.return_value = MockResponse({"message": "Bad Request"}, status_code=400)

    with pytest.raises(Exception, match="Token refresh failed"):
        _refresh_token()


# ── exchange_code ──

@patch("services.strava.set_key")
@patch("services.strava.requests.post")
def test_exchange_code_success(mock_post, mock_set_key):
    from services.strava import exchange_code, _token_store

    mock_post.return_value = MockResponse(MOCK_TOKEN_RESPONSE)
    result = exchange_code("test_code_123")

    assert result["access_token"] == "new_access_token_123"
    assert _token_store["access_token"] == "new_access_token_123"


@patch("services.strava.requests.post")
def test_exchange_code_failure(mock_post):
    from services.strava import exchange_code

    mock_post.return_value = MockResponse({"message": "Invalid code"}, status_code=400)

    with pytest.raises(Exception, match="Code exchange failed"):
        exchange_code("bad_code")


# ── get_authorize_url ──

def test_get_authorize_url():
    from services.strava import get_authorize_url

    url = get_authorize_url("http://localhost:8000/auth/callback")

    assert "client_id=test_id" in url
    assert "redirect_uri=http://localhost:8000/auth/callback" in url
    assert "scope=read,activity:read_all,profile:read_all" in url
    assert "approval_prompt=force" in url
