# -*- coding: utf-8 -*-

# Run this app with `python app.py` and visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/
# based on ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# mouse-over or 'hover' behavior is based on https://dash.plotly.com/interactive-graphing
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line
# Mapmaking code initially learned from https://plotly.com/python/mapbox-layers/.


from flask import Flask
from os import environ
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotting as plot
import station

#load markdown
instructions = open('instructions.md', 'r')
instructions_markdown = instructions.read()

attributions = open('attributions.md', 'r')
attributions_markdown = attributions.read()

#initial settings for the plots
initial_cruise = 'GIPY0405'
initial_y_range = [0, 500]
initial_x_range = 'default'
initial_hov_station = station.Station('hover', None, None, None, 'blue')
initial_click_stations = []

def station_dict(obj):
    return obj.__dict__


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
app = dash.Dash(
    server=server,
    url_base_pathname=environ.get('JUPYTERHUB_SERVICE_PREFIX', '/'),
    external_stylesheets=external_stylesheets
)

app.layout = html.Div([

    dcc.Markdown(
        children=instructions_markdown
        ),

# plot with the map of cruise stations
    html.Div([
        dcc.Graph(
            id='map',
            config={
                'staticPlot': False,  # True, False
                'scrollZoom': True,  # True, False
                'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                'showTips': True,  # True, False
                'displayModeBar': False,  # True, False, 'hover'
                'watermark': True,
                'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d'],
            },
            clear_on_unhover = True, #clears hover plots when cursor isn't over the station
        )
    ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 20', 'vertical-align': 'middle', 'margin-bottom': 30, 'margin-right': 50, 'margin-left': 20}),


    # slider or checklist details at https://dash.plotly.com/dash-core-components
    # checkboxes can be lumped together but then logic in "update_graph" is messier.
    # Content can be delivered using html, but markdown is simpler.
    html.Div([

        # choose the cruise
        dcc.Markdown('''
        **Select Cruise**
        '''),

        dcc.RadioItems( #radiobuttons to choose the current cruise
            id='cruise',
            options=[
                {'label': 'GIPY04 and GIPY05', 'value': 'GIPY0405'},
                {'label': 'GA03', 'value': 'GA03'},
                {'label': 'GP02', 'value': 'GP02'}
            ],
            value=initial_cruise,
            style={"margin-bottom": "30px"}
        ),


        dcc.Markdown('''
            **Select x-axis fit**
        '''),
        dcc.RadioItems( #radiobuttons to select either a default x-axis range, or to fit to the data
            id='x_range',
            options=[
                {'label': 'default', 'value': 'default'},
                {'label': 'fit to data', 'value': 'fitted'},
            ],
            value=initial_x_range
        ),

    ], style={'width': '40%', 'display': 'inline-block', 'vertical-align': 'middle'}),

    html.Div([
        dcc.Markdown('''
            **Depth (m)**
        '''),
    ], style={'display': 'inline-block', 'width': '5%', 'vertical-align': 'middle', 'textAlign': 'center'}),

    html.Div([
        dcc.RangeSlider(
            # slider to select the y-axis range
            # range slider documentation: https://dash.plotly.com/dash-core-components/rangeslider
            # note: I couldn't find a way to put the "max" value on the bottom of the slider (to flip the slider vertically)
            # so I made the slider go from -500 to 0, and I take the absolute value of the range later
            id='y_range',
            min=-500,
            max=0,
            step=0.5,
            #adding ticks to the slider without having labels
            marks={
                0: '', -100: '', -200: '', -300: '', -400: '', -500: '',
            },
            value=[-500, 0],
            vertical=True,
            verticalHeight=360
        )
    ], style={'display': 'inline-block', 'width': '2%', 'vertical-align': 'middle'}),

    html.Div([
        # the graph of subplots which show depth profiles for different parameters
        dcc.Graph(
            id='profiles',
            config={
                'staticPlot': False,  # True, False
                'scrollZoom': False,  # True, False
                'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                'showTips': True,  # True, False
                'displayModeBar': 'hover',  # True, False, 'hover'
                'watermark': False,
                'modeBarButtonsToRemove': ['resetAxis', 'pan2d', 'resetScale2d', 'select2d', 'lasso2d', 'zoom2d',
                                           'zoomIn2d', 'zoomOut2d', 'hoverCompareCartesian', 'hoverClosestCartesian',
                                           'autoScale2d'],
            }
        ),
    ], style={'display': 'inline-block', 'width': '93%', 'vertical-align': 'middle', 'margin-bottom': '50px'}),

    dcc.Markdown('''
            *Density, Sigma0, is potential density anomaly, or potential density minus 1000 kg/m\u00B3. [Reference](http://www.teos-10.org/pubs/gsw/html/gsw_sigma0.html).
            '''),
    dcc.Markdown(
        children=attributions_markdown
    ),
    dcc.Store(id='hov_station',
              data=json.dumps(initial_hov_station.__dict__)),
    dcc.Store(id='click_stations', data=json.dumps(initial_click_stations, default=station_dict))
], style={'width': '1000px'})



#using the plotting file to plot the figures

#initialize the map and the depth profiles
fig_map = plot.initialize_map(initial_cruise)
fig_profiles = plot.initialize_profiles(initial_cruise, initial_x_range, initial_y_range)

#stations
@app.callback(
    Output(component_id='hov_station', component_property='data'),
    Input(component_id='map', component_property='hoverData'),
    Input(component_id='cruise', component_property='value'),
)
def update_hover_station(hov_data, cruise):
    if (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'cruise'):
        #clear hover
        hov_station = station.Station('hover', None, None, None, 'blue')
    else:
        hov_station = station.get_hov_station(hov_data)

    return json.dumps(hov_station.__dict__)

@app.callback(
    Output(component_id='click_stations', component_property='data'),
    Input(component_id='map', component_property='clickData'),
    Input(component_id='click_stations', component_property='data'),
    Input(component_id='cruise', component_property='value'),
)
def update_click_stations(click_data, click_stations_json, cruise):
    click_stations = station.dict_list_to_station(json.loads(click_stations_json))
    if (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'cruise'):
        # clear click stations
        click_stations = []
    else:
        click_stations = station.get_click_stations(click_data, click_stations)

    return json.dumps(click_stations, default=station_dict)

#Suplot graph
@app.callback(
    Output(component_id='profiles', component_property='figure'),
    Input(component_id='hov_station', component_property='data'),
    Input(component_id='click_stations', component_property='data'),
    Input(component_id='cruise', component_property='value'),
    Input(component_id='x_range', component_property='value'),
    Input(component_id='y_range', component_property='value')
)
def update_profiles(hov_station_json, click_stations_json, cruise, x_range, y_range):
    hov_station = station.dict_to_station(json.loads(hov_station_json))
    click_stations = station.dict_list_to_station(json.loads(click_stations_json))

    y_range[0] = abs(y_range[0])
    y_range[1] = abs(y_range[1])
    # if the callback that was triggered was the cruise changing, we switch profiles (switch cruises)
    # otherwise, we update the profiles for the current cruise
    if (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'cruise'):
        fig = plot.switch_profiles(cruise, fig_profiles, x_range, y_range)
    else:
        fig = plot.update_profiles(hov_station, click_stations, cruise, fig_profiles, x_range, y_range)
    return fig



# The callback function with it's app.callback wrapper.
@app.callback(
    Output(component_id='map', component_property='figure'),
    Input(component_id='cruise', component_property='value'),
    Input(component_id='click_stations', component_property='data'),
    Input(component_id='map', component_property='figure')
)
def update_map(cruise, click_stations_json, figure_data):
    click_stations = station.dict_list_to_station(json.loads(click_stations_json))
    # switch map is called when we switch cruises, update map is called for other updates.
    if (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'cruise'):
        fig = plot.switch_map(cruise, fig_map)
    else:
        fig = plot.update_map(click_stations, figure_data, cruise)
    return fig



if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
