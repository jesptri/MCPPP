"""Unit tests for all tool handlers — Strava API calls mocked at the service layer."""
from unittest.mock import patch

import pytest

from tests.conftest import (
    MOCK_ACTIVITIES,
    MOCK_ACTIVITY,
    MOCK_ATHLETE,
    MOCK_STATS,
    MOCK_LAPS,
    MOCK_ZONES,
    MOCK_CLUBS,
    MOCK_SEGMENTS_RESPONSE,
    MOCK_GEAR,
)


# ── list_activities ──

@patch("tools.activities.get_activities", return_value=MOCK_ACTIVITIES)
def test_list_activities_tool(mock):
    from tools.activities import list_activities_tool

    result = list_activities_tool({"per_page": 2})

    assert len(result) == 2
    assert result[0]["name"] == "Morning Run"
    assert result[0]["distance_km"] == 10.23
    assert result[0]["moving_time_min"] == 52.0
    assert result[0]["date"] == "2024-06-15"
    assert result[1]["type"] == "Ride"


@patch("tools.activities.get_activities", return_value=MOCK_ACTIVITIES)
def test_list_activities_tool_default_per_page(mock):
    from tools.activities import list_activities_tool

    list_activities_tool({})
    mock.assert_called_once_with(5)


# ── get_athlete_stats ──

@patch("tools.stats.get_athlete_stats", return_value=MOCK_STATS)
@patch("tools.stats.get_athlete", return_value=MOCK_ATHLETE)
def test_get_athlete_stats_tool_auto_id(mock_athlete, mock_stats):
    from tools.stats import get_athlete_stats_tool

    result = get_athlete_stats_tool({})

    mock_athlete.assert_called_once()  # auto-fetches athlete ID
    mock_stats.assert_called_once_with(123456)
    assert result["biggest_ride_distance_km"] == 120.0
    assert result["recent_ride_totals"]["count"] == 3
    assert result["recent_ride_totals"]["distance_km"] == 95.0


@patch("tools.stats.get_athlete_stats", return_value=MOCK_STATS)
def test_get_athlete_stats_tool_explicit_id(mock_stats):
    from tools.stats import get_athlete_stats_tool

    result = get_athlete_stats_tool({"athlete_id": 789})

    mock_stats.assert_called_once_with(789)
    assert result["all_ride_totals"]["count"] == 200


# ── get_activity_laps ──

@patch("tools.laps.get_activity_laps", return_value=MOCK_LAPS)
def test_get_activity_laps_tool(mock):
    from tools.laps import get_activity_laps_tool

    result = get_activity_laps_tool({"activity_id": 99001})

    assert len(result) == 2
    assert result[0]["lap_index"] == 1
    assert result[0]["distance_km"] == 5.0
    assert result[0]["average_speed_kmh"] == 12.0  # 3.33 * 3.6 = 11.988 -> 12.0
    assert result[1]["average_watts"] == 210


def test_get_activity_laps_tool_missing_id():
    from tools.laps import get_activity_laps_tool

    with pytest.raises(ValueError, match="activity_id is required"):
        get_activity_laps_tool({})


# ── get_activity_zones ──

@patch("tools.zones.get_activity_zones", return_value=MOCK_ZONES)
def test_get_activity_zones_tool(mock):
    from tools.zones import get_activity_zones_tool

    result = get_activity_zones_tool({"activity_id": 99001})

    assert len(result) == 1
    assert result[0]["type"] == "heartrate"
    assert result[0]["sensor_based"] is True
    assert len(result[0]["buckets"]) == 5
    assert result[0]["buckets"][0]["time_seconds"] == 300


def test_get_activity_zones_tool_missing_id():
    from tools.zones import get_activity_zones_tool

    with pytest.raises(ValueError, match="activity_id is required"):
        get_activity_zones_tool({})


# ── get_athlete_clubs ──

@patch("tools.clubs.get_athlete_clubs", return_value=MOCK_CLUBS)
def test_get_athlete_clubs_tool(mock):
    from tools.clubs import get_athlete_clubs_tool

    result = get_athlete_clubs_tool({})

    assert len(result) == 1
    assert result[0]["name"] == "Paris Runners"
    assert result[0]["member_count"] == 250
    mock.assert_called_once_with(30)


@patch("tools.clubs.get_athlete_clubs", return_value=MOCK_CLUBS)
def test_get_athlete_clubs_tool_custom_per_page(mock):
    from tools.clubs import get_athlete_clubs_tool

    get_athlete_clubs_tool({"per_page": 10})
    mock.assert_called_once_with(10)


# ── explore_segments ──

@patch("tools.segments.explore_segments", return_value=MOCK_SEGMENTS_RESPONSE)
def test_explore_segments_tool(mock):
    from tools.segments import explore_segments_tool

    result = explore_segments_tool({"bounds": "48.8,2.3,48.9,2.4"})

    assert len(result) == 1
    assert result[0]["name"] == "Champs-Elysees Sprint"
    assert result[0]["distance_km"] == 2.1
    mock.assert_called_once_with("48.8,2.3,48.9,2.4", "riding")


@patch("tools.segments.explore_segments", return_value=MOCK_SEGMENTS_RESPONSE)
def test_explore_segments_tool_running(mock):
    from tools.segments import explore_segments_tool

    explore_segments_tool({"bounds": "48.8,2.3,48.9,2.4", "activity_type": "running"})
    mock.assert_called_once_with("48.8,2.3,48.9,2.4", "running")


def test_explore_segments_tool_missing_bounds():
    from tools.segments import explore_segments_tool

    with pytest.raises(ValueError, match="bounds is required"):
        explore_segments_tool({})


# ── get_gear ──

@patch("tools.gear.get_gear", return_value=MOCK_GEAR)
def test_get_gear_tool(mock):
    from tools.gear import get_gear_tool

    result = get_gear_tool({"gear_id": "b12345"})

    assert result["id"] == "b12345"
    assert result["name"] == "Tarmac SL7"
    assert result["brand_name"] == "Specialized"
    assert result["distance_km"] == 3254.76
    assert result["weight_kg"] == 7.2
    mock.assert_called_once_with("b12345")


def test_get_gear_tool_missing_id():
    from tools.gear import get_gear_tool

    with pytest.raises(ValueError, match="gear_id is required"):
        get_gear_tool({})
