# Run this app with `python app.py` and visit http://127.0.0.1:8050/ in your web browser.

# This is the main file. It contains the Dash setup and callbacks, along with any functions needed to update the plots.

import json
from os import environ

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask

# load markdown file for the introduction
introduction = open("introduction.md", "r")
introduction_markdown = introduction.read()
# load the json with descriptions for each of the factors.
with open("descriptions.json") as f:
    descriptions = json.load(f)
# load the csvs with the climate data. There is a file for celsius data, and one for fahrenheit.
land_ocean_data_c = pd.read_csv(
    "./land_ocean_c_filtered.csv"
)  # the observed temperature anomoly data
land_ocean_data_f = pd.read_csv("./land_ocean_f_filtered.csv")
climate_forcings_data_c = pd.read_csv(
    "./climate_forcings_c_filtered.csv"
)  # the temperature change due to forcings
climate_forcings_data_f = pd.read_csv("./climate_forcings_f_filtered.csv")

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

server = Flask(__name__)
app = dash.Dash(
    server=server,
    url_base_pathname=environ.get("JUPYTERHUB_SERVICE_PREFIX", "/"),
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,  # because of the tabs, not all callbacks are accessible so we suppress callback exceptions
)

app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Markdown(
                    children=introduction_markdown  # setting the introduction from the markdown file we loaded in above.
                ),
            ],
            style={
                "width": "100%",
                "display": "inline-block",
                "padding": "0 20",
                "vertical-align": "middle",
                "margin-bottom": 30,
                "margin-right": 50,
                "margin-left": 20,
            },
        ),
        # Tabs: https://dash.plotly.com/dash-core-components/tabs
        html.Div(
            [
                dcc.Tabs(
                    id="tabs",
                    value="learn",
                    children=[
                        dcc.Tab(
                            label="Learn", value="learn"
                        ),  # we have a 'learn' tab and an 'explore' tab
                        dcc.Tab(label="Explore", value="explore"),
                    ],
                ),
                html.Div(id="tabs-content"),
            ],
            style={
                "width": "100%",
                "display": "inline-block",
                "padding": "0 20",
                "vertical-align": "middle",
                "margin-bottom": 30,
                "margin-right": 50,
                "margin-left": 20,
            },
        ),
        html.Iframe(
            src="https://ubc.ca1.qualtrics.com/jfe/form/SV_9zS1U0C7odSt76K",
            style={"height": "800px", "width": "100%", "margin-left": 20,},
        ),
    ],
    style={"width": "1000px"},
)


@app.callback(Output("tabs-content", "children"), Input("tabs", "value"))
def render_content(tab):
    # The structure of the 'learn' tab:
    if tab == "learn":
        return html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(
                            id="learn_graph",
                            config={
                                "displayModeBar": True,
                                "doubleClick": "reset",
                            },
                            # animate=True, #if we set animate to True, there's a fun effect when we change forcings
                        ),
                    ],
                    style={
                        "width": "80%",
                        "display": "inline-block",
                        "vertical-align": "middle",
                    },
                ),
                html.Div(
                    [
                        dcc.Markdown("""**Contributing Factors**"""),
                        dcc.RadioItems(
                            # radiobuttons for each of the forcings (https://dash.plotly.com/dash-core-components/radioitems)
                            id="forcing_radiobuttons",
                            options=[
                                {"label": "Volcanic", "value": "V"},
                                {"label": "Ozone", "value": "O"},
                                {"label": "Orbital Changes", "value": "OC"},
                                {"label": "Solar", "value": "S"},
                                {"label": "Land Use", "value": "LU"},
                                {"label": "Aerosols", "value": "A"},
                                {"label": "Greenhouse Gases", "value": "GG"},
                            ],
                            style={"margin-bottom": "50px"},
                        ),
                        dcc.Markdown("""**Units**"""),
                        dcc.RadioItems(
                            # radiobuttons to switch between plotting celsius and fahrenheit
                            id="units",
                            options=[
                                {"label": "Celsius", "value": "C"},
                                {"label": "Fahrenheit", "value": "F"},
                            ],
                            value="C",
                        ),
                    ],
                    style={
                        "width": "20%",
                        "display": "inline-block",
                        "vertical-align": "middle",
                    },
                ),
                html.Div(
                    [
                        # markdown that will display the description of the forcing, from the json that was loaded in above
                        dcc.Markdown(
                            children="""**Text**""",
                            id="description",
                            style={"font-size": "14px"},
                        ),
                    ]
                ),
            ]
        )
    # The structure of the 'explore' tab:
    elif tab == "explore":
        return html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(
                            id="explore_graph",
                            config={
                                "displayModeBar": True,
                                "modeBarButtonsToAdd": [
                                    "drawline",
                                    "drawcircle",
                                    "eraseshape",
                                ],
                                "doubleClick": "reset",
                            },
                        ),
                    ],
                    style={
                        "width": "80%",
                        "display": "inline-block",
                        "vertical-align": "middle",
                    },
                ),
                html.Div(
                    [
                        dcc.Markdown("""**Contributing Factors**"""),
                        dcc.Checklist(
                            # checklist for forcings (https://dash.plotly.com/dash-core-components/checklist)
                            id="forcing_checklist",
                            options=[
                                {"label": "Volcanic", "value": "V"},
                                {"label": "Ozone", "value": "O"},
                                {"label": "Orbital Changes", "value": "OC"},
                                {"label": "Solar", "value": "S"},
                                {"label": "Land Use", "value": "LU"},
                                {"label": "Aerosols", "value": "A"},
                                {"label": "Greenhouse Gases", "value": "GG"},
                            ],
                            value=[],
                        ),
                        dcc.Checklist(
                            # checkbox if they want to plot the sum of multiple factors
                            id="add_forcings",
                            options=[
                                {
                                    "label": "Sum selected factors",
                                    "value": "add_forcings",
                                },
                            ],
                            value=[],
                            style={"margin-top": "30px", "margin-bottom": "30px"},
                        ),
                        dcc.Markdown("""**Units**"""),
                        dcc.RadioItems(
                            # radiobuttons to choose to plot in celsius or fahrenheit
                            id="units",
                            options=[
                                {"label": "Celsius", "value": "C"},
                                {"label": "Fahrenheit", "value": "F"},
                            ],
                            value="C",
                        ),
                    ],
                    style={
                        "width": "20%",
                        "display": "inline-block",
                        "vertical-align": "middle",
                    },
                ),
                html.Div(
                    [
                        dcc.Textarea(
                            # text box to type in student information
                            id="text_area",
                            value="Name: \nStudent Number: \nComments: ",
                            style={
                                "width": "70%",
                                "height": 150,
                                "margin-left": "80px",
                            },
                        ),
                    ]
                ),
            ]
        )


@app.callback(
    Output(component_id="description", component_property="children"),
    Input(component_id="forcing_radiobuttons", component_property="value"),
)
def update_description(forcing):
    # update the desctiption below the plot for the 'learn' tab
    output = []
    if forcing is not None:
        output += descriptions[forcing]
    return output


def update_learn_factors(fig, factors, units):
    # decide which data to use based on units
    if units == "C":
        data = climate_forcings_data_c
    elif units == "F":
        data = climate_forcings_data_f

    # colors: https://www.w3schools.com/cssref/css_colors.asp
    # several arrays with the properties of each factor so I can loop through them all to update
    colour_name = [
        "DeepSkyBlue",
        "Orange",
        "Red",
        "Sienna",
        "CadetBlue",
        "MediumSlateBlue",
        "SeaGreen",
        "GreenYellow",
        "DarkGrey",
        "Purple",
    ]
    colour_rgb = [
        "rgba(0, 191, 255, 0.2)",
        "rgba(255, 165, 0, 0.2)",
        "rgba(255, 0, 0, 0.2)",
        "rgba(136, 45, 23, 0.2)",
        "rgba(95, 158, 160, 0.2)",
        "rgba(123, 104, 238, 0.2)",
        "rgba(46, 139, 87, 0.2)",
        "rgba(173, 255, 47, 0.2)",
        "rgba(169, 169, 169, 0.2)",
        "rgba(128, 0, 128, 0.2)",
    ]
    name = ["OC", "S", "V", "LU", "O", "A", "GG", "N", "H", "ALL"]
    label_name = [
        "Orbital Changes",
        "Solar",
        "Volcanic",
        "Land Use",
        "Ozone",
        "Aerosols",
        "Greenhouse Gases",
        "Natural Forcings",
        "Human Forcings",
        "All Forcings",
    ]
    df_name = [
        "Orbital changes",
        "Solar",
        "Volcanic",
        "Land use",
        "Ozone",
        "Anthropogenic tropospheric aerosol",
        "Greenhouse gases",
        "Natural",
        "Human",
        "All forcings",
    ]
    for i in range(10):
        if name[i] in factors:
            # error bars: https://plotly.com/python/continuous-error-bars/
            # start with empty data for the 'learn' tab, and it will be plotted when 'play' is pressed
            new_fig = px.line(
                data, x=None, y=None, color_discrete_sequence=[colour_name[i]]
            )
            new_fig.update_traces(
                hovertemplate="Year: %{x}<br>" + label_name[i] + ": %{y:.3f}"
            )
            new_fig_error = go.Figure(
                [
                    go.Scatter(
                        name="Upper Bound",
                        x=[None],
                        y=[None],
                        mode="lines",
                        marker=dict(color="#444"),
                        line=dict(width=0),
                        showlegend=False,
                    ),
                    go.Scatter(
                        name="Lower Bound",
                        x=[None],
                        y=[None],
                        marker=dict(color="#444"),
                        line=dict(width=0),
                        mode="lines",
                        fillcolor=colour_rgb[i],
                        fill="tonexty",
                        showlegend=False,
                    ),
                ]
            )

            new_fig_error.update_traces(
                hovertemplate="Year: %{x}<br>" + label_name[i] + ": %{y:.3f}"
            )  # format how many decimals are seen when we hover over data
            fig.add_traces(new_fig_error.data)  # add the traces to the main figure
            fig.add_trace(new_fig.data[0])

            # animation from: https://stackoverflow.com/questions/62231223/animated-lineplot-with-python-plotly
            fig.update(
                frames=[
                    go.Frame(
                        data=[
                            # add frames for the full data, including error bars.
                            go.Scatter(
                                x=data["Year"][:k],
                                y=(data[df_name[i]] + data["Error"])[:k],
                            ),
                            go.Scatter(
                                x=data["Year"][:k],
                                y=(data[df_name[i]] - data["Error"])[:k],
                            ),
                            go.Scatter(x=data["Year"][:k], y=data[df_name[i]][:k]),
                        ]
                    )
                    for k in range(1, len(data) + 1)
                ]
            )

            # update layout for animation. Add play, pause buttons, give animation parameters
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="right",
                        pad={"r": 20, "l": 50},
                        xanchor="left",
                        yanchor="top",
                        buttons=[
                            dict(
                                label="Play",
                                method="animate",
                                args=[
                                    None,
                                    dict(
                                        frame={"duration": 1, "redraw": False},
                                        fromcurrent=True,
                                        transition={"duration": 300},
                                    ),
                                ],
                            ),
                            dict(
                                label="Pause",
                                method="animate",
                                args=[
                                    [None],
                                    dict(
                                        frame={"duration": 0, "redraw": False},
                                        mode="immediate",
                                        transition={"duration": 0},
                                    ),
                                ],
                            ),
                        ],
                    )
                ]
            )

    fig.update_xaxes(
        range=[1880, 2010]
    )  # update the xaxis because plotting empty data changes xrange
    fig.update_layout(showlegend=False)  # we don't want to show traces in the legend
    return fig


def update_explore_factors(fig, factors, units):
    # update which data we use based on units
    if units == "C":
        data = climate_forcings_data_c
    elif units == "F":
        data = climate_forcings_data_f

    # colors: https://www.w3schools.com/cssref/css_colors.asp
    colour_name = [
        "DeepSkyBlue",
        "Orange",
        "Red",
        "Sienna",
        "CadetBlue",
        "MediumSlateBlue",
        "SeaGreen",
        "GreenYellow",
        "DarkGrey",
        "Purple",
    ]
    colour_rgb = [
        "rgba(0, 191, 255, 0.2)",
        "rgba(255, 165, 0, 0.2)",
        "rgba(255, 0, 0, 0.2)",
        "rgba(136, 45, 23, 0.2)",
        "rgba(95, 158, 160, 0.2)",
        "rgba(123, 104, 238, 0.2)",
        "rgba(46, 139, 87, 0.2)",
        "rgba(173, 255, 47, 0.2)",
        "rgba(169, 169, 169, 0.2)",
        "rgba(128, 0, 128, 0.2)",
    ]
    name = ["OC", "S", "V", "LU", "O", "A", "GG", "N", "H", "ALL"]
    label_name = [
        "Orbital Changes",
        "Solar",
        "Volcanic",
        "Land Use",
        "Ozone",
        "Aerosols",
        "Greenhouse Gases",
        "Natural Forcings",
        "Human Forcings",
        "All Forcings",
    ]
    df_name = [
        "Orbital changes",
        "Solar",
        "Volcanic",
        "Land use",
        "Ozone",
        "Anthropogenic tropospheric aerosol",
        "Greenhouse gases",
        "Natural",
        "Human",
        "All forcings",
    ]
    for i in range(10):
        if name[i] in factors:
            # error bars: https://plotly.com/python/continuous-error-bars/
            new_fig = px.line(
                data, x="Year", y=df_name[i], color_discrete_sequence=[colour_name[i]]
            )
            new_fig.update_traces(
                hovertemplate="Year: %{x}<br>" + label_name[i] + ": %{y:.3f}"
            )
            new_fig_error = go.Figure(
                [
                    go.Scatter(
                        name="Upper Bound",
                        x=data["Year"],
                        y=data[df_name[i]] + data["Error"],
                        mode="lines",
                        marker=dict(color="#444"),
                        line=dict(width=0),
                        showlegend=False,
                    ),
                    go.Scatter(
                        name="Lower Bound",
                        x=data["Year"],
                        y=data[df_name[i]] - data["Error"],
                        marker=dict(color="#444"),
                        line=dict(width=0),
                        mode="lines",
                        fillcolor=colour_rgb[i],
                        fill="tonexty",
                        showlegend=False,
                    ),
                ]
            )
            new_fig_error.update_traces(
                hovertemplate="Year: %{x}<br>" + label_name[i] + ": %{y:.3f}"
            )
            fig.add_traces(new_fig_error.data)
            fig.add_trace(new_fig.data[0])

    return fig


# function to sum all selected factors and plot one line (used by 'explore' tab)
def add_factors(fig, factors, units):
    # select data based on units
    if units == "C":
        data = climate_forcings_data_c
    elif units == "F":
        data = climate_forcings_data_f

    y = [0] * len(data)

    name = ["OC", "S", "V", "LU", "O", "A", "GG", "N", "H", "ALL"]
    df_name = [
        "Orbital changes",
        "Solar",
        "Volcanic",
        "Land use",
        "Ozone",
        "Anthropogenic tropospheric aerosol",
        "Greenhouse gases",
        "Natural",
        "Human",
        "All forcings",
    ]
    for i in range(
        10
    ):  # loop through each factor and if it is selected, add its values to 'y'
        if name[i] in factors:
            y += data[df_name[i]]

    # plotting. Done the same as in previous functions.
    new_fig = px.line(x=data["Year"], y=y, color_discrete_sequence=["purple"])
    new_fig.update_traces(hovertemplate="Year: %{x}<br> Summed Factors: %{y:.3f}")
    new_fig_error = go.Figure(
        [
            go.Scatter(
                name="Upper Bound",
                x=data["Year"],
                y=y + data["Error"],
                mode="lines",
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False,
            ),
            go.Scatter(
                name="Lower Bound",
                x=data["Year"],
                y=y - data["Error"],
                marker=dict(color="#444"),
                line=dict(width=0),
                mode="lines",
                fillcolor="rgba(128, 0, 128, 0.2)",
                fill="tonexty",
                showlegend=False,
            ),
        ]
    )
    new_fig_error.update_traces(hovertemplate="Year: %{x}<br> Summed Factors: %{y:.3f}")
    fig.add_traces(new_fig_error.data)
    fig.add_trace(new_fig.data[0])
    return fig


@app.callback(
    Output(component_id="learn_graph", component_property="figure"),
    Input(component_id="forcing_radiobuttons", component_property="value"),
    Input(component_id="units", component_property="value"),
)
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
            text="<b>observed<br>temperature anomaly</b>",
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
        else:
            text_output += chr

    # character limit = 80
    # if a line is longer than 80 characters, wrap it to the next line.
    output = text_output.split("<br>")
    new_output = ""
    for i in output:
        if len(i) > 80:
            chunks = [i[j : j + 80] for j in range(0, len(i), 80)]
            for k in chunks:
                new_output += k + "<br>"
        else:
            new_output += i + "<br>"

    text_output = new_output

    # update the annotation on the figure with our text
    fig.update_layout(margin=dict(b=150))
    fig.update_layout(
        annotations=[
            go.layout.Annotation(
                text=text_output,
                align="left",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0,
                y=-0.5,
                bordercolor="black",
                borderwidth=0,
                borderpad=5,
            )
        ]
    )

    return fig


@app.callback(
    Output(component_id="explore_graph", component_property="figure"),
    Input(component_id="forcing_checklist", component_property="value"),
    Input(component_id="add_forcings", component_property="value"),
    Input(component_id="text_area", component_property="value"),
    Input(component_id="units", component_property="value"),
)
def update_explore_plot(forcings, add_forcings, text_input, units):
    # select data based on units
    if units == "C":
        data = land_ocean_data_c
    if units == "F":
        data = land_ocean_data_f

    # add axis lines
    fig = px.line()
    fig.update_layout(
        plot_bgcolor="rgb(255, 255, 255)",
        yaxis_zeroline=True,
        yaxis_zerolinecolor="gainsboro",
        yaxis_showline=True,
        yaxis_linecolor="gainsboro",
    )

    # if the checkbox to sum selected factors is checked, we call 'add_factors'. Otherwise we plot like normal with 'update_explore_factors'
    if add_forcings != ["add_forcings"]:
        fig = update_explore_factors(fig, forcings, units)
    elif len(forcings) > 0:
        fig = add_factors(fig, forcings, units)

    # plot the observed temperature anomaly
    figTemp = px.line(
        data, x="Year", y="Annual_Mean", color_discrete_sequence=["black"]
    )
    fig.add_trace(figTemp.data[0])

    # update the annotation on the graph with student comments
    if text_input is not None:
        fig = update_text(fig, text_input)

    # update yaxis range based on units, and add the annotation for 'observed temperature anomaly'
    if units == "C":
        fig.update_yaxes(title="Temperature Anomaly (ºC)", range=[-1.2, 1.2])
        # annotation
        fig.add_annotation(
            x=2005,
            y=0.938064516129032,
            text="<b>observed<br>temperature anomaly</b>",
            showarrow=True,
            arrowhead=1,
        )
    elif units == "F":
        fig.update_yaxes(
            title="Temperature Anomaly (ºF)", range=[-1.2 * 1.8, 1.2 * 1.8]
        )
        # annotation
        fig.add_annotation(
            x=2005,
            y=0.938064516129032 * 1.8,
            text="<b>observed<br>temperature anomaly</b>",
            showarrow=True,
            arrowhead=1,
        )

    # add the ability to draw on the plot
    fig.update_layout(
        # dragmode='drawline',
        newshape=dict(line_color="magenta"),
        height=500,
    )

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
