# This is the main file the app is run from. This file has the dash structure and callbacks.

# Run this app with `python app.py` and visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/

# based on ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# mouse-over or 'hover' behavior is based on https://dash.plotly.com/interactive-graphing
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line
# Mapmaking code initially learned from https://plotly.com/python/mapbox-layers/.


import dash
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask
from plotly.subplots import make_subplots

import plotting as plot
import station

# load markdown for instructions and sources
instructions = open("instructions.md", "r")
instructions_markdown = instructions.read()

attributions = open("attributions.md", "r")
attributions_markdown = attributions.read()

# initial settings for the plots
initial_cruise = "GIPY0405"
initial_y_range = [0, 500]
initial_x_range = "default"


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        dcc.Markdown(
            # using the instructions markdown file that was loaded in above
            children=instructions_markdown
        ),
        html.Div(
            [
                # This is the plot with the map of cruises and stations
                dcc.Graph(
                    id="map",
                    config={
                        "staticPlot": False,  # True, False
                        "scrollZoom": True,  # True, False
                        "doubleClick": "reset",  # 'reset', 'autosize' or 'reset+autosize', False
                        "showTips": True,  # True, False
                        "displayModeBar": False,  # True, False, 'hover'
                        "watermark": True,
                        "modeBarButtonsToRemove": ["pan2d", "select2d", "lasso2d"],
                    },
                    clear_on_unhover=True,  # clears hover plots when cursor isn't over the station
                )
            ],
            style={
                "width": "50%",
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
                dcc.Markdown(
                    """
        **Select Cruise**
        """
                ),
                dcc.RadioItems(  # radiobuttons to choose the current cruise
                    id="cruise",
                    options=[
                        {"label": "GIPY04 and GIPY05", "value": "GIPY0405"},
                        {"label": "GA03", "value": "GA03"},
                        {"label": "GP02", "value": "GP02"},
                    ],
                    value=initial_cruise,
                    style={"margin-bottom": "30px"},
                ),
                dcc.Markdown(
                    """
            **Select x-axis fit**
        """
                ),
                dcc.RadioItems(  # radiobuttons to select either a default x-axis range, or to fit to the data
                    id="x_range",
                    options=[
                        {"label": "default", "value": "default"},
                        {"label": "fit to data", "value": "fitted"},
                    ],
                    value=initial_x_range,
                ),
                # button to clear the selected stations from the map
                html.Button("Clear", id="clear_button", style={"margin-top": "30px"}),
            ],
            style={
                "width": "40%",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
        html.Div(
            [
                dcc.Markdown(
                    """
            **Depth (m)**
        """
                ),
            ],
            style={
                "display": "inline-block",
                "width": "5%",
                "vertical-align": "middle",
                "textAlign": "center",
            },
        ),
        html.Div(
            [
                dcc.RangeSlider(
                    # slider to select the y-axis range
                    # range slider documentation: https://dash.plotly.com/dash-core-components/rangeslider
                    # note: I couldn't find a way to put the "max" value on the bottom of the slider (to flip the slider vertically)
                    # so I made the slider go from -500 to 0, and I take the absolute value of the range later
                    id="y_range",
                    min=-500,
                    max=0,
                    step=0.5,
                    # adding ticks to the slider without having labels
                    marks={
                        0: "",
                        -100: "",
                        -200: "",
                        -300: "",
                        -400: "",
                        -500: "",
                    },
                    value=[-500, 0],
                    vertical=True,
                    verticalHeight=360,
                )
            ],
            style={
                "display": "inline-block",
                "width": "2%",
                "vertical-align": "middle",
            },
        ),
        html.Div(
            [
                # the graph of subplots which show depth profiles for different parameters
                dcc.Graph(
                    id="profiles",
                    config={
                        "staticPlot": False,  # True, False
                        "scrollZoom": False,  # True, False
                        "doubleClick": "reset",  # 'reset', 'autosize' or 'reset+autosize', False
                        "showTips": True,  # True, False
                        "displayModeBar": "hover",  # True, False, 'hover'
                        "watermark": False,
                        "modeBarButtonsToRemove": [
                            "resetAxis",
                            "pan2d",
                            "resetScale2d",
                            "select2d",
                            "lasso2d",
                            "zoom2d",
                            "zoomIn2d",
                            "zoomOut2d",
                            "hoverCompareCartesian",
                            "hoverClosestCartesian",
                            "autoScale2d",
                        ],
                    },
                ),
            ],
            style={
                "display": "inline-block",
                "width": "93%",
                "vertical-align": "middle",
                "margin-bottom": "50px",
            },
        ),
        dcc.Markdown(
            # notes on the data, displayed under the depth profiles.
            """
            *Density, Sigma0, is potential density anomaly, or potential density minus 1000 kg/m\u00B3. [Reference](http://www.teos-10.org/pubs/gsw/html/gsw_sigma0.html).
            
            **The Nitrate/Iron data was calculated from interpolated values of Nitrate and the exact values of Iron.
            """
        ),
        dcc.Markdown(
            # the markdown from the attributions file loaded in above.
            children=attributions_markdown
        ),
        # Using dcc.Store (https://dash.plotly.com/dash-core-components/store) to store values of the hover station and the clicked stations
        # The hov_station is the station currently being hovered over by the mouse. clicked_stations is a list of stations
        # that were clicked and should be plotted. dcc.Store stores a variable as a json, and then it can be accessed through a callback.
        # dcc.Store is an alternative to using global variables, since global variables don't work with Dash when there are concurrent users.
        dcc.Store(id="hov_station", data={}, storage_type="memory"),
        dcc.Store(id="click_stations", data={}, storage_type="memory"),
    ],
    style={"width": "1000px"},
)


# update the hover station
@app.callback(
    Output(
        component_id="hov_station", component_property="data"
    ),  # we output to the dcc.Store variable 'hov_station'
    Input(
        component_id="map", component_property="hoverData"
    ),  # the hover data from the map, which tells us which station the mouse is hovering over
    Input(component_id="cruise", component_property="value"),
    Input(component_id="hov_station", component_property="data"),
)
def update_hover_station(hov_data, cruise, hov_station):
    # the 'dash.callback_context.triggered' statement checks if the cruise was just switched. If the cruise is switched, we clear the hover.
    if (
        (hov_station == {})
        | (hov_station is None)
        | (dash.callback_context.triggered[0]["prop_id"].split(".")[0] == "cruise")
    ):
        # clear hover
        hov_station = station.Station(
            "hover", None, None, None, None, "blue"
        ).__dict__  # empty station
    else:
        hov_station = station.get_hov_station(hov_data)

    return hov_station


# The clear button callback. Uses the dcc.Store 'clear_data' property to clear the stored information.
@app.callback(
    Output(component_id="click_stations", component_property="clear_data"),
    Output(component_id="hov_station", component_property="clear_data"),
    Input(component_id="clear_button", component_property="n_clicks"),
)
def clear_stations(n_clicks):
    return True, True


# The callback for the 'clicked_stations' list. We input the current stored value for clicked_stations, update it, and return it.
@app.callback(
    Output(component_id="click_stations", component_property="data"),
    Input(component_id="map", component_property="clickData"),
    Input(component_id="click_stations", component_property="data"),
    Input(component_id="cruise", component_property="value"),
)
def update_click_stations(click_data, click_stations, cruise):
    # converting the inputed clicked_stations to a list of Station objects from a json.
    if (click_stations is None) | (click_stations == {}):
        click_stations = []

    # if the cruise was just switched, we clear the clicked stations list
    if dash.callback_context.triggered[0]["prop_id"].split(".")[0] == "cruise":
        click_stations = []
    # if the click_data was just updated, we add the new clicked station to the list. The
    # if statement prevents adding the same station multiple times, as click_data doesn't clear.
    elif dash.callback_context.triggered[0]["prop_id"].split(".")[0] == "map":
        click_stations = station.get_click_stations(click_data, click_stations)

    return click_stations


# Depth profiles
@app.callback(
    Output(component_id="profiles", component_property="figure"),
    Input(component_id="profiles", component_property="figure"),
    Input(component_id="hov_station", component_property="data"),
    Input(component_id="click_stations", component_property="data"),
    Input(component_id="cruise", component_property="value"),
    Input(component_id="x_range", component_property="value"),
    Input(component_id="y_range", component_property="value"),
)
def update_profiles(
    fig_profiles_dict, hov_station, click_stations, cruise, x_range, y_range
):
    if fig_profiles_dict is None:  # if the figure is empty, we initialize it
        fig_profiles = plot.initialize_profiles(
            initial_cruise, initial_x_range, initial_y_range
        )  # fig_profiles is the figure with depth profile subplots
    else:  # otherwise we make a new figure and give it the data and layout from the inputed figure dictionary. This converts a dict to a figure.
        fig_profiles = make_subplots(
            rows=1,
            cols=6,
            subplot_titles=(
                "<b>Temperature</b>",
                "<b>Salinity</b>",
                "<b>Sigma0*</b>",
                "<b>Nitrate</b>",
                "<b>Iron</b>",
                "<b>Nitrate/Iron</b>",
            ),
        )
        fig_profiles.update(
            data=fig_profiles_dict["data"], layout=fig_profiles_dict["layout"]
        )

    # update the y_axis of the graph. Need to use absolute values for reasons stated above in the html for the y_range slider
    y_range[0] = abs(y_range[0])
    y_range[1] = abs(y_range[1])
    # if the callback that was triggered was the cruise changing, we switch profiles (switch cruises)
    # otherwise, we update the profiles for the current cruise
    if dash.callback_context.triggered[0]["prop_id"].split(".")[0] == "cruise":
        fig = plot.switch_profiles(cruise, fig_profiles, x_range, y_range)
    else:
        fig = plot.update_profiles(
            hov_station, click_stations, cruise, fig_profiles, x_range, y_range
        )
    return fig


# Callback for the map plot
@app.callback(
    Output(component_id="map", component_property="figure"),
    Input(component_id="map", component_property="figure"),
    Input(component_id="cruise", component_property="value"),
    Input(component_id="click_stations", component_property="data"),
    Input(component_id="map", component_property="figure"),
)
def update_map(fig_map_dict, cruise, click_stations, figure_data):
    if fig_map_dict is None:  # if the figure doesn't exist yet, we initialize it
        fig_map = plot.initialize_map(initial_cruise)
    else:  # otherwise we convert our figure dictionary to a Figure
        fig_map = go.Figure(data=fig_map_dict["data"], layout=fig_map_dict["layout"])

    # switch map is called when we switch cruises, update map is called for other updates.
    if dash.callback_context.triggered[0]["prop_id"].split(".")[0] == "cruise":
        fig = plot.switch_map(cruise, fig_map)
    else:
        fig = plot.update_map(click_stations, figure_data, cruise)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
