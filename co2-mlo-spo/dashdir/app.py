#### Exploring linear models for prediction
# -*- coding: utf-8 -*-

# Run this app with `python app3.py` and
# visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/

# based on ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line

import datetime
from os import environ

import dash
import numpy as np
import pandas as pd
# plotly express could be used for simple applications
# but this app needs to build plotly graph components separately
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask
from plotly.subplots import make_subplots

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

server = Flask(__name__)
app = dash.Dash(
    server=server,
    url_base_pathname=environ.get("JUPYTERHUB_SERVICE_PREFIX", "/"),
    external_stylesheets=external_stylesheets,
)

##################################
# Fetch and prep the data
# read in the data from the prepared CSV file.
# Mauna Loa data
mlo_data_source = "data/monthly_in_situ_co2_mlo.csv"
mlo_data_full = pd.read_csv(
    mlo_data_source, skiprows=np.arange(0, 56), na_values="-99.99"
)

mlo_data_full.columns = [
    "year",
    "month",
    "date_int",
    "date",
    "raw_co2",
    "seasonally_adjusted",
    "fit",
    "seasonally_adjusted_fit",
    "co2 filled",
    "seasonally_adjusted_filled",
]

# for handling NaN's see https://pandas.pydata.org/pandas-docs/stable/user_guide/missing_data.html
mlo_data = mlo_data_full.dropna()

# South Pole data
spo_data_source = "data/monthly_merge_co2_spo.csv"
spo_data_full = pd.read_csv(
    spo_data_source, skiprows=np.arange(0, 58), na_values="      NaN"
)

spo_data_full.columns = [
    "year",
    "month",
    "date_int",
    "date",
    "raw_co2",
    "seasonally_adjusted",
    "fit",
    "seasonally_adjusted_fit",
    "co2 filled",
    "seasonally_adjusted_filled",
]

spo_data = spo_data_full.dropna()

# A linear model with slope and intercept to predict CO2
def predict_co2(slope, intercept, initial_date, prediction_date):
    a = slope * (prediction_date - initial_date) + intercept

    return a


# read in markdown files for instructions, sources, etc.
instructions = open("instructions.md", "r")
instructions_markdown = instructions.read()

example_activity = open("example-activity.md", "r")
example_activity_markdown = example_activity.read()

sources = open("sources.md", "r")
sources_markdown = sources.read()

##################################
# Lay out the page
app.layout = html.Div(
    [
        # Introduction
        dcc.Markdown(
            children=instructions_markdown  # display the instructions markdown file
        ),
        # controls for plot
        # checklist to choose what is being plotted
        html.Div(
            [
                dcc.Markdown(""" **_Data Source:_** """),
                dcc.Checklist(
                    id="data_type",
                    options=[
                        {"label": "raw Mauna Loa data", "value": "mlo"},
                        {"label": "raw South Pole data", "value": "spo"},
                        {"label": "adjustable straight line", "value": "fit"},
                    ],
                    value=["mlo"],
                ),
            ],
            style={"width": "40%", "display": "inline-block", "vertical-align": "top"},
        ),
        # selecting which month(s) to plot
        html.Div(
            [
                dcc.Markdown(""" **_Select Month:_** """),
                dcc.Dropdown(
                    id="month_selection",
                    options=[
                        {"label": "All", "value": "all"},
                        {"label": "January", "value": 1},
                        {"label": "February", "value": 2},
                        {"label": "March", "value": 3},
                        {"label": "April", "value": 4},
                        {"label": "May", "value": 5},
                        {"label": "June", "value": 6},
                        {"label": "July", "value": 7},
                        {"label": "August", "value": 8},
                        {"label": "September", "value": 9},
                        {"label": "October", "value": 10},
                        {"label": "November", "value": 11},
                        {"label": "December", "value": 12},
                    ],
                    value=["all"],
                    multi=True,
                ),
            ],
            style={"width": "60%", "display": "inline-block", "vertical-align": "top"},
        ),
        # slider to select the y limits on the graph
        html.Div(
            [
                dcc.RangeSlider(
                    id="ylim_slider",
                    min=300,
                    max=450,
                    step=1.0,
                    marks={
                        300: "300",
                        350: "350",
                        400: "400",
                        450: "450",
                    },
                    value=[300, 450],
                    vertical=True,
                    verticalHeight=270,
                ),
            ],
            style={
                "width": "5%",
                "margin-left": "5px",
                "margin-top": "20px",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
        html.Div(
            [
                dcc.Graph(
                    id="graph",
                    config={
                        "displayModeBar": True,
                        #'modeBarButtonsToRemove': ['select', 'lasso2d', 'resetScale'],
                    },
                ),
            ],
            style={
                "width": "93%",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
        # range slider to choose x limits on the graph
        html.Div(
            [
                dcc.RangeSlider(
                    id="xlim_slider",
                    min=1957,
                    max=2021,
                    step=1.0,
                    marks={
                        1957: "1957",
                        # 1960: '1960',
                        1970: "1970",
                        1980: "1980",
                        1990: "1990",
                        2000: "2000",
                        2010: "2010",
                        # 2020: '2020',
                        2021: "2021",
                    },
                    value=[1957, 2021],
                ),
            ],
            style={"width": "76%", "margin-left": "60px", "display": "inline-block"},
        ),
        # fitting controls
        html.Div(
            [
                dcc.Markdown(""" **_Slope:_** """),
                dcc.Slider(
                    id="line_slope",
                    min=0,
                    max=3,
                    step=0.02,
                    value=2,
                    marks={
                        0: "0",
                        0.5: "0.5",
                        1: "1",
                        1.5: "1.5",
                        2: "2",
                        2.5: "2.5",
                        3: "3",
                    },
                    tooltip={"always_visible": True, "placement": "topLeft"},
                ),
            ],
            style={"width": "48%", "display": "inline-block"},
        ),
        html.Div(
            [
                dcc.Markdown(""" **_Intercept:_** """),
                dcc.Slider(
                    id="line_intcpt",
                    min=220,
                    max=320,
                    step=0.2,
                    value=312,
                    marks={
                        220: "220",
                        240: "240",
                        260: "260",
                        280: "280",
                        300: "300",
                        320: "320",
                    },
                    tooltip={"always_visible": True, "placement": "topLeft"},
                ),
            ],
            style={"width": "48%", "display": "inline-block", "margin-bottom": "20px"},
        ),
        html.Div(
            [
                dcc.Markdown(""" **_Prediction Year:_** """),
                dcc.Input(
                    id="predict_input",
                    type="number",
                    min=1960,
                    max=2030,
                    step=1,
                    value=2030,
                ),
                dcc.Markdown(id="prediction"),
            ],
            style={"width": "40%", "display": "inline-block", "vertical-align": "top"},
        ),
        # long generic survey
        # html.Iframe(src="https://ubc.ca1.qualtrics.com/jfe/form/SV_3yiBycgV0t8YhCu", style={"height": "800px", "width": "100%"}),
        # short generic survey:
        # html.Iframe(src="https://ubc.ca1.qualtrics.com/jfe/form/SV_9zS1U0C7odSt76K", style={"height": "800px", "width": "100%"}),
        # example activity markdown
        dcc.Markdown(children=example_activity_markdown),
        # closing text
        dcc.Markdown(children=sources_markdown),
    ],
    style={"width": "900px"},
)

# end of layout and definition of controls.
##################################

# The callback function with it's app.callback wrapper.
@app.callback(
    Output("graph", "figure"),
    Output("prediction", "children"),
    Input("line_slope", "value"),
    Input("line_intcpt", "value"),
    Input("data_type", "value"),
    Input("month_selection", "value"),
    Input("xlim_slider", "value"),
    Input("ylim_slider", "value"),
    Input("predict_input", "value"),
)
def update_graph(
    line_slope,
    line_intcpt,
    data_type,
    month_selection,
    xlim_slider,
    ylim_slider,
    predict_input,
):
    # construct all the figure's components
    plot = go.Figure()

    if "all" in month_selection:
        mlo_data_plot = mlo_data
        spo_data_plot = spo_data
    else:
        # https://stackoverflow.com/questions/12096252/use-a-list-of-values-to-select-rows-from-a-pandas-dataframe
        mlo_data_plot = mlo_data[
            mlo_data.month.isin(month_selection)
        ]  # selecting data corresponding to the selected months
        spo_data_plot = spo_data[spo_data.month.isin(month_selection)]

    l1 = line_slope * (spo_data.date - np.min(spo_data.date)) + line_intcpt

    # plot the co2 data
    if "mlo" in data_type:
        plot.add_trace(
            go.Scatter(
                x=mlo_data_plot.date,
                y=mlo_data_plot.raw_co2,
                mode="markers",
                line=dict(color="DodgerBlue"),
                name="CO_2 - Mauna Loa".ljust(20, " "),
            )
        )
    if "spo" in data_type:
        plot.add_trace(
            go.Scatter(
                x=spo_data_plot.date,
                y=spo_data_plot.raw_co2,
                mode="markers",
                line=dict(color="DarkOrange"),
                name="CO_2 - South Pole".ljust(20, " "),
            )
        )
    if "fit" in data_type:
        plot.add_trace(
            go.Scatter(
                x=spo_data.date,
                y=l1,
                mode="lines",
                line=dict(color="#525252"),
                name="adjustable straight<br>line",
            )
        )

    plot.update_layout(xaxis_title="Year", yaxis_title="ppm")
    plot.update_layout(showlegend=True)
    plot.update_layout(margin_l=0)

    # update x limits and y limits from sliders
    plot.update_xaxes(range=[xlim_slider[0], xlim_slider[1]])
    plot.update_yaxes(range=[ylim_slider[0], ylim_slider[1]])

    plot.layout.title = "CO_2 Concentration vs. Time"

    # update prediction text
    predicted_co2 = predict_co2(line_slope, line_intcpt, 1957, predict_input)
    predict_co2_text = f"Predicted CO_2 for {predict_input}: {predicted_co2:1.2f} ppm."

    return plot, predict_co2_text


if __name__ == "__main__":
    app.run_server(debug=True)
