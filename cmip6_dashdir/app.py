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
import fsspec
import xarray as xr
import pooch
import cftime
import datetime
from scipy import signal
import pandas as pd

#install zarr
#install gcsfs

models_df = pd.read_csv('models.csv')

var_id = "cl"

#query = "variable_id=='"+var_id+"' & table_id=='"+table_id+"'"
query = "variable_id=='"+var_id+"'"
models_list = models_df.query(query).drop_duplicates(['source_id'])['source_id']

# if we want to use all the models:
model_options = []
for model in models_list:
    model_options.append({"label": model, "value": model})


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

server = Flask(__name__)
app = dash.Dash(
    server=server,
    requests_pathname_prefix='/cmip6demo/',
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,  # because of the tabs, not all callbacks are accessible so we suppress callback exceptions
)

app.layout = html.Div(
    [
        dcc.Markdown(
            '''
            Low Cloud Feedback
            '''
        ),

        #select model
        html.Div(
            [
                dcc.Markdown("""Select Model: """),
                dcc.Dropdown(
                    id="model",
                    options=model_options,
                    value="CESM2",
                    #multi=True,
                ),
            ],
            style={"width": "50%", "display": "inline-block"},
        ),

        #select experiment
        html.Div(
            [
                dcc.Markdown("""Select Experiment: """),
                dcc.Dropdown(
                    id="exp",
                    options=[
                        {"label": "historical", "value": "historical"},
                        {"label": "piControl", "value": "piControl"},
                        {"label": "ssp585", "value": "ssp585"},
                    ],
                    value=["historical"],
                    multi=True,
                ),
            ],
            style={"width": "50%", "display": "inline-block"},
        ),


        #graph
        html.Div(
            [
                dcc.Graph(
                    id="graph",
                    config={
                        "displayModeBar": True,
                    },
                ),
            ],
            style={"width": "100%", "display": "inline-block",},
        ),


    ],
    style={"width": "1000px"},
)


def filter_cloud_cover(cloud_cover, n_years):
    #using average month length for now
    fs = 1/(30.437*24*60*60) #1 month in Hz (sampling frequency)
    nyquist = fs / 2 # 0.5 times the sampling frequency
    cutoff =  1/(n_years*365*24*60*60)# cutoff in Hz, n_years in Hz
    normal_cutoff = cutoff / nyquist
    
    b, a = signal.butter(5, normal_cutoff, btype='lowpass') #low pass filter
    cloud_cover_filt = signal.filtfilt(b, a, cloud_cover)
    return cloud_cover_filt

def get_cloud_fraction(ds):
    cloud_fraction = (1-ds.p).prod(dim='lev')
    return cloud_fraction

@app.callback(
    Output("exp", "options"),
    Input("model", "value"),
)
def update_dropdown(mod_id):
    query = "variable_id=='"+var_id+"' & source_id=='"+mod_id+"'"
    exp_list = models_df.query(query)['experiment_id']

    # if we want to use all the models:
    exp_options = []
    for exp in exp_list:
        exp_options.append({"label": exp, "value": exp})
    
    return exp_options


@app.callback(
    Output("graph", "figure"),
    Input("model", "value"),
    Input("exp", "value"),
)
def update_graph(mod_id, exp_id_list):
    fig = go.Figure()


    for exp_id in exp_id_list:
        query = "variable_id=='"+var_id+"' & source_id=='"+mod_id+"' & experiment_id=='"+exp_id+"'"
        path = models_df.query(query)['path'].iloc[0]
        ds = xr.open_zarr(Path(path))

        #spatial_mean = ds.mean(dim=["lat", "lon", "lev"])
        spatial_mean = ds.mean(dim=["lat", "lon"])
        clear_sky_prob = (1-(spatial_mean.cl/100)).prod(dim='lev').values
        tot_cloud_fraction = 1 - clear_sky_prob

        times = xr.cftime_range(start="1850", periods=len(spatial_mean[var_id]), freq="M", calendar="noleap")
        times = times.shift(-1, "M").shift(16, "D").shift(12, "H")
        
        '''
        if (mod_id == "CESM2") & (exp_id == "ssp585"):
            cloud_cover = spatial_mean[var_id].values*100
        else:
            cloud_cover = spatial_mean[var_id].values
            
        cloud_cover_filt = filter_cloud_cover(cloud_cover, 10)
        '''
        cloud_fraction_filt = filter_cloud_cover(tot_cloud_fraction, 10)

        #fig.add_trace(go.Scatter(x=times, y=cloud_cover_filt, mode="lines", name=exp_id))
        fig.add_trace(go.Scatter(x=times, y=cloud_fraction_filt, mode="lines", name=exp_id))

    fig.update_layout(title=mod_id + ", low level cloud cover, 10 year lowpass filter, eastern pacific", 
        xaxis_title="Time", yaxis_title="Total Cloud Fraction", showlegend=True)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
