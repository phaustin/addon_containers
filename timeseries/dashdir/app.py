# -*- coding: utf-8 -*-

# Run this app with `python app3.py` and
# visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/

# based on app3.py and ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line

from os import environ

import dash
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask
from numpy import random

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

server = Flask(__name__)
app = dash.Dash(
    server=server,
    url_base_pathname=environ.get("JUPYTERHUB_SERVICE_PREFIX", "/"),
    external_stylesheets=external_stylesheets,
)

#reading in md files for instructions, etc.
purpose = open("purpose.md", "r")
purpose_markdown = purpose.read()

instructions = open("instructions.md", "r")
instructions_markdown = instructions.read()

app.layout = html.Div(
    [
        dcc.Markdown(children=purpose_markdown), #display the md files we read in
        dcc.Markdown(children=instructions_markdown),
        # slider or checklist details at https://dash.plotly.com/dash-core-components
        # checkbox can be lumped together but then logic in "update_graph" is messier.
        # Content can be delivered using html, but markdown is simpler.
        html.Div(
            [
                dcc.Markdown(
                    """
        **Select signal components**
        """
                ),
                dcc.Checklist(
                    id="signal_components",
                    options=[
                        {"label": "SineWave", "value": "sine"},
                        {"label": "Noise", "value": "noise"},
                        {"label": "Trend", "value": "trend"},
                    ],
                    value=["sine"],
                    style={"margin-bottom": "20px"},
                ),
                dcc.Markdown(
                    """
        **Check to show smoothed**
        """
                ),
                dcc.Checklist(
                    id="smooth_checkbox",
                    options=[{"label": "Smoothed", "value": "smooth"}],
                    value=[],
                    style={"margin-bottom": "20px"},
                ),
                dcc.Markdown(
                    """
        **Trend angle (degrees)**
        """
                ),
                dcc.Slider(
                    id="trend_angle",
                    min=0,
                    max=45,
                    value=45,
                    step=0.5,
                    marks={0: "0", 15: "15", 30: "30", 45: "45"},
                    tooltip={"always_visible": True, "placement": "topLeft"},
                ),
            ],
            style={
                "width": "48%",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("No. cycles:"),
                        dcc.Slider(
                            id="ncycles",
                            min=1,
                            max=10,
                            value=3,
                            step=0.5,
                            marks={
                                1: "1",
                                2: "2",
                                3: "3",
                                4: "4",
                                5: "5",
                                6: "6",
                                7: "7",
                                8: "8",
                                9: "9",
                                10: "10",
                            },
                            tooltip={"always_visible": True, "placement": "topLeft"},
                        ),
                    ],
                    style={"margin-bottom": "20px"},
                ),
                html.Div(
                    [
                        html.Label("Noise level"),
                        dcc.Slider(
                            id="noiselevel",
                            min=0.0,
                            max=3.0,
                            value=1.0,
                            step=0.25,
                            marks={0: "0", 1: "1", 2: "2", 3: "3"},
                            tooltip={"always_visible": True, "placement": "topLeft"},
                        ),
                    ],
                    style={"margin-bottom": "20px"},
                ),
                html.Label("N-pt smoothing"),
                dcc.Slider(
                    id="smoothwin",
                    min=1.0,
                    max=15.0,
                    value=5.0,
                    step=2.0,
                    marks={
                        1: "1",
                        3: "3",
                        5: "5",
                        7: "7",
                        9: "9",
                        11: "11",
                        13: "13",
                        15: "15",
                    },
                    tooltip={"always_visible": True, "placement": "topLeft"},
                ),
            ],
            style={
                "width": "48%",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
        dcc.Graph(id="indicator-graphic"),
    ],
    style={"width": "900px"},
)


def moving_avg(x, w):
    y = np.convolve(x, np.ones(w), "valid") / w

    # applying "roll" is necessary so the timeseries are aligned over the correct x-axis values.
    # this is probably easier using data frames when x-axis will be the index frame.
    z = np.roll(y, int(w / 2))

    # roll wraps end points back to first points, so set these to zero; a cludge, but works for now.
    wrap = int((w) / 2)
    z[:wrap] = 0
    return z


# The callback function with it's app.callback wrapper.
@app.callback(
    Output("indicator-graphic", "figure"),
    Input("ncycles", "value"),
    Input("noiselevel", "value"),
    Input("smoothwin", "value"),
    Input("signal_components", "value"),
    Input("smooth_checkbox", "value"),
    Input("trend_angle", "value"),
)
def update_graph(
    ncycles, noiselevel, smoothwin, signal_components, smooth_checkbox, trend_angle
):
    # make a noisy sine wave on a linear trend
    # build the X-axis first, then the three time series:
    xpoints = np.arange(0, ncycles + 0.05, 0.05)
    N = len(xpoints)  # this may not be the most sophisticated approach
    ypoints = np.sin(xpoints * 2 * np.pi)
    randpoints = 2 * noiselevel * (random.rand(N) - 0.5) #the noise level corresponds to the amplitude
    slope = np.tan(trend_angle * (np.pi / 180))
    trendpoints = slope * xpoints 

    a1 = a2 = a3 = 0
    if "sine" in signal_components:
        a1 = 1
    if "noise" in signal_components:
        a2 = 1
    if "trend" in signal_components:
        a3 = 1

    if a1 or a2 or a3:
        sumpoints = a1 * ypoints + a2 * randpoints + a3 * trendpoints
    else:
        sumpoints = []

    if smooth_checkbox == ["smooth"]:
        smoothpoints = moving_avg(sumpoints, smoothwin)
    else:
        smoothpoints = []

    # constructing the figure more directly than using plotly.express
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=xpoints,
            y=sumpoints,
            mode="lines",
            name="signal",
            marker=dict(
                color="DodgerBlue",
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=xpoints,
            y=smoothpoints,
            mode="lines",
            name="smoothed",
            marker=dict(
                color="DarkOrange",
            ),
        )
    )

    fig.update_layout(xaxis_title="Time", yaxis_title="Value")
    fig.update_xaxes(range=[0, 10])
    fig.update_yaxes(range=[-2, 7])

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
