import os
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


def fetch_metadata() -> str:
    """Call the FastAPI metadata endpoint and return response text."""
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT, verify=True) as client:
            resp = client.get(METADATA_API_URL)
            resp.raise_for_status()
            # return raw text (often JSON); you can pretty-print later
            return resp.text
    except Exception as e:
        # Return an error message instead of crashing the app
        return f"Error contacting metadata API: {e}"


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
    ui.card_header("Metadata API response")
    # classic-core output, since express ui has no output_text
    core_ui.output_text("metadata_response")


# -------------------------------------------------------------------
# Server logic
# -------------------------------------------------------------------

@render.text
def metadata_response():
    # re-run when refresh button is clicked
    input.refresh()

    return fetch_metadata()
