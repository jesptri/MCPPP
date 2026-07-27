"""Unit tests for all tool handlers -- Meteo-France API calls mocked at the service layer."""
from unittest.mock import patch

import pytest

from tests.conftest import (
    MOCK_PLACES,
    MOCK_FORECAST,
    MOCK_OBSERVATION,
    MOCK_RAIN,
    MOCK_WARNINGS,
)


# -- search_places --

@patch("tools.search_places.search_places", return_value=MOCK_PLACES)
def test_search_places_tool(mock):
    from tools.search_places import search_places_tool

    result = search_places_tool({"query": "Paris"})

    assert len(result) == 2
    assert result[0]["name"] == "Paris"
    mock.assert_called_once_with("Paris", latitude=None, longitude=None)


@patch("tools.search_places.search_places", return_value=MOCK_PLACES[:1])
def test_search_places_tool_with_coords(mock):
    from tools.search_places import search_places_tool

    result = search_places_tool({"query": "Paris", "latitude": 48.85, "longitude": 2.35})
    mock.assert_called_once_with("Paris", latitude=48.85, longitude=2.35)


def test_search_places_tool_missing_query():
    from tools.search_places import search_places_tool

    with pytest.raises(ValueError, match="query is required"):
        search_places_tool({})


# -- get_forecast --

@patch("tools.forecast.get_forecast", return_value=MOCK_FORECAST)
def test_get_forecast_tool(mock):
    from tools.forecast import get_forecast_tool

    result = get_forecast_tool({"latitude": 48.8566, "longitude": 2.3522})

    assert result["position"]["name"] == "Paris"
    assert result["updated_on"] == 1700000000
    mock.assert_called_once_with(48.8566, 2.3522)


def test_get_forecast_tool_missing_coords():
    from tools.forecast import get_forecast_tool

    with pytest.raises(ValueError, match="latitude and longitude are required"):
        get_forecast_tool({})


# -- get_observation --

@patch("tools.observation.get_observation", return_value=MOCK_OBSERVATION)
def test_get_observation_tool(mock):
    from tools.observation import get_observation_tool

    result = get_observation_tool({"latitude": 48.8566, "longitude": 2.3522})

    assert result["temperature_c"] == 12.5
    assert result["weather_description"] == "Cloudy"
    mock.assert_called_once_with(48.8566, 2.3522)


def test_get_observation_tool_missing_coords():
    from tools.observation import get_observation_tool

    with pytest.raises(ValueError, match="latitude and longitude are required"):
        get_observation_tool({"latitude": 48.85})


# -- get_rain --

@patch("tools.rain.get_rain", return_value=MOCK_RAIN)
def test_get_rain_tool(mock):
    from tools.rain import get_rain_tool

    result = get_rain_tool({"latitude": 48.8566, "longitude": 2.3522})

    assert result["next_rain"] is None
    assert len(result["forecast"]) == 2
    mock.assert_called_once_with(48.8566, 2.3522)


def test_get_rain_tool_missing_coords():
    from tools.rain import get_rain_tool

    with pytest.raises(ValueError, match="latitude and longitude are required"):
        get_rain_tool({})


# -- get_warnings --

@patch("tools.warnings.get_warnings", return_value=MOCK_WARNINGS)
def test_get_warnings_tool(mock):
    from tools.warnings import get_warnings_tool

    result = get_warnings_tool({})

    assert result["domain"] == "france"
    assert result["max_color_name"] == "Yellow"
    mock.assert_called_once_with(domain="france")


@patch("tools.warnings.get_warnings", return_value=MOCK_WARNINGS)
def test_get_warnings_tool_with_domain(mock):
    from tools.warnings import get_warnings_tool

    get_warnings_tool({"domain": "75"})
    mock.assert_called_once_with(domain="75")
