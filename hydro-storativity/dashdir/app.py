# Run this app with `python app.py` and visit http://127.0.0.1:8050/ in your web browser.

# This is the main file. It contains the dash setup and callbacks.

from os import environ

import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
from flask import Flask

import calculations as calc

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

server = Flask(__name__)
app = dash.Dash(
    server=server,
    requests_pathname_prefix='/store/',
    external_stylesheets=external_stylesheets)

# read in csv files containing the values displayed in the table.
alpha_df = pd.read_csv("./alpha.csv")
porosity_df = pd.read_csv("./porosity.csv")

# read in a markdown file with the introduction and one with sources
introduction = open("introduction.md", "r")
introduction_markdown = introduction.read()

sources = open("sources.md", "r")
sources_markdown = sources.read()

# initial values for the dash components
init_y_plotting = "S"
init_inp_alpha = "avg"
init_inp_porosity = "mid"
init_inp_density = "sea_water"
init_inp_thickness = 15
init_y_axis = "fitted"


# function to initialize the plot
def initialize_plot(y_plotting, inp_alpha, inp_porosity, inp_density, inp_thickness):
    materials = ["Clay", "Sand", "Gravel", "Jointed Rock", "Sound Rock"]

    alpha, porosity, density, thickness = (
        calc.alpha(inp_alpha),
        calc.porosity(inp_porosity),
        calc.density(inp_density),
        inp_thickness,
    )
    # all the calculations of y-values are done in the calculations file
    if y_plotting == "S":
        y_values = calc.storativity(alpha, porosity, density, thickness)
    elif y_plotting == "Ss":
        y_values = calc.specific_storage(alpha, porosity, density)
    elif y_plotting == "Sw":
        y_values = calc.storativity_water_compressibility(porosity, density, thickness)

    fig = go.Figure([go.Bar(x=materials, y=y_values)])
    fig.update_layout(xaxis_title="Material")

    # update axes based on the variable we are plotting
    if y_plotting == "S":
        fig.update_layout(xaxis_title="Material", yaxis_title="S (dimensionless)")
    elif y_plotting == "Ss":
        fig.update_layout(xaxis_title="Material", yaxis_title="Ss (m\u207B\u00B9)")
    elif y_plotting == "Sw":
        fig.update_layout(xaxis_title="Material", yaxis_title="Sw (dimensionless)")
    fig.update_layout(title='<b>Select parameters, then click "Update Plot."</b>')
    fig.update_layout(title_pad_l=120)

    fig.update_layout(
        yaxis_type="log", yaxis_range=[-7, 0]
    )  # our graph has a logarithimic y-axis
    return fig


fig = initialize_plot(
    init_y_plotting,
    init_inp_alpha,
    init_inp_porosity,
    init_inp_density,
    init_inp_thickness,
)

app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Markdown(
                    children=introduction_markdown
                ),  # markdown with the introduction text
            ],
            style={"width": "100%", "display": "inline-block"},
        ),
        html.Div(
            [
                dcc.Graph(
                    id="plot", figure=fig
                ),  # initializing the plot with the figure declared above
                dcc.Markdown(
                    children="""Water Compressibility (beta) = 4.40E-10 m\u00B2/N.""",
                    style={"margin-left": "30px"},
                ),
                html.Div(
                    [
                        # table with values (from the csv file) for alpha. Data Table documentation: https://dash.plotly.com/datatable
                        # styling data tables: https://dash.plotly.com/datatable/style
                        dash_table.DataTable(
                            id="alpha_table",
                            columns=[{"name": i, "id": i} for i in alpha_df.columns],
                            data=alpha_df.to_dict("records"),
                            style_cell={
                                "padding": "5px",
                                "textAlign": "left",
                                "backgroundColor": "Lavender",
                                "font-family": "sans-serif",
                            },
                            style_header={
                                "backgroundColor": "CornflowerBlue",
                                "fontWeight": "bold",
                                "textAlign": "left",
                                "font-family": "sans-serif",
                            },
                        ),
                    ],
                    style={"padding": "30px", "padding-bottom": "0px"},
                ),
                html.Div(
                    [
                        # table with values for porosity.
                        dash_table.DataTable(
                            id="porosity_table",
                            columns=[{"name": i, "id": i} for i in porosity_df.columns],
                            data=porosity_df.to_dict("records"),
                            style_cell={
                                "padding": "5px",
                                "textAlign": "left",
                                "backgroundColor": "Lavender",
                                "font-family": "sans-serif",
                            },
                            style_header={
                                "backgroundColor": "CornflowerBlue",
                                "fontWeight": "bold",
                                "textAlign": "left",
                                "font-family": "sans-serif",
                            },
                        ),
                    ],
                    style={"padding": "30px"},
                ),
            ],
            style={
                "width": "70%",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
        html.Div(
            [
                dcc.Markdown(
                    """
                    **Plot:**
                """
                ),
                dcc.RadioItems(
                    # radiobuttons to choose the y-value we are plotting. Documentation: https://dash.plotly.com/dash-core-components/radioitems
                    id="y_plotting",
                    options=[
                        {"label": "S, storativity", "value": "S"},
                        {"label": "Ss, specific storage", "value": "Ss"},
                        {
                            "label": "Sw, storativity due to compressibility of water",
                            "value": "Sw",
                        },
                    ],
                    value=init_y_plotting,
                    style={"margin-bottom": "30px"},
                ),
                dcc.Markdown(
                    """
            **Alpha (m\u00B2/N):**
        """
                ),
                dcc.RadioItems(
                    id="alpha",
                    options=[
                        {"label": "min", "value": "min"},
                        {"label": "avg", "value": "avg"},
                        {"label": "max", "value": "max"},
                    ],
                    value=init_inp_alpha,
                    labelStyle={"display": "inline-block"},
                    style={"margin-bottom": "30px"},
                ),
                dcc.Markdown(
                    """
            **Porosity:**
        """
                ),
                dcc.RadioItems(
                    id="porosity",
                    options=[
                        {"label": "min", "value": "min"},
                        {"label": "middle", "value": "mid"},
                        {"label": "max", "value": "max"},
                    ],
                    value=init_inp_porosity,
                    labelStyle={"display": "inline-block"},
                    style={"margin-bottom": "30px"},
                ),
                dcc.Markdown(
                    """
            **Water Density (kg/L):**
        """
                ),
                dcc.RadioItems(
                    id="density",
                    options=[
                        {"label": "potable (1.000)", "value": "potable"},
                        {"label": "sea water (1.025)", "value": "sea_water"},
                        {"label": "brine (1.088)", "value": "brine"},
                    ],
                    value=init_inp_density,
                    style={"margin-bottom": "30px"},
                ),
                dcc.Markdown(
                    """
            **Confined Aquifer Thickness (m):**
        """
                ),
                dcc.Slider(
                    # slider to choose value for thickness. Documentation: https://dash.plotly.com/dash-core-components/slider
                    id="thickness",
                    min=1,
                    max=30,
                    step=None,
                    marks={1: "1", 2: "2", 4: "4", 8: "8", 15: "15", 30: "30"},
                    value=init_inp_thickness,
                ),
                html.Button(
                    # From: https://dash.plotly.com/dash-html-components/button
                    "Update Plot",
                    id="submit_button",
                    style={"margin-top": "40px", "margin-bottom": "20px"},
                ),
            ],
            style={
                "width": "30%",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
        dcc.Markdown(
            children=sources_markdown
        ),  # markdown for the sources at the bottom of the page.
    ],
    style={"width": "1000px"},
)


@app.callback(
    Output(component_id="plot", component_property="figure"),
    Input(component_id="submit_button", component_property="n_clicks"),
    Input(component_id="plot", component_property="figure"),
    Input(component_id="y_plotting", component_property="value"),
    Input(component_id="alpha", component_property="value"),
    Input(component_id="porosity", component_property="value"),
    Input(component_id="density", component_property="value"),
    Input(component_id="thickness", component_property="value"),
)
def update_plot(
    submit_button,
    og_fig,
    y_plotting,
    inp_alpha,
    inp_porosity,
    inp_density,
    inp_thickness,
):
    # the if statement is called if the submit button is pressed. This is the only time we update the graph.
    if dash.callback_context.triggered[0]["prop_id"].split(".")[0] == "submit_button":
        materials = ["Clay", "Sand", "Gravel", "Jointed Rock", "Sound Rock"]
        # the variables below are changed from qualitative (e.g. 'min') to quantitative in the calculations file.
        alpha, porosity, density, thickness = (
            calc.alpha(inp_alpha),
            calc.porosity(inp_porosity),
            calc.density(inp_density),
            inp_thickness,
        )
        # get the y-values based on the user-selected y-variable. y-values are calculated in the calculations file.
        if y_plotting == "S":
            y_values = calc.storativity(alpha, porosity, density, thickness)
        elif y_plotting == "Ss":
            y_values = calc.specific_storage(alpha, porosity, density)
        elif y_plotting == "Sw":
            y_values = calc.storativity_water_compressibility(
                porosity, density, thickness
            )

        fig = go.Figure([go.Bar(x=materials, y=y_values)])  # creating the bar chart
        fig.update_layout(xaxis_title="Material")

        # updating axis titles based on what we are plotting.
        if y_plotting == "S":
            fig.update_layout(xaxis_title="Material", yaxis_title="S (dimensionless)")
        elif y_plotting == "Ss":
            fig.update_layout(xaxis_title="Material", yaxis_title="Ss (m\u207B\u00B9)")
        elif y_plotting == "Sw":
            fig.update_layout(xaxis_title="Material", yaxis_title="Sw (dimensionless)")
        fig.update_layout(title='<b>Select parameters, then click "Update Plot."</b>')
        fig.update_layout(title_pad_l=120)

        fig.update_layout(yaxis_type="log", yaxis_range=[-7, 0])
        return fig
    else:
        return (
            og_fig  # we return the original figure if the submit button isn't pressed.
        )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
