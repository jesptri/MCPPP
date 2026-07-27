"""Service layer for the Meteo-France MCP server.

Wraps the meteofrance-api client to expose simple functions
consumed by MCP tools, resources and prompts.
"""

from __future__ import annotations

from meteofrance_api import MeteoFranceClient

# Singleton client -- no API key needed for the public mobile API.
_client = MeteoFranceClient()


# ---------------------------------------------------------------------------
# Places
# ---------------------------------------------------------------------------

def search_places(query: str, latitude: float | None = None, longitude: float | None = None) -> list[dict]:
    """Search for cities / forecast locations by name or postal code."""
    places = _client.search_places(query, latitude=latitude, longitude=longitude)
    return [
        {
            "name": p.name,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "country": p.country,
            "admin": p.admin,
            "admin2": p.admin2,
            "postal_code": p.postal_code,
            "insee": p.insee,
        }
        for p in places
    ]


# ---------------------------------------------------------------------------
# Forecast
# ---------------------------------------------------------------------------

def get_forecast(latitude: float, longitude: float) -> dict:
    """Return the weather forecast for a GPS location."""
    fc = _client.get_forecast(latitude, longitude, language="fr")
    return {
        "position": fc.position,
        "updated_on": fc.updated_on,
        "today": fc.today_forecast,
        "daily": fc.daily_forecast,
        "hourly": fc.forecast[:12],  # next 12 hours to keep payload manageable
        "probability": fc.probability_forecast[:6] if fc.probability_forecast else [],
    }


# ---------------------------------------------------------------------------
# Observation
# ---------------------------------------------------------------------------

def get_observation(latitude: float, longitude: float) -> dict:
    """Return the latest weather observation for a GPS location."""
    obs = _client.get_observation(latitude, longitude, language="fr")
    return {
        "timezone": obs.timezone,
        "time": obs.time_as_string,
        "temperature_c": obs.temperature,
        "wind_speed_kmh": obs.wind_speed,
        "wind_direction_deg": obs.wind_direction,
        "weather_description": obs.weather_description,
        "weather_icon": obs.weather_icon,
    }


# ---------------------------------------------------------------------------
# Rain (next hour)
# ---------------------------------------------------------------------------

def get_rain(latitude: float, longitude: float) -> dict:
    """Return the rain forecast for the next hour at a GPS location."""
    rain = _client.get_rain(latitude, longitude, language="fr")
    next_rain = rain.next_rain_date_locale()
    return {
        "position": rain.position,
        "updated_on": rain.updated_on,
        "forecast": rain.forecast,
        "quality": rain.quality,
        "next_rain": next_rain.isoformat() if next_rain else None,
    }


# ---------------------------------------------------------------------------
# Warnings (vigilance)
# ---------------------------------------------------------------------------

PHENOMENON_NAMES = {
    1: "Wind",
    2: "Rain-Flood",
    3: "Thunderstorms",
    4: "Flood",
    5: "Snow-Ice",
    6: "Heatwave",
    7: "Extreme Cold",
    8: "Avalanches",
    9: "Waves-Submersion",
}

COLOR_NAMES = {
    1: "Green",
    2: "Yellow",
    3: "Orange",
    4: "Red",
}


def get_warnings(domain: str = "france", depth: int = 0) -> dict:
    """Return the current weather alerts for a domain.

    Args:
        domain: 'france' or a 2-digit department number (e.g. '75').
        depth: 0 = summary only; 1 = include per-department details (france only).
    """
    ph = _client.get_warning_current_phenomenons(domain=domain, depth=depth)
    phenomenons = []
    for p in ph.phenomenons_max_colors:
        phenomenons.append({
            "phenomenon_id": p.get("phenomenon_id"),
            "phenomenon_name": PHENOMENON_NAMES.get(p.get("phenomenon_id"), "Unknown"),
            "color": p.get("phenomenon_max_color_id"),
            "color_name": COLOR_NAMES.get(p.get("phenomenon_max_color_id"), "Unknown"),
        })
    return {
        "domain": ph.domain_id,
        "update_time": ph.update_time,
        "end_validity_time": ph.end_validity_time,
        "max_color": ph.get_domain_max_color(),
        "max_color_name": COLOR_NAMES.get(ph.get_domain_max_color(), "Unknown"),
        "phenomenons": phenomenons,
    }
