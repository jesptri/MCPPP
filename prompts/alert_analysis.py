import json
from services.meteofrance import get_warnings

PROMPT_DEFINITION = {
    "name": "alert_analysis",
    "description": "Analyzes weather alerts (vigilance) for a department or all of France",
    "arguments": [
        {
            "name": "domain",
            "description": (
                "Vigilance domain: 'france' or a 2-digit department number "
                "(e.g. '75', '33')"
            ),
            "required": False,
        }
    ],
}


def get_alert_analysis_messages(arguments: dict):
    """Build the prompt messages for an alert analysis."""
    domain = arguments.get("domain", "france")

    warnings = get_warnings(domain=domain)

    return {
        "description": PROMPT_DEFINITION["description"],
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        f"Here are the weather alerts (vigilance) for domain '{domain}':\n\n"
                        f"{json.dumps(warnings, indent=2, ensure_ascii=False)}\n\n"
                        f"Analyze these alerts in detail: which phenomena are active, "
                        f"what is the risk level, and what precautions should be taken. "
                        f"If everything is green, reassure the user."
                    ),
                },
            }
        ],
    }
