# -*- coding: utf-8 -*-

# Run this app with `python app3.py` and
# visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/

from flask import Flask
from os import environ

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import base64

import plotly.express as px
import plotly.graph_objects as go

import numpy as np
from numpy import random

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
app = dash.Dash(
    server=server,
    requests_pathname_prefix='/mohrs/',  # comment out this line to run locally. Keep for deploying on server.
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True #because of the tabs, not all callbacks are accessible so we suppress callback exceptions
)

# load introduction text
intro = open('introduction.md', 'r')
intro_md = intro.read()
intro = open('sources.md', 'r')
sources_md = intro.read()

image_filename = 'mohrs-diagram.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())


xmin = -200
xmax = 500
ymin = -300
ymax = 300

app.layout = html.Div([
    html.Div([
      dcc.Markdown(
          children=intro_md
        ),
    ]),

#Tabs: https://dash.plotly.com/dash-core-components/tabs
    html.Div([
        dcc.Tabs(id='tabs', value='tab1', children=[
            dcc.Tab(label='(1) Set Mean and Deviatoric Stresses', value='tab1'),
            dcc.Tab(label='(2) Set sigma1 and sigma3', value='tab2'),
        ]),
        html.Div(id='tabs-content')
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '0 20', 'vertical-align': 'middle', 'margin-bottom': 30, 'margin-right': 50, 'margin-left': 20}),

# below the graph
    html.Div([
        html.Div([
            dcc.Markdown('''
                ----
           ''')
        ]),
        html.Div([
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'width': '600px'})
        ], style={'margin-left': '50px', 'margin-bottom': '20px'}),
    
    html.Div([
            dcc.Markdown(
                children=sources_md
            )
        ])
    ])

], style={'width': '1000px'})


@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab1':
        return html.Div([
            html.Div([
                dcc.Markdown('''
                      **Mohr's circle parameters**
                      '''),

                html.Label(children='Mean stress (MPa)', style={'margin-top': '20px'}),
                dcc.Slider(id='s_m', min=0, max=xmax, value=xmax / 2, step=20,
                           marks={0: '0', 100: '100', 200: '200', 300: '300', 400: '400', 500: '500'},
                           tooltip={'always_visible':True, 'placement':'topLeft'}
                           ),

                html.Label(children='Deviatoric stress (MPa)', style={'margin-top': '20px'}),
                dcc.Slider(id='s_d', min=0.0, max=150, value=80, step=10,
                           marks={0: '0', 25: '25', 50: '50', 75: '75', 100: '100', 125: '125', 150: '150'},
                           tooltip={'always_visible':True, 'placement':'topLeft'}
                           ),

                html.Label(children='Theta (degrees)', style={'margin-top': '20px'}),
                dcc.Slider(id='theta', min=0, max=90, value=40, step=5,
                           marks={0: '0', 20:'20', 40:'40', 60:'60', 80:'80', 90:'90'},
                           tooltip={'always_visible':True, 'placement':'topLeft'}
                           )

            ], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top'}),
#            ], style={'width': '45%', 'display': 'inline-block', 'margin-left': '30px', 'margin-right': '30px', 'vertical-align': 'top'}),

            html.Div([
                dcc.Markdown('''
                        **Failure envelope parameters**
                        '''),
                html.Label(children='Cohesive strength (MPa)', style={'margin-top': '20px'}),
                dcc.Slider(id='s_o', min=0.0, max=150.0, value=50.0, step=10.0,
                           marks={0: '0', 25: '25', 50: '50', 75: '75', 100: '100', 125: '125', 150: '150'},
                           tooltip={'always_visible':True, 'placement':'topLeft'}
                           ),
                html.Label(children='Coeff. of internal friction', style={'margin-top': '20px'}),
                dcc.Slider(id='mu', min=0.0, max=2.0, value=0.5, step=0.1,
                           marks={0: '0', 0.5: '0.5', 1: '1', 1.5: '1.5', 2: '2'},
                           tooltip={'always_visible':True, 'placement':'topLeft'}
                           ),
                dcc.Checklist(
                    id='circle_checkbox',
                    options=[
                        {'label': 'Show Mohrs Circle', 'value': 'circle'}
                    ],
                    value=['circle'], # default is "on"
                    style={'margin-top': '20px', 'margin-left': '80px'}
                ),

                dcc.Checklist(
                    id='coulomb_checkbox',
                    options=[
                        {'label': 'Show failure envelope', 'value': 'coulomb'},
                    ],
                    value=[], # default is "off"
                    style={'margin-top': '20px', 'margin-left': '80px'}
                )
            ], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top'}),

            html.Div([
                dcc.Graph(
                    id='mean_dev_graph',
                    config={
                        'displayModeBar': True,
                        'modeBarButtonsToRemove': ['select', 'lasso2d', 'resetScale'],                     
                }),
            ]),
        ])
    elif tab == 'tab2':
        return html.Div([
            html.Div([
                dcc.Markdown('''
                  **Mohr's circle parameters**
                  '''),

                html.Label(children='Sigma_1 (MPa)', style={'margin-top': '20px'}),
                dcc.Slider(id='s1', min=0, max=xmax, value=350, step=20,
                           marks={0: '0', 100: '100', 200: '200', 300: '300', 400: '400', 500: '500'},
                           tooltip={'always_visible': True, 'placement': 'topLeft'}
                           ),

                html.Label(children='Sigma_3 (MPa)', style={'margin-top': '20px'}),
                dcc.Slider(id='s3', min=0, max=xmax, value=120, step=20,
                           marks={0: '0', 100: '100', 200: '200', 300: '300', 400: '400', 500: '500'},
                           tooltip={'always_visible': True, 'placement': 'topLeft'}
                           ),

                html.Label(children='Theta (degrees)', style={'margin-top': '20px'}),
                dcc.Slider(id='theta', min=0, max=90, value=40, step=5,
                           marks={0: '0', 20:'20', 40:'40', 60:'60', 80:'80', 90:'90'},
                           tooltip={'always_visible':True, 'placement':'topLeft'}
                           )

            ], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top'}),
#            ], style={'width': '45%', 'display': 'inline-block', 'margin-left': '30px', 'margin-right': '30px', 'vertical-align': 'top'}),

            html.Div([
                dcc.Markdown('''
                    **Failure envelope parameters**
                    '''),
                html.Label(children='Cohesive strength (MPa)', style={'margin-top': '20px'}),
                dcc.Slider(id='s_o', min=0.0, max=150.0, value=50.0, step=10.0,
                           marks={0: '0', 25: '25', 50: '50', 75: '75', 100: '100', 125: '125', 150: '150'},
                           tooltip={'always_visible': True, 'placement': 'topLeft'}
                           ),
                html.Label(children='Coeff. of internal friction', style={'margin-top': '20px'}),
                dcc.Slider(id='mu', min=0.0, max=2.0, value=0.5, step=0.1,
                           marks={0: '0', 0.5: '0.5', 1: '1', 1.5: '1.5', 2: '2'},
                           tooltip={'always_visible': True, 'placement': 'topLeft'}
                           ),
                dcc.Checklist(
                    id='circle_checkbox',
                    options=[
                        {'label': 'Show Mohrs Circle', 'value': 'circle'}
                    ],
                    value=['circle'], # default is "on"
                    style={'margin-top': '20px', 'margin-left': '80px'}
                ),

                dcc.Checklist(
                    id='coulomb_checkbox',
                    options=[
                        {'label': 'Show failure envelope', 'value': 'coulomb'},
                    ],
                    value=[], # default is "off"
                    style={'margin-top': '20px', 'margin-left': '80px'}
                )
            ], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top'}),

            html.Div([
                dcc.Graph(
                    id='s1s3_graph',
                    config={
                        'displayModeBar': True,
                        'modeBarButtonsToRemove': ['select', 'lasso2d', 'resetScale'],                     
                }),
            ]),
        ])


### TAB 1

# The callback function with it's app.callback wrapper.
@app.callback(
    Output('mean_dev_graph', 'figure'),
    Input('circle_checkbox', 'value'),
    Input('coulomb_checkbox', 'value'),
    Input('s_m', 'value'),
    Input('s_d', 'value'),
    Input('theta', 'value'),
    Input('s_o', 'value'),
    Input('mu', 'value')
)
def update_graph(circle_checkbox, coulomb_checkbox, s_m, s_d, theta, s_o, mu, ):
    # array for drawing a circle, angle going from 0 to 90 since 2*angle is used.
    # for a whole circle, use np.pi, not np.pi/2

    angle = np.linspace(0, np.pi, 100)

    # build the mohr's circle and coulomb failure line
    s3 = s_m - s_d
    s1 = s_m + s_d

    coulx1 = np.linspace(0, xmax, 50)
    couly1 = s_o + mu * coulx1
    coulx2 = np.linspace(0, xmax, 50)
    couly2 = -s_o - mu * coulx2

    s_n = 0.5 * (s1 + s3) + 0.5 * (s1 - s3) * np.cos(2 * angle)
    s_s = 0.5 * (s1 - s3) * np.sin(2 * angle)
    snmin = np.amin(s_n)
    snmax = np.amax(s_n)

    theta_rad = theta * np.pi/180
    # draw the angle representing the plane of interest
    x = np.array([s_m, 0.5 * (s1 + s3) + 0.5 * (s1 - s3) * np.cos(2 * theta_rad)])
    y = np.array([0, 0.5 * (s1 - s3) * np.sin(2 * theta_rad)])
    
    # generate the plot.
    fig = go.Figure()

    if circle_checkbox == ['circle']:
        fig.add_trace(go.Scatter(
            x=s_n, 
            y=s_s, 
            mode='lines',
            hovertemplate = 
                'Sn: %{x:.1f}'+
                '<br>Ss: %{y:.1f}', 
            name='circle'))
        fig.add_trace(go.Scatter(
            x=x, 
            y=y, 
            name="linear", 
            line_shape='linear', 
            hovertemplate = 
                'Sn: %{x:.1f}'+
                '<br>Ss: %{y:.1f}', 
            line=dict(color='green')))
        
        # for annotations, see https://plotly.com/python/text-and-annotations/
        fig.add_annotation(x=snmin, y=0,
            text="S_3",
            showarrow=True,
            arrowhead=1)
        fig.add_annotation(x=snmax, y=0,
            text="S_1",
            showarrow=True,
            ax=20,
            ay=-30,
            arrowhead=1)

    if coulomb_checkbox == ['coulomb']:
        fig.add_trace(go.Scatter(
            x=coulx1, 
            y=couly1, 
            mode='lines', 
            hovertemplate = 
                'Sn: %{x:.1f}'+
                '<br>Ss: %{y:.1f}', 
            name='Coulomb+', 
            line=dict(color='red')))
        fig.add_trace(go.Scatter(
            x=coulx2, 
            y=couly2, 
            mode='lines', 
            hovertemplate = 
                'Sn: %{x:.1f}'+
                '<br>Ss: %{y:.1f}', 
            name='Coulomb-', 
            line=dict(color='red')))        

    # We want a "square" figure so the circle is seen as a circle
    # Ranges for xaxis and yaxis, and the plot width/height must be be chosen for a square graph.
    # width and height are in pixels.
    fig.update_layout(xaxis_title='Sigma_n (MPa)', yaxis_title='Sigma_s (MPa)', width=700, height=600, showlegend=False)
    #    fig.update_layout(xaxis_title='Sigma_n', yaxis_title='Sigma_s', width=800, height=660, showlegend=False)
    fig.update_layout(title_text="Mohr's Circle with failure envelope")
    fig.update_xaxes(range=[xmin, xmax])
    fig.update_yaxes(range=[ymin, ymax])

    return fig




### TAB 2

# The callback function with it's app.callback wrapper.
@app.callback(
    Output('s1s3_graph', 'figure'),
    Input('circle_checkbox', 'value'),
    Input('coulomb_checkbox', 'value'),
    Input('s1', 'value'),
    Input('s3', 'value'),
    Input('theta', 'value'),
    Input('s_o', 'value'),
    Input('mu', 'value')
)
def update_graph(circle_checkbox, coulomb_checkbox, s1, s3, theta, s_o, mu, ):
    # array for drawing a circle, angle going from 0 to 90 since 2*angle is used.
    # for a whole circle, use np.pi, not np.pi/2

    angle = np.linspace(0, np.pi, 100)

    # build the mohr's circle and coulomb failure line
    s_m = (s1 + s3) / 2
    s_d = s1 + s3

    s_n = 0.5 * (s1 + s3) + 0.5 * (s1 - s3) * np.cos(2 * angle)
    s_s = 0.5 * (s1 - s3) * np.sin(2 * angle)
    snmin = np.amin(s_n)
    snmax = np.amax(s_n)

    theta_rad = theta * np.pi/180
    # draw the angle representing the plane of interest
    x = np.array([s_m, 0.5 * (s1 + s3) + 0.5 * (s1 - s3) * np.cos(2 * theta_rad)])
    y = np.array([0, 0.5 * (s1 - s3) * np.sin(2 * theta_rad)])

    coulx1 = np.linspace(0, xmax, 50)
    couly1 = s_o + mu * coulx1
    coulx2 = np.linspace(0, xmax, 50)
    couly2 = -s_o - mu * coulx2

    # generate the plot.
    fig = go.Figure()

    if circle_checkbox == ['circle']:
        fig.add_trace(go.Scatter(
            x=s_n, 
            y=s_s, 
            mode='lines',
            hovertemplate = 
                'Sn: %{x:.1f}'+
                '<br>Ss: %{y:.1f}', 
            name='circle'))
        fig.add_trace(go.Scatter(
            x=x, 
            y=y, 
            name="linear", 
            line_shape='linear', 
            hovertemplate = 
                'Sn: %{x:.1f}'+
                '<br>Ss: %{y:.1f}', 
            line=dict(color='green')))

        # for annotations, see https://plotly.com/python/text-and-annotations/
        fig.add_annotation(x=snmin, y=0,
            text="S_3",
            showarrow=True,
            arrowhead=1)
        fig.add_annotation(x=snmax, y=0,
            text="S_1",
            showarrow=True,
            ax=20,
            ay=-30,
            arrowhead=1)

    if coulomb_checkbox == ['coulomb']:
        fig.add_trace(go.Scatter(
            x=coulx1, 
            y=couly1, 
            mode='lines', 
            hovertemplate = 
                'Sn: %{x:.1f}'+
                '<br>Ss: %{y:.1f}', 
            name='Coulomb+', 
            line=dict(color='red')))
        fig.add_trace(go.Scatter(
            x=coulx2, 
            y=couly2, 
            mode='lines', 
            hovertemplate = 
                'Sn: %{x:.1f}'+
                '<br>Ss: %{y:.1f}', 
            name='Coulomb-', 
            line=dict(color='red')))

    # We want a "square" figure so the circle is seen as a circle
    # Ranges for xaxis and yaxis, and the plot width/height must be be chosen for a square graph.
    # width and height are in pixels.
    fig.update_layout(xaxis_title='Sigma_n (MPa)', yaxis_title='Sigma_s (MPa)', width=700, height=600, showlegend=False)
    #    fig.update_layout(xaxis_title='Sigma_n', yaxis_title='Sigma_s', width=800, height=660, showlegend=False)
    fig.update_layout(title_text="Mohr's Circle with failure envelope")
    fig.update_xaxes(range=[xmin, xmax])
    fig.update_yaxes(range=[ymin, ymax])

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
