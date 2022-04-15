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
    ],
        '''
        #select model
        html.Div(
            [
                dcc.Markdown("""Select Model: """),
                dcc.Dropdown(
                    id="model",
                    options=[
                        {'label': 'New York City', 'value': 'NYC'},
                        {'label': 'Montreal', 'value': 'M'},
                        {'label': 'San Francisco', 'value': 'SF'},
                    ],
                    value="NYC",
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
        '''

    #],
    #style={"width": "1000px"},
)


'''
@app.callback(
    Output("graph", "figure"),
    Input("model", "value"),
)
def update_graph(mod_id):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=np.linspace(0, 100, 1000), y=np.linspace(0, 100, 1000), mode="lines"))

    fig.update_layout(title=mod_id + ", low level cloud cover, 10 year lowpass filter, eastern pacific", 
        xaxis_title="Time", yaxis_title="Total Cloud Fraction", showlegend=True)

    return fig
'''


if __name__ == "__main__":
    app.run_server(debug=True)
