from pathlib import Path
from shiny import App, ui, render, reactive

OMERO_LOGIN_URL = "https://nife-dev.cancer.gov/webclient/login/"
OMERO_IFRAME_URL = "https://nife-dev.cancer.gov/webgateway/render_thumbnail/11422"

WWW_DIR = Path(__file__).parent / "www"

app_ui = ui.page_fluid(
    ui.tags.div(id="omero_container"),
    ui.tags.script(src="omero.js")  # this will load from WWW_DIR
)

app = App(
    app_ui,
    server=lambda i, o, s: None,
    static_assets=WWW_DIR
)
