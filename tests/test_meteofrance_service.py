"""Unit tests for services/meteofrance.py -- all API calls mocked."""

from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from tests.conftest import MOCK_PLACES, MockPlace


# ---------------------------------------------------------------------------
# search_places
# ---------------------------------------------------------------------------

@patch("services.meteofrance._client")
def test_search_places_returns_list(mock_client):
    from services.meteofrance import search_places

    mock_client.search_places.return_value = [MockPlace(p) for p in MOCK_PLACES]
    result = search_places("Paris")

    assert len(result) == 2
    assert result[0]["name"] == "Paris"
    assert result[0]["latitude"] == 48.8566
    assert result[0]["country"] == "FR"
    mock_client.search_places.assert_called_once_with("Paris", latitude=None, longitude=None)


@patch("services.meteofrance._client")
def test_search_places_with_coords(mock_client):
    from services.meteofrance import search_places

    mock_client.search_places.return_value = [MockPlace(MOCK_PLACES[0])]
    search_places("Paris", latitude=48.85, longitude=2.35)

    mock_client.search_places.assert_called_once_with("Paris", latitude=48.85, longitude=2.35)


@patch("services.meteofrance._client")
def test_search_places_empty(mock_client):
    from services.meteofrance import search_places

    mock_client.search_places.return_value = []
    result = search_places("xyznonexistent")

    assert result == []


# ---------------------------------------------------------------------------
# get_forecast
# ---------------------------------------------------------------------------

@patch("services.meteofrance._client")
def test_get_forecast(mock_client):
    from services.meteofrance import get_forecast

    mock_fc = MagicMock()
    mock_fc.position = {"lat": 48.8566, "lon": 2.3522, "name": "Paris"}
    mock_fc.updated_on = 1700000000
    mock_fc.today_forecast = {"dt": 1700000000, "T": {"min": 8, "max": 15}}
    mock_fc.daily_forecast = [{"dt": 1700000000}]
    mock_fc.forecast = [{"dt": 1700000000, "T": {"value": 12}}]
    mock_fc.probability_forecast = []
    mock_client.get_forecast.return_value = mock_fc

    result = get_forecast(48.8566, 2.3522)

    assert result["position"]["name"] == "Paris"
    assert result["updated_on"] == 1700000000
    assert result["today"]["T"]["min"] == 8
    mock_client.get_forecast.assert_called_once_with(48.8566, 2.3522, language="fr")


# ---------------------------------------------------------------------------
# get_observation
# ---------------------------------------------------------------------------

@patch("services.meteofrance._client")
def test_get_observation(mock_client):
    from services.meteofrance import get_observation

    mock_obs = MagicMock()
    mock_obs.timezone = "Europe/Paris"
    mock_obs.time_as_string = "2024-11-14T14:00:00"
    mock_obs.temperature = 12.5
    mock_obs.wind_speed = 15.0
    mock_obs.wind_direction = 220
    mock_obs.weather_description = "Cloudy"
    mock_obs.weather_icon = "p3j"
    mock_client.get_observation.return_value = mock_obs

    result = get_observation(48.8566, 2.3522)

    assert result["temperature_c"] == 12.5
    assert result["weather_description"] == "Cloudy"
    assert result["timezone"] == "Europe/Paris"


# ---------------------------------------------------------------------------
# get_rain
# ---------------------------------------------------------------------------

@patch("services.meteofrance._client")
def test_get_rain_no_rain(mock_client):
    from services.meteofrance import get_rain

    mock_rain = MagicMock()
    mock_rain.position = {"lat": 48.8566, "lon": 2.3522}
    mock_rain.updated_on = 1700000000
    mock_rain.forecast = [{"dt": 1700000000, "rain": 1, "desc": "Dry weather"}]
    mock_rain.quality = 0
    mock_rain.next_rain_date_locale.return_value = None
    mock_client.get_rain.return_value = mock_rain

    result = get_rain(48.8566, 2.3522)

    assert result["next_rain"] is None
    assert result["quality"] == 0


# ---------------------------------------------------------------------------
# get_warnings
# ---------------------------------------------------------------------------

@patch("services.meteofrance._client")
def test_get_warnings(mock_client):
    from services.meteofrance import get_warnings

    mock_ph = MagicMock()
    mock_ph.domain_id = "france"
    mock_ph.update_time = 1700000000
    mock_ph.end_validity_time = 1700086400
    mock_ph.get_domain_max_color.return_value = 2
    mock_ph.phenomenons_max_colors = [
        {"phenomenon_id": 1, "phenomenon_max_color_id": 2},
        {"phenomenon_id": 3, "phenomenon_max_color_id": 1},
    ]
    mock_client.get_warning_current_phenomenons.return_value = mock_ph

    result = get_warnings(domain="france")

    assert result["domain"] == "france"
    assert result["max_color"] == 2
    assert result["max_color_name"] == "Yellow"
    assert len(result["phenomenons"]) == 2
    assert result["phenomenons"][0]["phenomenon_name"] == "Wind"
    assert result["phenomenons"][1]["color_name"] == "Green"
    mock_client.get_warning_current_phenomenons.assert_called_once_with(domain="france", depth=0)
