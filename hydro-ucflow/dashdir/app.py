# Run this app with `python app.py` and visit http://127.0.0.1:8050/ in your web browser.

# This is the main file. It contains Dash setup and callbacks.

import base64
from os import environ

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask

import plotting as plot

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

server = Flask(__name__)
app = dash.Dash(
    server=server,
    requests_pathname_prefix='/hydro/',
    external_stylesheets=external_stylesheets)

# initial values for dash components
initial_h1 = 35
initial_h2 = 30
initial_K = 1
initial_W = 0.05
initial_L = 800
initial_material = "silty_sand"
initial_arrow_visibility = ["visible"]

# load markdown for the header, introduction, sources.
header = open("header.md", "r")
header_markdown = header.read()
introduction = open("introduction.md", "r")
introduction_markdown = introduction.read()
sources = open("sources.md", "r")
sources_markdown = sources.read()

# load the image in the intro. Following solution here: https://community.plotly.com/t/adding-local-image/4896/4
image_filename = "diagram.png"
encoded_image = base64.b64encode(open(image_filename, "rb").read())

app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Markdown(
                    # markdown for the header
                    children=header_markdown
                ),
            ],
            style={"width": "100%", "margin-left": "200px", "margin-bottom": "20px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Markdown(
                            # markdown for the introduction
                            children=introduction_markdown
                        ),
                    ],
                    style={
                        "width": "60%",
                        "display": "inline-block",
                        "vertical-align": "middle",
                        "margin-left": "20px",
                    },
                ),
                html.Div(
                    [
                        # image added following: https://community.plotly.com/t/adding-local-image/4896/4
                        html.Img(
                            src="data:image/png;base64,{}".format(
                                encoded_image.decode()
                            ),
                            style={"width": "400px"},
                        )
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "vertical-align": "middle",
                    },
                ),
            ],
            style={"width": "100%"},
        ),
        html.Div(
            [
                dcc.Markdown(
                    """
            ------
            """
                ),
            ],
            style={
                "width": "100%",
                "display": "inline-block",
                "padding": "0 20",
                "vertical-align": "middle",
                "margin-bottom": 30,
                "margin-right": 50,
                "margin-left": 20,
            },
        ),
        html.Div(
            [
                # Dash Sliders: https://dash.plotly.com/dash-core-components/slider
                dcc.Markdown(
                    id="h1_label",
                    children=""" Left side head: **_h1_ = """
                    + str(initial_h1)
                    + """m**""",
                ),
                dcc.Slider(
                    id="h1",
                    min=1,
                    max=50,
                    step=0.5,
                    value=initial_h1,
                    marks={1: "1", 10: "10", 20: "20", 30: "30", 40: "40", 50: "50"},
                ),
                dcc.Markdown(
                    id="K_label",
                    children=""" Hydraulic conductivity: **_K_ = """
                    + str(10 ** initial_K)
                    + """m/day**""",
                    style={"margin-top": "20px"},
                ),
                dcc.Slider(
                    # K is a logarithmic slider, so the input values are actually n, where K = 10^n
                    id="K",
                    min=-2,
                    max=2,
                    step=0.01,
                    value=initial_K,
                    marks={
                        -2: "10\u207B\u00B2",
                        -1: "10\u207B\u00B9",
                        0: "1",
                        1: "10",
                        2: "10\u00B2",
                    },
                ),
                dcc.Markdown(
                    id="L_label",
                    children=""" Profile length: **_L_ = """
                    + str(initial_L)
                    + """m**""",
                    style={"margin-top": "20px"},
                ),
                dcc.Slider(
                    id="L",
                    min=100,
                    max=800,
                    step=5,
                    value=initial_L,
                    marks={
                        100: "100",
                        200: "200",
                        300: "300",
                        400: "400",
                        500: "500",
                        600: "600",
                        700: "700",
                        800: "800",
                    },
                ),
            ],
            style={"width": "37%", "display": "inline-block", "vertical-align": "top"},
        ),
        html.Div(
            [
                dcc.Markdown(
                    id="h2_label",
                    children=""" Right side head: **_h2_ = """
                    + str(initial_h2)
                    + """m**""",
                ),
                dcc.Slider(
                    id="h2",
                    min=1,
                    max=50,
                    step=0.5,
                    value=initial_h2,
                    marks={1: "1", 10: "10", 20: "20", 30: "30", 40: "40", 50: "50"},
                ),
                dcc.Markdown(
                    id="W_label",
                    children=""" Recharge: **_W_ = """ + str(initial_W) + """m/day**""",
                    style={"margin-top": "20px"},
                ),
                dcc.Slider(
                    id="W",
                    min=-0.05,
                    max=0.1,
                    step=0.01,
                    value=initial_W,
                    marks={-0.05: "-0.05", 0: "0.0", 0.05: "0.05", 0.1: "0.1"},
                ),
            ],
            style={"width": "37%", "display": "inline-block", "vertical-align": "top"},
        ),
        html.Div(
            [
                dcc.Markdown(""" **Material:** """),
                dcc.RadioItems(
                    # Dash Radiobuttons: https://dash.plotly.com/dash-core-components/radioitems
                    id="material",
                    options=[
                        {
                            "label": "Silt, Loess (10\u207B\u2074 < K < 1)",
                            "value": "silt",
                        },
                        {
                            "label": "Silty Sand (10\u207B\u00B2 < K < 10\u00B2)",
                            "value": "silty_sand",
                        },
                        {
                            "label": "Clean Sand (10\u207B\u00B9 < K < 10\u00B3)",
                            "value": "clean_sand",
                        },
                        {
                            "label": "Gravel (10\u00B2 < K < 10\u2075)",
                            "value": "gravel",
                        },
                    ],
                    value=initial_material,
                    style={"margin-bottom": "20px"},
                ),
                dcc.Markdown(""" **Flow Arrows:** """),
                dcc.Checklist(
                    # check box for whether or not to display flow arrows.
                    id="arrow_visibility",
                    options=[
                        {"label": "arrows visible", "value": "visible"},
                    ],
                    value=initial_arrow_visibility,
                    style={"margin-bottom": "50px"},
                ),
                html.Button(
                    "Reset", id="reset_button"
                ),  # Dash Buttons: https://dash.plotly.com/dash-html-components/button
            ],
            style={"width": "26%", "display": "inline-block", "vertical-align": "top"},
        ),
        html.Div(
            [
                dcc.Graph(
                    id="elevation_plot",
                    config={
                        "staticPlot": True,
                        "doubleClick": "reset",
                        "showTips": True,
                        "displayModeBar": False,
                        "watermark": True,
                        "modeBarButtonsToRemove": ["pan2d", "select2d", "lasso2d"],
                    },
                ),
                dcc.Graph(
                    id="q_plot",
                ),
            ],
            style={"width": "100%", "display": "inline-block"},
        ),
        html.Div(
            [
                dcc.Markdown(
                    # markdown for sources.
                    children=sources_markdown
                ),
            ],
            style={
                "width": "100%",
                "display": "inline-block",
                "padding": "0 20",
                "vertical-align": "middle",
                "margin-bottom": 30,
                "margin-right": 50,
                "margin-left": 20,
            },
        ),
    ],
    style={"width": "1000px"},
)


# initialize plots
elevation_plot = plot.initialize_elevation_plot(
    initial_h1,
    initial_h2,
    (10 ** initial_K),
    initial_W,
    initial_L,
    initial_arrow_visibility,
)
q_plot = plot.initialize_q_plot(
    initial_h1, initial_h2, (10 ** initial_K), initial_W, initial_L
)


# updating slider labels. Everytime a value is changed, the text above the slider is updated here.
@app.callback(
    Output(component_id="h1_label", component_property="children"),
    Input(component_id="h1", component_property="value"),
)
def update_h1_label(h1):
    return """ Left side head: **_h1_ = """ + str(h1) + """m**"""


@app.callback(
    Output(component_id="h2_label", component_property="children"),
    Input(component_id="h2", component_property="value"),
)
def update_h2_label(h2):
    return """ Right side head: **_h2_ = """ + str(h2) + """m**"""


@app.callback(
    Output(component_id="K_label", component_property="children"),
    Input(component_id="K", component_property="value"),
)
def update_K_label(
    K,
):  # hydraulic conductivity is logarithmic, so we update the value before displaying.
    return """ Hydraulic conductivity: **_K_ = """ + str(10 ** K)[:4] + """m/day**"""


@app.callback(
    Output(component_id="W_label", component_property="children"),
    Input(component_id="W", component_property="value"),
)
def update_W_label(W):
    return """ Recharge: **_W_ = """ + str(W) + """m/day**"""


@app.callback(
    Output(component_id="L_label", component_property="children"),
    Input(component_id="L", component_property="value"),
)
def update_L_label(L):
    return """ Profile length: **_L_ = """ + str(L) + """m**"""


@app.callback(
    Output(component_id="K", component_property="min"),
    Output(component_id="K", component_property="max"),
    Output(component_id="K", component_property="marks"),
    Input(component_id="material", component_property="value"),
)
def update_K_bounds(material):  # update values for K based on the ground material
    if material == "silt":
        return (
            -4,
            0,
            {
                -4: "10\u207B\u2074",
                -3: "10\u207B\u00B3",
                -2: "10\u207B\u00B2",
                -1: "10\u207B\u00B9",
                0: "1",
            },
        )
    elif material == "silty_sand":
        return (
            -2,
            2,
            {
                -2: "10\u207B\u00B2",
                -1: "10\u207B\u00B9",
                0: "1",
                1: "10",
                2: "10\u00B2",
            },
        )
    elif material == "clean_sand":
        return (
            -1,
            3,
            {-1: "10\u207B\u00B9", 0: "1", 1: "10", 2: "10\u00B2", 3: "10\u00B3"},
        )
    elif material == "gravel":
        return 2, 5, {2: "10\u00B2", 3: "10\u00B3", 4: "10\u2074", 5: "10\u2075"}


@app.callback(
    Output(component_id="elevation_plot", component_property="figure"),
    Input(component_id="h1", component_property="value"),
    Input(component_id="h2", component_property="value"),
    Input(component_id="K", component_property="value"),
    Input(component_id="W", component_property="value"),
    Input(component_id="L", component_property="value"),
    Input(component_id="arrow_visibility", component_property="value"),
)
def update_elevation_plot(h1, h2, K, W, L, arrow_visibility):
    # update the elevation plot by calling a function in the plotting file. Note since K is logarithmic, we pass 10^K.
    fig = plot.update_elevation_plot(
        h1, h2, (10 ** (K)), W, L, arrow_visibility, elevation_plot
    )
    return fig


@app.callback(
    Output(component_id="q_plot", component_property="figure"),
    Input(component_id="h1", component_property="value"),
    Input(component_id="h2", component_property="value"),
    Input(component_id="K", component_property="value"),
    Input(component_id="W", component_property="value"),
    Input(component_id="L", component_property="value"),
)
def update_q_plot(h1, h2, K, W, L):
    # update the q plot by calling a function in the plotting file. Note since K is logarithmic, we pass 10^K.
    fig = plot.update_q_plot(h1, h2, (10 ** (K)), W, L, q_plot)
    return fig


@app.callback(
    Output(component_id="h1", component_property="value"),
    Output(component_id="h2", component_property="value"),
    Output(component_id="K", component_property="value"),
    Output(component_id="W", component_property="value"),
    Output(component_id="L", component_property="value"),
    Output(component_id="arrow_visibility", component_property="value"),
    Output(component_id="material", component_property="value"),
    Input(component_id="reset_button", component_property="n_clicks"),
)
def reset_page(n_clicks):
    # when the reset button is pressed, we change all the parameters to their initial values.
    return (
        initial_h1,
        initial_h2,
        initial_K,
        initial_W,
        initial_L,
        initial_arrow_visibility,
        initial_material,
    )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
