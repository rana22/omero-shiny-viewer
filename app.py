# from shiny import App, ui, reactive

# # ---- Config ----
# # Base OMERO viewer URL, without the image id
# # Example patterns (you’ll adjust this):
# #   https://omero.example.org/iviewer/?image={image_id}
# #   https://omero.example.org/webclient/img_detail/{image_id}/?show=viewer
# OMERO_VIEWER_BASE = "https://nife-dev.cancer.gov/iviewer/?images=11422"

# from shiny import App, ui, reactive

# # ---- Config ----
# # OMERO_VIEWER_BASE = "https://omero.example.org/iviewer/?image={image_id}"

# # ---- UI ----
# app_ui = ui.page_sidebar(
#     ui.sidebar(
#         ui.input_text(
#             "image_id",
#             "Image ID",
#             value="1",
#             width="100%",
#         ),
#         ui.input_action_button("load_btn", "Load Image"),
#         ui.hr(),
#         ui.input_text(
#             "raw_url",
#             "Or full OMERO viewer URL (overrides Image ID)",
#             value="",
#             width="100%",
#         ),
#         ui.markdown(
#             """
# **Usage**

# - Enter an OMERO image ID and click **Load Image**
# - Or paste a full iviewer URL.
#             """
#         ),
#         width=4,
#     ),

#     # main content
#     ui.layout_columns(
#         ui.card(
#             ui.card_header("OMERO iviewer"),
#             ui.output_ui("viewer_frame"),
#         ),
#         col_widths=[12],
#     ),
# )


# # ---- Server ----
# def server(input, output, session):
#     @reactive.Calc
#     def omero_url():
#         # If user provides a full URL, trust it.
#         raw = input.raw_url().strip()
#         if raw:
#             return raw

#         image_id = input.image_id().strip()
#         if not image_id:
#             return None

#         return OMERO_VIEWER_BASE.format(image_id=image_id)

#     @output
#     @ui.render_ui
#     def omero_view():
#         url = omero_url()
#         if not url:
#             return ui.div("Provide an image ID or URL to view.")

#         return ui.div(
#             ui.tags.iframe(
#                 src=url,
#                 style=(
#                     "width: 100%; "
#                     "background: red;"
#                     "height: 80vh; "
#                     "border: 1px solid #ccc; "
#                     "border-radius: 8px;"
#                 ),
#             )
#         )


# app = App(app_ui, server)


# app_express.py
from shiny.express import input, render, ui

# UI: a single slider
ui.input_slider("n", "N", 0, 100, 20)

# Server: reactive output that shows n*2 as code
@render.code
def txt():
    return f"n*2 is {input.n() * 2}"