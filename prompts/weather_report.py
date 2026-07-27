import json
from services.meteofrance import search_places, get_forecast, get_observation

PROMPT_DEFINITION = {
    "name": "weather_report",
    "description": "Generates a complete weather report for a given city",
    "arguments": [
        {
            "name": "city",
            "description": "City name (e.g. 'Paris', 'Lyon', 'Marseille')",
            "required": True,
        }
    ],
}


def get_weather_report_messages(arguments: dict):
    """Build the prompt messages for a weather report."""
    city = arguments.get("city")
    if not city:
        raise ValueError("city is required")

    places = search_places(city)
    if not places:
        raise ValueError(f"No place found for '{city}'")

    place = places[0]
    lat, lon = place["latitude"], place["longitude"]

    forecast = get_forecast(lat, lon)
    observation = get_observation(lat, lon)

    data = {
        "place": place,
        "current_observation": observation,
        "today_forecast": forecast.get("today"),
        "hourly_forecast": forecast.get("hourly", [])[:6],
        "daily_forecast": forecast.get("daily", [])[:5],
    }

    return {
        "description": PROMPT_DEFINITION["description"],
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Here is the weather data for {place['name']}:\n\n"
                        f"{json.dumps(data, indent=2, ensure_ascii=False)}\n\n"
                        f"Generate a complete and readable weather report: "
                        f"current conditions, today's forecast, "
                        f"trend for the coming days. "
                        f"Give practical advice (clothing, umbrella, etc.)."
                    ),
                },
            }
        ],
    }
