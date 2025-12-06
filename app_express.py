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
from shiny.express import ui, input, render
from shiny import ui as core_ui  # classic ui for outputs

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------

OMERO_BASE = os.environ.get("OMERO_BASE", "https://nife-dev.cancer.gov")
DEFAULT_TIMEOUT = 10.0


def omero_thumbnail_url(image_id: str) -> str:
    return f"{OMERO_BASE}/webgateway/render_thumbnail/{image_id}/"


def omero_full_image_url(image_id: str) -> str:
    return f"{OMERO_BASE}/webgateway/render_image/{image_id}/"


def fetch_binary(url: str) -> bytes:
    with httpx.Client(timeout=DEFAULT_TIMEOUT, verify=False) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.content


# -------------------------------------------------------------------
# UI (Express) + classic outputs
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

        - Shiny (server) calls OMERO `/webgateway` internally.
        - The browser only talks to this Shiny app.
        - No direct public → private requests from the browser.
        """
    )

with ui.layout_column_wrap(width=1 / 2):
    with ui.card(full_screen=True):
        ui.card_header("Thumbnail (proxied via Shiny)")
        core_ui.output_image("thumb")   # <-- use classic ui

    with ui.card(full_screen=True):
        ui.card_header("Full image (proxied via Shiny)")
        core_ui.output_image("full_img")  # <-- use classic ui


# -------------------------------------------------------------------
# Server logic
# -------------------------------------------------------------------


@render.image
def thumb():
    img_id = input.image_id().strip()
    if not img_id:
        return None

    try:
        data = fetch_binary(omero_thumbnail_url(img_id))
    except Exception as e:
        print(f"Error fetching thumbnail for {img_id}: {e}")
        return None

    return {
        "src": io.BytesIO(data),
        "format": "jpeg",
    }


@render.image
def full_img():
    img_id = input.image_id().strip()
    if not img_id:
        return None

    try:
        data = fetch_binary(omero_full_image_url(img_id))
    except Exception as e:
        print(f"Error fetching full image for {img_id}: {e}")
        return None

    return {
        "src": io.BytesIO(data),
        "format": "jpeg",
    }
