from os import environ

import dash
import numpy as np
import pandas as pd

import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask


from pathlib import Path

import json
import xarray as xr
import cftime
import datetime
from scipy import signal
import pandas as pd

# zarr and gcsfs must also be installed


models_df = pd.read_csv("models.csv")

# our model list is all the models with the cl variable.
var_id = "cl"
query = "variable_id=='" + var_id + "'"
models_list = models_df.query(query).drop_duplicates(["source_id"])["source_id"]

# if we want to use all the models:
model_options = []  # model options for the dropdown menu
for model in models_list:
    model_options.append({"label": model, "value": model})


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

server = Flask(__name__)
app = dash.Dash(
    server=server,
    #requests_pathname_prefix="/cmip6demo/",
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,  # because of the tabs, not all callbacks are accessible so we suppress callback exceptions
)

app.layout = html.Div(
    [
        dcc.Markdown(
            """
            Low Cloud Feedback
            """
        ),
        # select model
        html.Div(
            [
                dcc.Markdown("""Select Model: """),
                dcc.Dropdown(
                    id="model",
                    options=model_options,
                    value="CESM2",
                ),
            ],
            style={"width": "50%", "display": "inline-block"},
        ),
        # select experiment
        html.Div(
            [
                dcc.Markdown("""Select Experiment: """),
                dcc.Dropdown(
                    id="exp",
                    # hardcoded initial options for the CESM2 model. When the model is changed, the options are updated automatically.
                    options=[
                        {"label": "historical", "value": "historical"},
                        {"label": "piControl", "value": "piControl"},
                        {"label": "abrupt-4xCO2", "value": "abrupt-4xCO2"},
                        {"label": "ssp585", "value": "ssp585"},
                    ],
                    value=["historical"],
                    multi=True,
                ),
            ],
            style={"width": "50%", "display": "inline-block"},
        ),
        # graph
        html.Div(
            [
                dcc.Graph(
                    id="graph",
                    config={
                        "displayModeBar": True,
                    },
                ),
            ],
            style={
                "width": "100%",
                "display": "inline-block",
            },
        ),
    ],
    style={"width": "1000px"},
)


def filter_cloud_cover(cloud_cover, n_years):
    # low pass filter
    fs = 1 / (
        30.437 * 24 * 60 * 60
    )  # 1 month in Hz (sampling frequency). 30.437 is the average month length.
    nyquist = fs / 2  # 0.5 times the sampling frequency
    cutoff = 1 / (n_years * 365 * 24 * 60 * 60)  # cutoff in Hz, n_years in Hz
    normal_cutoff = cutoff / nyquist

    b, a = signal.butter(5, normal_cutoff, btype="lowpass")  # low pass filter
    cloud_cover_filt = signal.filtfilt(b, a, cloud_cover)
    return cloud_cover_filt


@app.callback(
    Output("exp", "options"),
    Output("exp", "value"),
    Input("model", "value"),
    Input("exp", "value"),
)
def update_dropdown(mod_id, old_exp_list):
    # updates the experiment selection dropdown menu depending on the model.
    # find the experiments that correspond to the current model:
    query = "variable_id=='" + var_id + "' & source_id=='" + mod_id + "'"
    new_exp_list = models_df.query(query)["experiment_id"]

    # if we want to use all the experiments:
    exp_options = []  # loop through each experiment and add it to the dropdown options
    for exp in new_exp_list:
        exp_options.append({"label": exp, "value": exp})

    # remove any selected experiments which aren't in the current model
    return_exp_list = list(set(old_exp_list).intersection(set(new_exp_list)))

    return exp_options, return_exp_list


@app.callback(
    Output("graph", "figure"),
    Input("model", "value"),
    Input("exp", "value"),
)
def update_graph(mod_id, exp_id_list):
    fig = go.Figure()

    # loop through each experiment to add to figure
    for exp_id in exp_id_list:
        # read in the zarr
        query = (
            "variable_id=='"
            + var_id
            + "' & source_id=='"
            + mod_id
            + "' & experiment_id=='"
            + exp_id
            + "'"
        )
        path = models_df.query(query)["path"].iloc[0]
        ds = xr.open_zarr(Path(path))

        spatial_mean = ds.mean(dim=["lat", "lon"])  # mean over lat and lon
        clear_sky_prob = (
            (1 - (spatial_mean.cl / 100)).prod(dim="lev").values
        )  # the probability of a clear patch through all the cloud levels
        tot_cloud_fraction = 1 - clear_sky_prob

        times = xr.cftime_range(
            start="0000", periods=len(spatial_mean[var_id]), freq="M", calendar="noleap"
        )  # make a time array that starts at year 0
        times = (
            times.shift(-1, "M").shift(16, "D").shift(12, "H")
        )  # shift the array by 12H so the spacing lines up with the original data.

        cloud_fraction_filt = filter_cloud_cover(
            tot_cloud_fraction, 10
        )  # apply a low pass filter, 10 years, to cloud fraction
        # remove the first 20 years, which are distorted by the filter and by the start-up of the model
        fig.add_trace(
            go.Scatter(
                x=times[0 : -12 * 20],
                y=cloud_fraction_filt[12 * 20 : -1],
                mode="lines",
                name=exp_id,
            )
        )  # add to figure

    fig.update_layout(
        title=mod_id
        + ", low level cloud cover, 10 year lowpass filter, eastern pacific",
        xaxis_title="Time",
        yaxis_title="Total Cloud Fraction",
        showlegend=True,
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
