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
    url_base_pathname=environ.get("JUPYTERHUB_SERVICE_PREFIX", "/"),
    external_stylesheets=external_stylesheets,
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
<<<<<<< HEAD
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
=======
def update_learn_plot(forcing, units):
    # check units to get appropriate data
    if units == "C":
        data = land_ocean_data_c
    if units == "F":
        data = land_ocean_data_f

    factors = [forcing]

    # add axis lines
    fig = px.line()
    fig.update_layout(
        plot_bgcolor="rgb(255, 255, 255)",
        yaxis_zeroline=True,
        yaxis_zerolinecolor="gainsboro",
        yaxis_showline=True,
        yaxis_linecolor="gainsboro",
    )

    # plot the forcings on the figure
    fig = update_learn_factors(fig, factors, units)
    # add the observed temperature anomoly line
    figTemp = px.line(
        data, x="Year", y="Annual_Mean", color_discrete_sequence=["black"]
    )
    figTemp.update_traces(hovertemplate="Year: %{x}<br>Annual Mean: %{y:.3f}")
    fig.add_trace(figTemp.data[0])

    # update yaxis based on unit, and add the annotation for observed temperature anomaly
    if units == "C":
        fig.update_yaxes(title="Temperature  Anomaly (ºC)", range=[-1.2, 1.2])
        # annotation
        fig.add_annotation(
            x=2005,
            y=0.938064516129032,
            text="<b>observed<br>temperature anomaly hot IIIIIII reload</b>",
            showarrow=True,
            arrowhead=1,
        )
    elif units == "F":
        fig.update_yaxes(
            title="Temperature  Anomaly (ºF)", range=[-1.2 * 1.8, 1.2 * 1.8]
        )
        # annotation
        fig.add_annotation(
            x=2005,
            y=0.938064516129032 * 1.8,
            text="<b>observed<br>temperature anomaly</b>",
            showarrow=True,
            arrowhead=1,
        )
    return fig


# function to update the student comments as an annotation on the 'explore' plot.
def update_text(fig, text_input):
    text_output = ""
    for chr in text_input:
        if (ord(chr) == 10) | (
            ord(chr) == 13
        ):  # replace 'enter' from the input with '<br>' to make a line break
            text_output += "<br>"
>>>>>>> 5e78b42 (checkpoint)
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
    app.run_server(debug=True)