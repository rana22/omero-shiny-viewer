import io
import os
import httpx
from shiny.express import ui, input
from shiny import render, ui as core_ui, reactive

import tempfile

THUMB_TMP_DIR = tempfile.gettempdir()  # or a custom dir you control

DEFAULT_TIMEOUT = 10.0
METADATA_API_URL = os.environ.get(
    "METADATA_API_URL",
    "https://nife-dev.cancer.gov/metadata/api/thumbnail",
)

def fetch_metadata_bytes(image_id) -> bytes | None:
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT, verify=True) as client:
            
            payload = {
                "user": "importer",
                "password": "A)#958hya30r9&*H3r09",
                "image_id": image_id,
            }

            resp = client.post(METADATA_API_URL, json=payload)
            resp.raise_for_status()
            print(resp.content)
            return resp.content          # <-- BYTES, not BytesIO

    except Exception as e:
        print("Error fetching bytes:", e)
        return None

ui.h3("OMERO Image Viewer")

ui.input_text(
    "image_id",
    "Image ID",
    value="11416",
    placeholder="Enter OMERO image ID",
)

ui.input_action_button(
    "search",
    "Search",
)

@render.image
@reactive.event(input.search)
def metadata_response():
    try:
        image_id = int(input.image_id())
    except ValueError:
        return None

    # 1. Get the JPEG bytes from OMERO
    data = fetch_metadata_bytes(image_id)
    print("data =", type(data), len(data))

    if not data:
        return None

    # 2. Write to a temp file
    tmp_path = os.path.join(THUMB_TMP_DIR, "omero_thumb.jpg")
    with open(tmp_path, "wb") as f:
        f.write(data)

    # 3. Return a dict with a *path*, not BytesIO
    return {
        "src": tmp_path,
        "width": "100%",       # optional
        "height": "auto",      # optional
        "alt": "OMERO thumbnail",
    }

IMAGE_URL = "https://picsum.photos/800/500"
OMERO_IMG = "https://nife-dev.cancer.gov/webgateway/render_thumbnail/11422"

ui.h3("Iframe demo (internet image)")

@render.ui
def iframe_view():
    return ui.tags.iframe(
        src=OMERO_IMG,
        style="width: 100%; height: 600px; border: none;",
    )
