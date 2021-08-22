# -*- coding: utf-8 -*-

# Run this app with `python app.py` and visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/
# based on ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# mouse-over or 'hover' behavior is based on https://dash.plotly.com/interactive-graphing
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line
# Mapmaking code initially learned from https://plotly.com/python/mapbox-layers/.


from flask import Flask
from os import environ

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotting as plot


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)

app = dash.Dash(__name__,server=server,
                requests_pathname_prefix='/hydro/',
                external_stylesheets=external_stylesheets)

#initial parameter values
initial_h1 = 35
initial_h2 = 30
initial_K = 50
initial_W = 0.05
initial_L = 800
initial_material = 'silty_sand'
initial_arrow_visibility = ['visible']

app.layout = html.Div([
    html.Div([
        dcc.Markdown('''
            ### EOSC 325: Unconfined Flow with Recharge
            
            Explore **unconfined** flow between two points (or water bodies) each with known hydraulic head for differente aquifer materials. 
            See "Sources" below for the origin and inspiration of this app.

            * Set "measured" hydraulic head at left and right sides of the 2D section with sliders h1 and h2 respectively.
            * Set hydraulic conductivity to a value within bounds determined by choice of material. 
            * Set recharge up to 10cm per day. Negative 'recharge' represents evaporation/transpiration. 

            Plans: >Make the slider for K function with logarithmic variation; >Fix L=800m (slider seems redundant); >Fine tune arrow lengths and add arrow length scale; >Make two plots "thinner" so the whole app is on one screen. Maybe use a different dash stylesheet? 

            ----------
            '''),
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '0 20', 'vertical-align': 'middle', 'margin-bottom': 30, 'margin-right': 50, 'margin-left': 20}),

    html.Div([
        dcc.Markdown(''' Left side head: **_h1_ (m).** '''),
        dcc.Slider(
            id='h1', min=1, max=50, step=0.5, value=initial_h1,
            marks={1:'1', 50:'50'},
            tooltip={'always_visible':True, 'placement':'topLeft'}
        ),
        dcc.Markdown(''' Hydraulic conductivity: **_K_ (m/day).** '''),
        dcc.Slider(
            id='K', min=10**(-2), max=10**(2), step=0.01, value=initial_K,
            marks={10**(-2):'10\u207B\u00B2', 10**(2):'10\u00B2'},
            tooltip={'always_visible':True, 'placement':'topLeft'}
        ),
        dcc.Markdown(''' Profile length: **_L_ (m).** '''),
        dcc.Slider(
            id='L', min=100, max=800, step=5, value=initial_L,
            marks={100:'100', 800:'800'},
            tooltip={'always_visible':True, 'placement':'topLeft'}
        ),
    ], style={'width': '37%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div([
        dcc.Markdown(''' Right side head: **_h2_ (m).** '''),
        dcc.Slider(
            id='h2', min=1, max=50, step=0.5, value=initial_h2,
            marks={1:'1', 50:'50'},
            tooltip={'always_visible':True, 'placement':'topLeft'}
        ),
        dcc.Markdown(''' Recharge: **_W_ (m/day).** '''),
        dcc.Slider(
            id='W', min=-0.05, max=0.1, step=0.01, value=initial_W,
            marks={-0.05:'-0.05', 0:'0.0', 0.05:'0.05', 0.1:'0.1'},
            tooltip={'always_visible':True, 'placement':'topLeft'}
        ),
    ], style={'width': '37%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div([
        dcc.Markdown(''' **Material:** '''),
        dcc.RadioItems(
            id='material',
            options=[
                {'label': 'Silt, Loess (10^-4 < K < 1)', 'value': 'silt'},
                {'label': 'Silty Sand (10^-2 < K < 10^2)', 'value': 'silty_sand'},
                {'label': 'Clean Sand (10^-1 < K < 10^3)', 'value': 'clean_sand'},
                {'label': 'Gravel (10^2 < K < 10^5)', 'value': 'gravel'},
            ],
            value=initial_material,
            style={'margin-bottom': '20px'}
        ),
        dcc.Markdown(''' **Flow Arrows:** '''),
        dcc.Checklist(
            id='arrow_visibility',
            options=[
                {'label': 'arrows visible', 'value': 'visible'},
            ],
            value=initial_arrow_visibility
        )
    ], style={'width': '26%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div([
        dcc.Graph(
            id='elevation_plot',
            config={
                'staticPlot': True,  # True, False
                #'scrollZoom': True,  # True, False
                'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                'showTips': True,  # True, False
                'displayModeBar': False,  # True, False, 'hover'
                'watermark': True,
                'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d'],
            },
        ),
    dcc.Graph(
            id='q_plot',
        )
    ], style={'width': '100%', 'display': 'inline-block'}),

    html.Div([
            dcc.Markdown('''
                #### Sources
                
                1. Inspired by [Hydrogeologic Properties of Earth Materials and Principles of Groundwater Flow](https://gw-project.org/books/hydrogeologic-properties-of-earth-materials-and-principles-of-groundwater-flow/), William W. Woessner (University of Montana, USA) and Eileen P. Poeter (Colorado School of Mines, USA), ISBN: 978-1-7770541-2-0.

                ----------
                '''),
        ], style={'width': '100%', 'display': 'inline-block', 'padding': '0 20', 'vertical-align': 'middle', 'margin-bottom': 30, 'margin-right': 50, 'margin-left': 20}),

], style={'width': '1000px'})


#initialize plots
elevation_plot = plot.initialize_elevation_plot(initial_h1, initial_h2, initial_K, initial_W, initial_L, initial_arrow_visibility)
q_plot = plot.initialize_q_plot(initial_h1, initial_h2, initial_K, initial_W, initial_L)

@app.callback(
    Output(component_id='K', component_property='min'),
    Output(component_id='K', component_property='max'),
    Output(component_id='K', component_property='marks'),
    Input(component_id='material', component_property='value'),
)
def update_K_bounds(material):
    if material == 'silt':
        return 10**(-4), 1, {10**(-4):'10\u207B\u2074', 1:'1'}
    elif material == 'silty_sand':
        return 10**(-2), 10**(2), {10**(-2):'10\u207B\u00B2', 10**(2):'10\u00B2'}
    elif material == 'clean_sand':
        return 10**(-1), 10**(3), {10**(-1):'10\u207B\u00B9', 10**(3):'10\u00B3'}
    elif material == 'gravel':
        return 10**(2), 10**(5), {10**(2):'10\u00B2', 10**(5):'10\u2075'}

@app.callback(
    Output(component_id='elevation_plot', component_property='figure'),
    Input(component_id='h1', component_property='value'),
    Input(component_id='h2', component_property='value'),
    Input(component_id='K', component_property='value'),
    Input(component_id='W', component_property='value'),
    Input(component_id='L', component_property='value'),
    Input(component_id='arrow_visibility', component_property='value')
)
def update_elevation_plot(h1, h2, K, W, L, arrow_visibility):
    fig = plot.update_elevation_plot(h1, h2, K, W, L, arrow_visibility, elevation_plot)
    return fig


@app.callback(
    Output(component_id='q_plot', component_property='figure'),
    Input(component_id='h1', component_property='value'),
    Input(component_id='h2', component_property='value'),
    Input(component_id='K', component_property='value'),
    Input(component_id='W', component_property='value'),
    Input(component_id='L', component_property='value')
)
def update_q_plot(h1, h2, K, W, L):
    fig = plot.update_q_plot(h1, h2, K, W, L, q_plot)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
