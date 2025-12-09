import io
import os
from typing import Optional, Dict, Any

import httpx
from shiny.express import ui, input, render
from shiny import reactive

# -------------------------------------------------------------------
# Config from environment
# -------------------------------------------------------------------
OMERO_BASE = os.environ.get("OMERO_BASE", "https://nife-dev.cancer.gov")
OMERO_USERNAME = os.environ.get("OMERO_USERNAME")
OMERO_PASSWORD = os.environ.get("OMERO_PASSWORD")
DEFAULT_TIMEOUT = 10.0

# OMERO endpoints – adjust if you use omero_plus vs webclient login
OMERO_LOGIN_URL = f"{OMERO_BASE}/omero_plus/login/"
OMERO_THUMBNAIL_URL = f"{OMERO_BASE}/webgateway/render_thumbnail/{{image_id}}/"
OMERO_FULL_URL = f"{OMERO_BASE}/webgateway/render_image/{{image_id}}/"

# -------------------------------------------------------------------
# Global-ish state: store session + status in Shiny reactives
# -------------------------------------------------------------------
session_client: reactive.Value[Optional[httpx.Client]] = reactive.Value(None)
login_status: reactive.Value[str] = reactive.Value("Not logged in.")


def _make_client() -> httpx.Client:
    # verify=False here only if needed for internal certs; otherwise remove.
    return httpx.Client(
        timeout=DEFAULT_TIMEOUT,
        verify=False,
        follow_redirects=True,
    )


def omero_login() -> bool:
    """
    Try to log in to OMERO using OMERO_USERNAME/OMERO_PASSWORD.
    Returns True if login is (likely) successful, False otherwise.
    Updates session_client and login_status reactives.
    """

    if not OMERO_USERNAME or not OMERO_PASSWORD:
        login_status.set("ERROR: OMERO_USERNAME or OMERO_PASSWORD is not set.")
        session_client.set(None)
        return False

    client = _make_client()

    try:
        # 1) Get login page to pick up CSRF token cookie if needed
        resp = client.get(OMERO_LOGIN_URL)
        resp.raise_for_status()

        # 2) POST credentials. The exact form fields depend on your OMERO Plus config.
        #    Adjust these names if your login form uses different fields.
        data = {
            "username": OMERO_USERNAME,
            "password": OMERO_PASSWORD,
            "server": "1",
            "url": "/",  # redirect target after login; can be anything
        }

        post_resp = client.post(OMERO_LOGIN_URL, data=data)
        post_resp.raise_for_status()

        # Heuristic: if we're still on a login URL or see "login" in URL, assume failure.
        if "login" in str(post_resp.url):
            login_status.set("ERROR: OMERO login failed (still on login page).")
            session_client.set(None)
            return False

        # If we got here, assume success.
        login_status.set(f"Logged in to OMERO as '{OMERO_USERNAME}'.")
        session_client.set(client)
        return True

    except Exception as e:
        login_status.set(f"ERROR logging in to OMERO: {e}")
        session_client.set(None)
        return False


def fetch_image_bytes(image_id: str, full: bool = False) -> Optional[bytes]:
    """
    Ensure we have a logged-in OMERO session, then fetch thumbnail or full image.
    Returns raw bytes or None on error; sets login_status with error info.
    """
    client = session_client.get()

    # If no client yet, try to login first.
    if client is None:
        ok = omero_login()
        if not ok:
            return None
        client = session_client.get()
        if client is None:
            return None

    # Build URL
    if full:
        url = OMERO_FULL_URL.format(image_id=image_id)
    else:
        url = OMERO_THUMBNAIL_URL.format(image_id=image_id)

    try:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        login_status.set(f"ERROR fetching image {image_id}: {e}")
        return None


# -------------------------------------------------------------------
# UI (express)
# -------------------------------------------------------------------

ui.page_opts(title="OMERO Shiny Login + Proxy Viewer", fillable=True)

with ui.sidebar(open="open"):
    ui.input_text(
        "image_id",
        "OMERO Image ID",
        value="11422",
        width="100%",
    )
    ui.input_action_button("load_btn", "Login + Load Image", width="100%")
    ui.hr()
    ui.output_text("status_text")

with ui.layout_column_wrap(width=1 / 2):
    with ui.card(full_screen=True):
        ui.card_header("Thumbnail (via OMERO session)")
        ui.output_image("thumb")

    with ui.card(full_screen=True):
        ui.card_header("Full Image (via OMERO session)")
        ui.output_image("full_img")


# -------------------------------------------------------------------
# Server logic
# -------------------------------------------------------------------

# Show current login / error status
@render.text
def status_text() -> str:
    return login_status.get()


# Trigger login + fetch when button is clicked
@render.image
def thumb() -> Optional[Dict[str, Any]]:
    # Only do work when user clicks the button
    if input.load_btn() < 1:
        return None

    img_id = input.image_id().strip()
    if not img_id:
        login_status.set("Please enter an OMERO image ID.")
        return None

    data = fetch_image_bytes(img_id, full=False)
    if data is None:
        # Error message already set in login_status
        return None

    return {
        "src": io.BytesIO(data),
        "format": "jpeg",
    }


@render.image
def full_img() -> Optional[Dict[str, Any]]:
    if input.load_btn() < 1:
        return None

    img_id = input.image_id().strip()
    if not img_id:
        return None

    data = fetch_image_bytes(img_id, full=True)
    if data is None:
        return None

    return {
        "src": io.BytesIO(data),
        "format": "jpeg",
    }
