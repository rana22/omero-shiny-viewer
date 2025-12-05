# app_express.py
from shiny import reactive
from shiny.express import input, render, ui

# Page options (optional but nice)
ui.page_opts(title="Random Image iFrame Demo")

# --- Existing example: slider + text -----------------------------------------
ui.input_slider("n", "N", 0, 100, 20)


@render.code
def txt():
    return f"n*2 is {input.n() * 2}"


# --- New section: random image iframe ----------------------------------------

ui.hr()
ui.h3("Random image in an iframe")

# Button to change image
ui.input_action_button("next_img", "Next image")

ui.br()

# Reactive URL that depends on button clicks
@reactive.calc
def img_url() -> str:
    # each click changes the seed → new random image
    click_count = input.next_img()
    # use click_count as the seed so each press gives a new URL
    return f"https://picsum.photos/seed/{click_count}/800/400"

OMERO_VIEWER_BASE = "https://nife-dev.cancer.gov/iviewer/?images=11422"
# Render an iframe pointing to that URL
@render.ui
def image_frame():
    return ui.tags.iframe(
        src=OMERO_VIEWER_BASE,
        style="width: 100%; height: 400px; border: none;",
        title="Random image viewer",
    )
