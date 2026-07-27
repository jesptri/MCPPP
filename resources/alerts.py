import json
from services.meteofrance import get_warnings

RESOURCE_DEFINITION = {
    "uri": "meteofrance://alerts/france",
    "name": "National Weather Alerts",
    "description": "Summary of current weather alerts across metropolitan France",
    "mimeType": "application/json",
}


def read_alerts():
    """Called when the client does resources/read with uri=meteofrance://alerts/france."""
    data = get_warnings(domain="france")
    return {
        "uri": RESOURCE_DEFINITION["uri"],
        "mimeType": "application/json",
        "text": json.dumps(data, indent=2, ensure_ascii=False),
    }
