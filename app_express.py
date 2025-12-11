import io
import os
import httpx
from shiny.express import ui, input
from shiny import render, ui as core_ui




# ui.page_opts(title="OMERO image via FastAPI", fillable=True)

# with ui.card():
#     ui.card_header("Image from OMERO FastAPI")
#     core_ui.output_image("omero_img")     # <-- image output


# @render.image
# def omero_img():
#     data = fetch_metadata_bytes()
#     print("data =", type(data), len(data) if data else None)

#     if not data:
#         return None

#     return {
#         "src": data,          # <-- wrap BYTES once
#         "format": "jpeg",
#     }

import tempfile


THUMB_TMP_DIR = tempfile.gettempdir()  # or a custom dir you control

# def fetch_omero_thumb_bytes() -> bytes:
#     # your existing httpx / OMERO call; just returns bytes
#     data = ...  # <- thumb_bytes
#     return data

DEFAULT_TIMEOUT = 10.0
METADATA_API_URL = os.environ.get(
    "METADATA_API_URL",
    "https://nife-dev.cancer.gov/metadata/api/fast-api",
)

def fetch_metadata_bytes() -> bytes | None:
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT, verify=True) as client:
            OMERO_USERNAME = os.environ.get("OMERO_USERNAME")
            OMERO_PASSWORD = os.environ.get("OMERO_PASSWORD")
            payload = {
                "user": OMERO_USERNAME,
                "password": OMERO_PASSWORD,
                "image_id": 11422,
            }
            resp = client.post(METADATA_API_URL, json=payload)
            resp.raise_for_status()
            print(resp.content)
            return resp.content          # <-- BYTES, not BytesIO
    except Exception as e:
        print("Error fetching bytes:", e)
        return None

@render.image
def metadata_response():
    # 1. Get the JPEG bytes from OMERO
    data = fetch_metadata_bytes()
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
