import json
from services.meteofrance import get_forecast

RESOURCE_TEMPLATE = {
    "uriTemplate": "meteofrance://forecast/{latitude}/{longitude}",
    "name": "Weather Forecast",
    "description": "Detailed weather forecast for a GPS position (latitude/longitude)",
    "mimeType": "application/json",
}


def read_forecast(latitude: float, longitude: float):
    """Called when the client does resources/read with uri=meteofrance://forecast/<lat>/<lon>."""
    data = get_forecast(latitude, longitude)
    return {
        "uri": f"meteofrance://forecast/{latitude}/{longitude}",
        "mimeType": "application/json",
        "text": json.dumps(data, indent=2, ensure_ascii=False),
    }
