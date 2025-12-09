import io
import os
from typing import Optional

import httpx
from shiny import ui as core_ui, render, reactive
from shiny.express import ui, input

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

OMERO_BASE = os.environ.get("OMERO_BASE", "https://nife-dev.cancer.gov")

OMERO_USERNAME = os.environ.get("OMERO_USERNAME")
OMERO_PASSWORD = os.environ.get("OMERO_PASSWORD")

DEFAULT_TIMEOUT = 10.0

if not OMERO_USERNAME or not OMERO_PASSWORD:
    print("WARNING: OMERO_USERNAME / OMERO_PASSWORD not set – image fetches will fail.")


# -------------------------------------------------------------------
# OMERO helpers
# -------------------------------------------------------------------

def omero_login() -> Optional[httpx.Client]:
    """
    Log into OMERO using a service account and return an httpx.Client
    with the session cookie stored. Returns None if login fails.
    """
    if not OMERO_USERNAME or not OMERO_PASSWORD:
        return None
    
    if OMERO_USERNAME:
        print(f"user name is present {OMERO_USERNAME}")

    if OMERO_PASSWORD:
        print(f"user OMERO_PASSWORD is present")

    login_url = f"{OMERO_BASE}/omero_plus/login/"

    client = httpx.Client(timeout=DEFAULT_TIMEOUT, verify=True)  # verify=False only if needed

    try:
        resp = client.post(
            login_url,
            data={"username": OMERO_USERNAME, "password": OMERO_PASSWORD},
            follow_redirects=False,
        )
    
    except Exception as e:
        print(f"Error contacting OMERO login endpoint: {e}")
        client.close()
        return None

    # OMERO typically redirects (302) after successful login
    if resp.status_code not in (200, 302):
        print(f"OMERO login failed: HTTP {resp.status_code}")
        client.close()
        return None

    # If no session cookie, something is off
    if "sessionid" not in client.cookies:
        print("OMERO login failed: no sessionid cookie received.")
        client.close()
        return None

    return client


def omero_thumbnail_url(image_id: str) -> str:
    return f"{OMERO_BASE}/webgateway/render_thumbnail/{image_id}/"


def omero_full_image_url(image_id: str) -> str:
    return f"{OMERO_BASE}/webgateway/render_image/{image_id}/"


def fetch_omero_image(image_id: str, kind: str) -> Optional[bytes]:
    """
    kind: "thumb" or "full"
    """
    client = omero_login()
    if client is None:
        return None

    try:
        if kind == "thumb":
            url = omero_thumbnail_url(image_id)
        else:
            url = omero_full_image_url(image_id)

        resp = client.get('https://nife-dev.cancer.gov/metadata/api/fast-api')
        resp.raise_for_status()
        print(resp.content)
        return resp.content
    except Exception as e:
        print(f"Error fetching OMERO {kind} image for {image_id}: {e}")
        return None
    finally:
        client.close()


# -------------------------------------------------------------------
# Reactive status message
# -------------------------------------------------------------------

status_msg = reactive.Value("Ready. No image requested yet.")

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

        - Shiny (server) logs into OMERO using a service account.
        - Shiny then fetches image data via `/webgateway` and serves it to the browser.
        - The browser never talks directly to OMERO.
        """
    )

with ui.layout_column_wrap(width=1 / 2):
    with ui.card(full_screen=True):
        ui.card_header("Thumbnail (proxied)")
        core_ui.output_image("thumb")

    with ui.card(full_screen=True):
        ui.card_header("Full image (proxied)")
        core_ui.output_image("full_img")

with ui.card():
    ui.card_header("Status")
    core_ui.output_text("status_text")


# -------------------------------------------------------------------
# Server logic
# -------------------------------------------------------------------

@render.text
def status_text() -> str:
    return status_msg()


@render.image
def thumb():
    # Only react when button clicked, but still allow initial value
    _ = input.load_btn()  # to register dependency
    img_id = input.image_id().strip()

    if not img_id:
        status_msg.set("Please enter an image ID.")
        return None

    data = fetch_omero_image(img_id, kind="thumb")

    if data is None:
        status_msg.set("Login or thumbnail fetch failed. Check credentials or network.")
        return None

    status_msg.set(f"Loaded thumbnail for image {img_id}.")
    return {
        "src": io.BytesIO(data),
        "format": "jpeg",
    }


@render.image
def full_img():
    _ = input.load_btn()  # same trigger
    img_id = input.image_id().strip()

    if not img_id:
        return None

    data = fetch_omero_image(img_id, kind="full")

    if data is None:
        # Don't override a more detailed status from thumb()
        return None

    return {
        "src": io.BytesIO(data),
        "format": "jpeg",
    }
