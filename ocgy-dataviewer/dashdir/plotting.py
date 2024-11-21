# This file is called by app.py. This file updates plots.
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

import station

# see Python routine "parse-csv.py" for the method of filtering data and making these csv files
GIPY05 = pd.read_csv("./data/GIPY05_filtered.csv")
GIPY04 = pd.read_csv("./data/GIPY04_filtered.csv")
GA03 = pd.read_csv("./data/GA03_filtered.csv")
GP02 = pd.read_csv("./data/GP02_filtered.csv")
GIPY0405 = pd.concat(
    [GIPY04, GIPY05], ignore_index=True
)  # merging the csv files for GIPY04 and GIPY05

all_data = pd.concat([GP02, GA03, GIPY04, GIPY05], keys=['GP02', 'GA03', 'GIPY04', 'GIPY05'])
cruises = all_data.index.values
cruises = np.array([np.array(list(x)) for x in cruises])
cruises = cruises[:,0]
all_data['Cruise'] = cruises


# SUBPLOTS PLOTTING
def get_x_y_values(lat, lon, data_name):
    # getting the x and y values to plot the depth profile for a given parameter (data_name) at a given lat and lon
    # We use latitude and longitude to specify the station, because originally there were duplicate station names, but there
    # are no duplicate latitudes and longitudes.

    xvals = all_data[data_name][
        (all_data["Latitude"] == lat) & (all_data["Longitude"] == lon)
        ]
    yvals = all_data["Depth"][
        (all_data["Latitude"] == lat) & (all_data["Longitude"] == lon)
        ]

    return [xvals, yvals]


def update_x_range(fig):
    # updating the x-axis range for the subplots:
    fig.update_xaxes(
        autorange=True
    )  # letting plotly select the x-range for 'fitted' data
    fig.update_xaxes(
        nticks=3
    )  # limiting the number of x-axis ticks so the plots don't change height
    return fig


# update the legend with station name, lat, lon, and date
def update_legend(fig, hov_station, click_stations):
    # Updating the legend info for the hover station
    if station.is_empty(hov_station) is False:
        fig.data[0]["showlegend"] = True
        fig.data[0]["name"] = (
                str(hov_station["name"])
                + "<br>lat: "
                + str("{:.2f}".format(hov_station["lat"]))
                + "<br>lon: "
                + str("{:.2f}".format(hov_station["lon"]))
                + "<br>date: "
                + str(hov_station["date"])
        )
    # updating legend info for clicked stations
    if len(click_stations) != 0:
        for i in range(len(click_stations)):
            fig.data[6 + 6 * i]["showlegend"] = True
            for i in range(len(click_stations)):
                fig.data[6 + 6 * i]["name"] = (
                        str(click_stations[i]["name"])
                        + "<br>lat: "
                        + str("{:.2f}".format(click_stations[i]["lat"]))
                        + "<br>lon: "
                        + str("{:.2f}".format(click_stations[i]["lon"]))
                        + "<br>date: "
                        + str(click_stations[i]["date"])
                )
    return fig


# clear (empty) traces from the legend
def clear_click_legend(fig):
    for i in range(8):
        fig.data[6 + i * 6]["showlegend"] = False
    return fig


def clear_hover_legend(fig):
    fig.data[0]["showlegend"] = False
    return fig


def clear_hover_traces(fig):
    clear_hover_legend(fig)  # clear empty traces from the legend
    # set all hover data to None
    fig.data[0].update(x=[None], y=[None])
    fig.data[1].update(x=[None], y=[None])
    fig.data[2].update(x=[None], y=[None])
    fig.data[3].update(x=[None], y=[None])
    fig.data[4].update(x=[None], y=[None])
    fig.data[5].update(x=[None], y=[None])
    return fig


def clear_click_traces(fig):
    clear_click_legend(fig)  # clear empty traces from the legend

    # loop through each station and set each parameter to None
    for i in range(8):
        fig.data[6 + i * 6].update(x=[None], y=[None])
        fig.data[7 + i * 6].update(x=[None], y=[None])
        fig.data[8 + i * 6].update(x=[None], y=[None])
        fig.data[9 + i * 6].update(x=[None], y=[None])
        fig.data[10 + i * 6].update(x=[None], y=[None])
        fig.data[11 + i * 6].update(x=[None], y=[None])
    return fig


# initialize the profiles
def initialize_profiles(y_range):
    fig = make_subplots(  # initialize subplots with titles
        rows=1,
        cols=6)
                        #subplot_titles=(
                        #    "<b>Temperature</b>",
                        #    "<b>Salinity</b>",
                        #    "<b>Sigma0*</b>",
                        #    "<b>Nitrate</b>",
                        #    "<b>Iron</b>",
                        #    "<b>Nitrate/Iron**</b>",
                        #),

    # empty traces for hovered data
    figT = px.scatter(x=[None], y=[None])
    figS = px.scatter(x=[None], y=[None])
    figD = px.scatter(x=[None], y=[None])
    figN = px.scatter(x=[None], y=[None])
    figI = px.scatter(x=[None], y=[None])
    figR = px.scatter(x=[None], y=[None])
    
    #Adds lines between the markers.
   # figT.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')
   # figS.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')
   # figD.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')
   # figN.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')
   # figI.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')
   # figR.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')

    fig.add_trace(figT.data[0], row=1, col=1)
    fig.add_trace(figS.data[0], row=1, col=2)
    fig.add_trace(figD.data[0], row=1, col=3)
    fig.add_trace(figN.data[0], row=1, col=4)
    fig.add_trace(figI.data[0], row=1, col=5)
    fig.add_trace(figR.data[0], row=1, col=6)

    for i in range(8):
        # empty traces for clicked data
        figT = px.scatter(x=[None], y=[None])
        figS = px.scatter(x=[None], y=[None])
        figD = px.scatter(x=[None], y=[None])
        figN = px.scatter(x=[None], y=[None])
        figI = px.scatter(x=[None], y=[None])
        figR = px.scatter(x=[None], y=[None])

        #Adds lines between the markers.
        #figT.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')
        #figS.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')
        #figD.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')
        #figN.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')
        #figI.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')
        #figR.update_traces(mode='lines + markers', connectgaps=True, line_shape='spline')
    
        fig.add_trace(figT.data[0], row=1, col=1)
        fig.add_trace(figS.data[0], row=1, col=2)
        fig.add_trace(figD.data[0], row=1, col=3)
        fig.add_trace(figN.data[0], row=1, col=4)
        fig.add_trace(figI.data[0], row=1, col=5)
        fig.add_trace(figR.data[0], row=1, col=6)

    fig.update_yaxes(range=y_range)
    # putting x-axis on top of the plot
    fig.update_layout(
        xaxis=dict(side="top"),
        xaxis2=dict(side="top"),
        xaxis3=dict(side="top"),
        xaxis4=dict(side="top"),
        xaxis5=dict(side="top"),
        xaxis6=dict(side="top"),
    )
    #fig.update_annotations(yshift=-410)  # moving titles to bottom of plot
    #fig.update_annotations(yshift=50) #move titles to top of plot
    fig.update_layout(margin={"l": 0, "b": 40, "r": 100, "t": 30})

    # customize x axes (use for auto updating axes)
    fig.update_xaxes(title_text="<b>Temperature</b><br>(\u00BAC)", row=1, col=1)
    fig.update_xaxes(title_text="<b>Salinity</b><br>(Practical Salinity)", row=1, col=2)
    fig.update_xaxes(title_text="<b>Sigma0*</b><br>(kg/m\u00B3)", row=1, col=3)  # unicode for the m^3
    fig.update_xaxes(title_text="<b>Nitrate</b><br>(\u03BCmol/kg)", row=1, col=4)
    fig.update_xaxes(title_text="<b>Iron</b><br>(nmol/kg)", row=1, col=5)
    fig.update_xaxes(title_text="<b>Nitrate/Iron**</b><br>(\u03BCmol/nmol)", row=1, col=6)
    fig = update_x_range(fig)
    
    #initial fixed x axes
    #fig.update_xaxes(title_text="<b>Temperature</b><br>(\u00BAC)", range = (-3,29), nticks = 3, row=1, col=1)
    #fig.update_xaxes(title_text="<b>Salinity</b><br>(Practical Salinity)", range = (30,38), nticks = 3, row=1, col=2)
    #fig.update_xaxes(title_text="<b>Sigma0*</b><br>(kg/m\u00B3)", range = (22,29), nticks = 3, row=1, col=3)  # unicode for the m^3
    #fig.update_xaxes(title_text="<b>Nitrate</b><br>(\u03BCmol/kg)", range = (-1,45), nticks = 3, row=1, col=4)
    #fig.update_xaxes(title_text="<b>Iron</b><br>(nmol/kg)", range = (-0.1,2), nticks = 3, row=1, col=5)
    #fig.update_xaxes(title_text="<b>Nitrate/Iron**</b><br>(\u03BCmol/nmol)", range = (-5,625), nticks = 3, row=1, col=6)

    fig.update_layout(template  = "simple_white")

    return fig


# this function is called when any parameters are changed, to update the profiles
def update_profiles(hov_station, click_stations, fig, y_range):
    fig = clear_hover_traces(fig)
    fig = clear_click_traces(fig)

    # if there is a hover station, we find all the profile data for the hover station
    if station.is_empty(hov_station) is False:
        hov_xvals_temp, hov_yvals_temp = get_x_y_values(
            hov_station["lat"], hov_station["lon"], "Temperature"
        )
        hov_xvals_sal, hov_yvals_sal = get_x_y_values(
            hov_station["lat"], hov_station["lon"], "Salinity"
        )
        hov_xvals_dens, hov_yvals_dens = get_x_y_values(
            hov_station["lat"], hov_station["lon"], "Density"
        )
        hov_xvals_nit, hov_yvals_nit = get_x_y_values(
            hov_station["lat"], hov_station["lon"], "Nitrate"
        )
        hov_xvals_iron, hov_yvals_iron = get_x_y_values(
            hov_station["lat"], hov_station["lon"], "Iron"
        )
        hov_xvals_ratio, hov_yvals_ratio = get_x_y_values(
            hov_station["lat"], hov_station["lon"], "Ratio"
        )

        fig.data[0].update(x=hov_xvals_temp, y=hov_yvals_temp, marker_color=hov_station["colour"])
        fig.data[1].update(x=hov_xvals_sal, y=hov_yvals_sal, marker_color=hov_station["colour"])
        fig.data[2].update(x=hov_xvals_dens, y=hov_yvals_dens, marker_color=hov_station["colour"])
        fig.data[3].update(x=hov_xvals_nit, y=hov_yvals_nit, marker_color=hov_station["colour"])
        fig.data[4].update(x=hov_xvals_iron, y=hov_yvals_iron, marker_color=hov_station["colour"])
        fig.data[5].update(x=hov_xvals_ratio, y=hov_yvals_ratio, marker_color=hov_station["colour"])

    # loop through each of the clicked stations and plot the traces
    if len(click_stations) != 0:
        for i in range(8):
            if i < len(click_stations):
                click_xvals_temp, click_yvals_temp = get_x_y_values(
                    click_stations[i]["lat"],
                    click_stations[i]["lon"],
                    "Temperature",
                )
                click_xvals_sal, click_yvals_sal = get_x_y_values(
                    click_stations[i]["lat"],
                    click_stations[i]["lon"],
                    "Salinity",
                )
                click_xvals_dens, click_yvals_dens = get_x_y_values(
                    click_stations[i]["lat"],
                    click_stations[i]["lon"],
                    "Density",
                )
                click_xvals_nit, click_yvals_nit = get_x_y_values(
                    click_stations[i]["lat"],
                    click_stations[i]["lon"],
                    "Nitrate",
                )
                click_xvals_iron, click_yvals_iron = get_x_y_values(
                    click_stations[i]["lat"], click_stations[i]["lon"], "Iron"
                )
                click_xvals_ratio, click_yvals_ratio = get_x_y_values(
                    click_stations[i]["lat"], click_stations[i]["lon"], "Ratio"
                )

                fig.data[6 + i * 6].update(
                    x=click_xvals_temp,
                    y=click_yvals_temp,
                    marker_color=click_stations[i]["colour"],
                    marker_symbol=click_stations[i]["symbol"],
                    marker_line_color="black",
                    marker_line_width=0.3,
                    marker_size=6,

                )
                fig.data[7 + i * 6].update(
                    x=click_xvals_sal,
                    y=click_yvals_sal,
                    marker_color=click_stations[i]["colour"],
                    marker_symbol=click_stations[i]["symbol"],
                    marker_line_color="black",
                    marker_line_width=0.3,
                    marker_size=6,
                )
                fig.data[8 + i * 6].update(
                    x=click_xvals_dens,
                    y=click_yvals_dens,
                    marker_color=click_stations[i]["colour"],
                    marker_symbol=click_stations[i]["symbol"],
                    marker_line_color="black",
                    marker_line_width=0.3,
                    marker_size=6,
                )
                fig.data[9 + i * 6].update(
                    x=click_xvals_nit,
                    y=click_yvals_nit,
                    marker_color=click_stations[i]["colour"],
                    marker_symbol=click_stations[i]["symbol"],
                    marker_line_color="black",
                    marker_line_width=0.3,
                    marker_size=6,
                )
                fig.data[10 + i * 6].update(
                    x=click_xvals_iron,
                    y=click_yvals_iron,
                    marker_color=click_stations[i]["colour"],
                    marker_symbol=click_stations[i]["symbol"],
                    marker_line_color="black",
                    marker_line_width=0.3,
                    marker_size=6,
                )
                fig.data[11 + i * 6].update(
                    x=click_xvals_ratio,
                    y=click_yvals_ratio,
                    marker_color=click_stations[i]["colour"],
                    marker_symbol=click_stations[i]["symbol"],
                    marker_line_color="black",
                    marker_line_width=0.3,
                    marker_size=6,
                )

    # display cruise info
    fig = update_legend(fig, hov_station, click_stations)
    fig.update_yaxes(range=y_range)

    return fig


# MAP PLOTTING
# function to plot the map and the stations on the map
def plot_stations(click_stations):
    # creating a mapbox figure
    fig = px.scatter_mapbox(
        all_data,
        lat="Latitude",
        lon="Longitude",
        custom_data=["Cruise", "Station", "Date"],  # custom data is used for the hovertext
        color="Cruise",
        color_discrete_map={
            "GP02": "red",
            "GA03": "green",
            "GIPY04": "goldenrod",
            "GIPY05": "magenta"},
        center=dict(lat=0, lon=-100),
        zoom=0,
    )
    fig.update_traces(
        hovertemplate="<b>Cruise: %{customdata[0]}</b><br>station: %{customdata[1]}<br>lat: %{lat}<br>lon: %{lon}<br>date: %{customdata[2]}"
    )
    fig.update_layout(mapbox_style="open-street-map")

    # adding markers from: https://plotly.com/python/scattermapbox/
    # the clicked stations are plotted as markers
    if len(click_stations) != 0:
        for i in range(len(click_stations)):
            fig.add_trace(
                go.Scattermapbox(
                    lat=[click_stations[i]["lat"]],
                    lon=[click_stations[i]["lon"]],
                    showlegend=False,
                    hovertemplate="<b>"
                                  + str(click_stations[i]["name"])
                                  + "</b><br>lat: %{lat}</br>lon: %{lon}</br>date: "
                                  + str(click_stations[i]["date"])
                                  + "<extra></extra>",
                    mode="markers",
                    marker=go.scattermapbox.Marker(
                        size=10, color=click_stations[i]["colour"],
                    ),
                )
            )

    return fig


def initialize_map():
    fig = plot_stations([])  # plot the map with empty clicked stations
    return fig


# called when any map parameters are changed
def update_map(click_stations, figure_data):
    fig = plot_stations(click_stations)  # update the plotted clicked stations

    if figure_data is not None:  # set map layout to its previous settings, so the zoom and position doesn't reset
        fig.layout["mapbox"] = figure_data["layout"]["mapbox"]

    return fig
