# # app_express.py
# from shiny import reactive
# from shiny.express import input, render, ui

# # Page options (optional but nice)
# ui.page_opts(title="Random Image iFrame Demo")

# # --- Existing example: slider + text -----------------------------------------
# ui.input_slider("n", "N", 0, 100, 20)


# @render.code
# def txt():
#     return f"n*2 is {input.n() * 2}"


# # --- New section: random image iframe ----------------------------------------

# ui.hr()
# ui.h3("Random image in an iframe")

# # Button to change image
# ui.input_action_button("next_img", "Next image")

# ui.br()

# # Reactive URL that depends on button clicks
# @reactive.calc
# def img_url() -> str:
#     # each click changes the seed → new random image
#     click_count = input.next_img()
#     # use click_count as the seed so each press gives a new URL
#     return f"https://picsum.photos/seed/{click_count}/800/400"

# OMERO_VIEWER_BASE = "https://nife-dev.cancer.gov/iviewer/?images=11422"
# # Render an iframe pointing to that URL
# @render.ui
# def image_frame():
#     return ui.tags.iframe(
#         src=OMERO_VIEWER_BASE,
#         style="width: 100%; height: 400px; border: none;",
#         title="Random image viewer",
#     )

# @render.ui
# def image_frame1():
#     return ui.tags.iframe(
#         src=OMERO_VIEWER_BASE,
#         style="width: 100%; height: 400px; border: none;",
#         title="Random image viewer",
#     )


import io
import os

import httpx
from shiny.express import input, render, ui
from shiny import ui as core_ui  # classic UI outputs

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------

OMERO_BASE = os.environ.get("OMERO_BASE", "https://nife-dev.cancer.gov").rstrip("/")
DEFAULT_TIMEOUT = 10.0

OMERO_USER = os.environ.get("OMERO_PROXY_USER")
OMERO_PASS = os.environ.get("OMERO_PROXY_PASS")

if not OMERO_USER or not OMERO_PASS:
    print("WARNING: OMERO_PROXY_USER / OMERO_PROXY_PASS not set – image fetches will fail.")


def omero_thumbnail_url(image_id: str) -> str:
    return f"{OMERO_BASE}/webgateway/render_thumbnail/11422/"


def omero_full_image_url(image_id: str) -> str:
    return f"{OMERO_BASE}/webgateway/render_image/11422/"


def fetch_binary(url: str) -> bytes:
    """
    Server-side fetch to OMERO using service-account credentials.
    """
    auth = (OMERO_USER, OMERO_PASS) if OMERO_USER and OMERO_PASS else None

    # NOTE: verify=False only if you have internal/self-signed certs.
    # For proper TLS, set verify=True or point to CA bundle.
    with httpx.Client(timeout=DEFAULT_TIMEOUT, verify=False, auth=auth) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.content


# -------------------------------------------------------------------
# UI (Express)
# -------------------------------------------------------------------

ui.page_opts(title="OMERO Shiny Proxy Viewer", fillable=True)

with ui.sidebar(open="open"):
    ui.input_text(
        "image_id",
        "OMERO Image ID",
        value="11422",
        width="100%",
    )
    ui.input_action_button("load_btn", "Load Image", width="100%")
    ui.hr()
    ui.markdown(
        """
        **How this works**

        - Shiny server calls OMERO `/webgateway` using a service account.
        - The browser talks only to this Shiny app.
        - For full iviewer, we embed the existing Svelte-based viewer.
        """
    )

with ui.layout_column_wrap(width=1 / 3):
    with ui.card(full_screen=True):
        ui.card_header("Thumbnail (via Shiny → OMERO proxy)")
        core_ui.output_image("thumb")

    with ui.card(full_screen=True):
        ui.card_header("Full image (via Shiny → OMERO proxy)")
        core_ui.output_image("full_img")

    with ui.card(full_screen=True):
        ui.card_header("Interactive iviewer (Svelte app iframe)")
        core_ui.output_ui("iviewer_frame")


# -------------------------------------------------------------------
# Server logic
# -------------------------------------------------------------------



@render.ui
def iviewer_frame():
    """
    Embed the existing Svelte+iviewer app in an iframe.

    Assumes your Svelte app listens to `image_id` in the URL, e.g.
    https://rana22.github.io/svelte-app/#/omero?images=1234
    """
    img_id = input.image_id().strip() or "11422"

    svelte_url = (
        f"https://rana22.github.io/svelte-app/#/"
    )

    return core_ui.HTML(
        f"""
        <iframe
          src="{svelte_url}"
          style="width:100%; height:600px; border:none;"
          allowfullscreen
        ></iframe>
        """
    )
