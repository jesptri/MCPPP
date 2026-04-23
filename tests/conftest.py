"""Shared fixtures and mock data for all tests."""
import time
import pytest


# ---------------------------------------------------------------------------
# Strava API mock responses — realistic payloads matching the real API
# ---------------------------------------------------------------------------
# Of course fake data

MOCK_ATHLETE = {
    "id": 123456,
    "firstname": "Jules",
    "lastname": "E",
    "city": "Paris",
    "country": "France",
    "sex": "M",
    "weight": 72.0,
    "profile": "https://example.com/pic.jpg",
    "follower_count": 42,
    "friend_count": 15, # I've no friend as I'm too fast
}

MOCK_ACTIVITY = {
    "id": 99001,
    "name": "Morning Run",
    "type": "Run",
    "sport_type": "Run",
    "distance": 10234.5,
    "moving_time": 3120,
    "elapsed_time": 3300,
    "total_elevation_gain": 85.0,
    "average_speed": 3.28,
    "max_speed": 4.5,
    "average_heartrate": 155,
    "max_heartrate": 178,
    "calories": 620,
    "start_date_local": "2024-06-15T07:30:00Z",
    "description": "Easy tempo run",
    "kudos_count": 5,
}

MOCK_ACTIVITIES = [
    {
        "name": "Morning Run",
        "type": "Run",
        "distance": 10234.5,
        "moving_time": 3120,
        "start_date_local": "2024-06-15T07:30:00Z",
        "total_elevation_gain": 85,
    },
    {
        "name": "Evening Ride",
        "type": "Ride",
        "distance": 42000.0,
        "moving_time": 5400,
        "start_date_local": "2024-06-14T18:00:00Z",
        "total_elevation_gain": 320,
    },
]

MOCK_STATS = {
    "biggest_ride_distance": 120000.0,
    "biggest_climb_elevation_gain": 1500.0,
    "recent_ride_totals": {
        "count": 3,
        "distance": 95000.0,
        "moving_time": 14400,
        "elevation_gain": 800.0,
    },
    "recent_run_totals": {
        "count": 2,
        "distance": 18000.0,
        "moving_time": 6000,
        "elevation_gain": 150.0,
    },
    "recent_swim_totals": {"count": 0, "distance": 0, "moving_time": 0, "elevation_gain": 0},
    "ytd_ride_totals": {"count": 50, "distance": 2000000, "moving_time": 360000, "elevation_gain": 15000},
    "ytd_run_totals": {"count": 30, "distance": 300000, "moving_time": 108000, "elevation_gain": 3000},
    "ytd_swim_totals": {"count": 0, "distance": 0, "moving_time": 0, "elevation_gain": 0},
    "all_ride_totals": {"count": 200, "distance": 8000000, "moving_time": 1440000, "elevation_gain": 60000},
    "all_run_totals": {"count": 100, "distance": 1000000, "moving_time": 360000, "elevation_gain": 10000},
    "all_swim_totals": {"count": 5, "distance": 10000, "moving_time": 7200, "elevation_gain": 0},
}

MOCK_LAPS = [
    {
        "lap_index": 1,
        "name": "Lap 1",
        "distance": 5000.0,
        "moving_time": 1500,
        "elapsed_time": 1550,
        "total_elevation_gain": 40,
        "average_speed": 3.33,
        "max_speed": 4.2,
        "average_watts": 220,
        "average_cadence": 85,
    },
    {
        "lap_index": 2,
        "name": "Lap 2",
        "distance": 5234.5,
        "moving_time": 1620,
        "elapsed_time": 1700,
        "total_elevation_gain": 45,
        "average_speed": 3.23,
        "max_speed": 4.0,
        "average_watts": 210,
        "average_cadence": 82,
    },
]

MOCK_ZONES = [
    {
        "type": "heartrate",
        "sensor_based": True,
        "points": 6,
        "distribution_buckets": [
            {"min": 0, "max": 120, "time": 300},
            {"min": 120, "max": 150, "time": 1200},
            {"min": 150, "max": 170, "time": 900},
            {"min": 170, "max": 190, "time": 600},
            {"min": 190, "max": -1, "time": 120},
        ],
    }
]

MOCK_CLUBS = [
    {
        "id": 1001,
        "name": "Paris Runners",
        "sport_type": "running",
        "city": "Paris",
        "state": "IDF",
        "country": "France",
        "member_count": 250,
        "private": False,
        "url": "paris-runners",
    }
]

MOCK_SEGMENTS_RESPONSE = {
    "segments": [
        {
            "id": 5001,
            "name": "Champs-Elysees Sprint",
            "climb_category": 0,
            "avg_grade": 0.5,
            "distance": 2100.0,
            "elev_difference": 10.5,
            "start_latlng": [48.8698, 2.3076],
            "end_latlng": [48.8738, 2.2950],
        }
    ]
}

MOCK_GEAR = {
    "id": "b12345",
    "name": "Tarmac SL7",
    "primary": True,
    "brand_name": "Specialized",
    "model_name": "Tarmac SL7",
    "description": "Race bike",
    "distance": 3254761,
    "frame_type": 3,
    "weight": 7.2,
}

MOCK_TOKEN_RESPONSE = {
    "access_token": "new_access_token_123",
    "refresh_token": "new_refresh_token_456",
    "expires_at": int(time.time()) + 21600,
    "athlete": {"firstname": "Jules", "lastname": "E"},
}


# ---------------------------------------------------------------------------
# Helper to build a mock requests.Response
# ---------------------------------------------------------------------------

class MockResponse:
    """Minimal mock for requests.Response."""

    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
        self.text = str(json_data)

    def json(self):
        return self._json
