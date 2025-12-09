import os
import json
import httpx

from shiny.express import ui, input
from shiny import render, ui as core_ui

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------

METADATA_API_URL = os.environ.get(
    "METADATA_API_URL",
    "https://nife-dev.cancer.gov/metadata/api/fast-api",
)
DEFAULT_TIMEOUT = 10.0


def fetch_metadata_json():
    """Call the FastAPI metadata endpoint and return parsed JSON or an error."""
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT, verify=True) as client:
            resp = client.get(METADATA_API_URL)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        # Return an error object so UI can still render something
        return {
            "error": str(e),
            "endpoint": METADATA_API_URL,
        }


# -------------------------------------------------------------------
# UI (Shiny Express)
# -------------------------------------------------------------------

ui.page_opts(title="OMERO Metadata API Test", fillable=True)

with ui.sidebar(open="open"):
    ui.markdown(
        f"""
        ### Metadata API Test

        - Endpoint: `{METADATA_API_URL}`
        - Click **Refresh** to re-query the API.
        """
    )
    ui.input_action_button("refresh", "Refresh", width="100%")

with ui.card(full_screen=True):
    ui.card_header("Metadata API JSON response")
    core_ui.output_ui("metadata_response")  # render.ui target


# -------------------------------------------------------------------
# Server logic
# -------------------------------------------------------------------

@render.ui
def metadata_response():
    # Make this reactive to button clicks
    input.refresh()

    data = fetch_metadata_json()

    # Pretty-print JSON
    pretty = json.dumps(data, indent=2, sort_keys=True)

    # Show inside <pre> for nice formatting
    return core_ui.pre(pretty)
