"""UI resource for the Meteo France forecast MCP App (SEP-1865).

Serves the forecast widget HTML with mimeType text/html;profile=mcp-app
and the required _meta.ui metadata (CSP, prefersBorder).
"""

import os

_HTML_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir, "static", "forecast_app.html"
)

UI_RESOURCE_URI = "ui://meteo-france/forecast"

UI_RESOURCE_DEFINITION = {
    "uri": UI_RESOURCE_URI,
    "name": "Forecast Widget",
    "description": "Interactive weather forecast widget for Meteo France",
    "mimeType": "text/html;profile=mcp-app",
}


def read_forecast_ui():
    """Return the UI resource content for resources/read."""
    with open(_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    return {
        "uri": UI_RESOURCE_URI,
        "mimeType": "text/html;profile=mcp-app",
        "text": html,
        "_meta": {
            "ui": {
                "csp": {
                    # The widget is self-contained for now.
                    # If we later call the Meteo France API directly from
                    # the browser, add the domain here.
                    "connectDomains": [],
                    "resourceDomains": [],
                },
                "prefersBorder": True,
            }
        },
    }
