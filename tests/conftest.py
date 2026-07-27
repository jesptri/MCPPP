"""Shared fixtures and mock data for all Meteo-France MCP tests."""

import pytest


# ---------------------------------------------------------------------------
# Meteo-France API mock responses -- realistic payloads
# ---------------------------------------------------------------------------

MOCK_PLACES = [
    {
        "name": "Paris",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "country": "FR",
        "admin": "Ile-de-France",
        "admin2": "75",
        "postal_code": "75001",
        "insee": "75056",
    },
    {
        "name": "Paris-Charles de Gaulle",
        "latitude": 49.0097,
        "longitude": 2.5479,
        "country": "FR",
        "admin": "Ile-de-France",
        "admin2": "95",
        "postal_code": "95700",
        "insee": "95527",
    },
]

MOCK_FORECAST = {
    "position": {
        "lat": 48.8566,
        "lon": 2.3522,
        "alti": 35,
        "name": "Paris",
        "country": "FR",
        "timezone": "Europe/Paris",
    },
    "updated_on": 1700000000,
    "today": {
        "dt": 1700000000,
        "T": {"min": 8.0, "max": 15.0},
        "humidity": {"min": 55, "max": 85},
        "weather12H": {"icon": "p3j", "desc": "Cloudy"},
    },
    "daily": [
        {
            "dt": 1700000000,
            "T": {"min": 8.0, "max": 15.0},
            "humidity": {"min": 55, "max": 85},
        },
        {
            "dt": 1700086400,
            "T": {"min": 7.0, "max": 14.0},
            "humidity": {"min": 60, "max": 90},
        },
    ],
    "hourly": [
        {
            "dt": 1700000000,
            "T": {"value": 12.5},
            "wind": {"speed": 15, "direction": 220},
            "weather": {"icon": "p3j", "desc": "Cloudy"},
        }
    ],
    "probability": [],
}

MOCK_OBSERVATION = {
    "timezone": "Europe/Paris",
    "time": "2024-11-14T14:00:00",
    "temperature_c": 12.5,
    "wind_speed_kmh": 15.0,
    "wind_direction_deg": 220,
    "weather_description": "Cloudy",
    "weather_icon": "p3j",
}

MOCK_RAIN = {
    "position": {"lat": 48.8566, "lon": 2.3522, "name": "Paris"},
    "updated_on": 1700000000,
    "forecast": [
        {"dt": 1700000000, "rain": 1, "desc": "Dry weather"},
        {"dt": 1700000600, "rain": 1, "desc": "Dry weather"},
    ],
    "quality": 0,
    "next_rain": None,
}

MOCK_WARNINGS = {
    "domain": "france",
    "update_time": 1700000000,
    "end_validity_time": 1700086400,
    "max_color": 2,
    "max_color_name": "Yellow",
    "phenomenons": [
        {
            "phenomenon_id": 1,
            "phenomenon_name": "Wind",
            "color": 2,
            "color_name": "Yellow",
        },
        {
            "phenomenon_id": 3,
            "phenomenon_name": "Thunderstorms",
            "color": 1,
            "color_name": "Green",
        },
    ],
}


# ---------------------------------------------------------------------------
# Place-like object used for search_places mocking
# ---------------------------------------------------------------------------

class MockPlace:
    """Mimics meteofrance_api.model.Place for unit tests."""

    def __init__(self, data: dict):
        self._data = data

    @property
    def name(self):
        return self._data["name"]

    @property
    def latitude(self):
        return self._data["latitude"]

    @property
    def longitude(self):
        return self._data["longitude"]

    @property
    def country(self):
        return self._data["country"]

    @property
    def admin(self):
        return self._data.get("admin")

    @property
    def admin2(self):
        return self._data.get("admin2")

    @property
    def postal_code(self):
        return self._data.get("postal_code")

    @property
    def insee(self):
        return self._data.get("insee")
