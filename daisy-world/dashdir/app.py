# file app.py

# based on this model for now from: https://github.com/strawpants/daisyworld
# nice words about daisyworld at: http://www.jameslovelock.org/biological-homeostasis-of-the-global-environment-the-parable-of-daisyworld/


import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output
import copy
import json

import plotting as plot
import calculations as calc


# Dashboard preliminaries:
es = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=es)

# Load any markdown files to insert into the app:
instructions = open("./assets/instructions.md", "r")
instructions_md = instructions.read()

attributions = open("./assets/attributions.md", "r")
attributions_md = attributions.read()

# Load the dictionary of initial parameters:
with open("init_vars.json") as infile:
    init_vars = json.load(infile)

# Deepcopy of init_vars for callbacks:
live_vars = copy.deepcopy(init_vars)

# Function calls for initializing figures:
constant_flux_temp = plot.constant_flux_temp(
    **init_vars,
)
constant_flux_area = plot.constant_flux_area(
    **init_vars,
)
varying_solar_flux_temp = plot.varying_solar_flux_temp(**init_vars)
varying_solar_flux_area = plot.varying_solar_flux_area(**init_vars)


# Make a dictionary for slider_style for convenience
slider_style = {
    "width": "20%",
    "display": "inline-block",
    "horizontal-align": "top",
}

# Main event:
app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Markdown(
                    """
            ### Welcome to Daisyworld!
                 """
                ),
                html.Img(src=app.get_asset_url("Daisyworld_pict.jpeg")),
                dcc.Markdown(children=instructions_md),
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
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Constant solar flux",
                    children=[
                        html.Div(
                            [
                                ###
                                html.Div(
                                    [
                                        dcc.Markdown(""" White daisy albedo:"""),
                                        dcc.Slider(
                                            id="Aw_1",
                                            min=0.5,
                                            max=1,
                                            step=0.05,
                                            value=init_vars["Albedo"]["w"],
                                            marks={0.5: "0.5", 1: "1"},
                                            tooltip={
                                                "always_visible": True,
                                                "placement": "topLeft",
                                            },
                                        ),
                                    ],
                                    style=slider_style,
                                ),
                                html.Div(
                                    [
                                        dcc.Markdown(""" Black daisy albedo: """),
                                        dcc.Slider(
                                            id="Ab_1",
                                            min=0,
                                            max=0.5,
                                            step=0.05,
                                            value=init_vars["Albedo"]["b"],
                                            marks={0: "0", 0.5: "0.5"},
                                            tooltip={
                                                "always_visible": True,
                                                "placement": "topLeft",
                                            },
                                        ),
                                    ],
                                    style=slider_style,
                                ),
                                html.Div(
                                    [
                                        dcc.Markdown(""" Soil albedo """),
                                        dcc.Slider(
                                            id="Ap_1",
                                            min=0.3,
                                            max=0.7,
                                            step=0.01,
                                            value=init_vars["Albedo"]["none"],
                                            marks={0.3: "0.3", 0.7: "0.7"},
                                            tooltip={
                                                "always_visible": True,
                                                "placement": "topLeft",
                                            },
                                        ),
                                    ],
                                    style=slider_style,
                                ),
                                html.Div(
                                    [
                                        dcc.Markdown("""Insulation factor"""),
                                        dcc.Slider(
                                            id="ins_1",
                                            min=0,
                                            max=0.5,
                                            step=0.05,
                                            value=init_vars["ins_p"],
                                            marks={0: "0", 0.5: "0.5"},
                                            tooltip={
                                                "always_visible": True,
                                                "placement": "topRight",
                                            },
                                        ),
                                    ],
                                    style=slider_style,
                                ),
                                html.Div(
                                    [
                                        dcc.Markdown("""Distance from Sun (AU)"""),
                                        dcc.Slider(
                                            id="distance",
                                            min=0.8,
                                            max=1.2,
                                            step=0.01,
                                            value=1,
                                            marks={0.8: "0.8", 1.2: "1.2"},
                                            tooltip={
                                                "always_visible": True,
                                                "placement": "topRight",
                                            },
                                        ),
                                    ],
                                    style=slider_style,
                                ),
                                html.Button("Reset", id="reset_button", n_clicks=0),
                                dcc.Graph(id="constant_flux_area"),
                            ],
                            style={"width": "100%", "display": "inline-block"},
                        ),
                        html.Div(
                            [
                                dcc.Graph(id="constant_flux_temp"),
                            ],
                            style={"width": "100%", "display": "inline-block"},
                        ),
                    ],
                ),
                dcc.Tab(
                    label="Varying solar flux",
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Markdown(""" White daisy albedo:"""),
                                        dcc.Slider(
                                            id="Aw_2",
                                            min=0.5,
                                            max=1,
                                            step=0.05,
                                            value=init_vars["Albedo"]["w"],
                                            marks={0.5: "0.5", 1: "1"},
                                            tooltip={
                                                "always_visible": True,
                                                "placement": "topLeft",
                                            },
                                        ),
                                    ],
                                    style=slider_style,
                                ),
                                html.Div(
                                    [
                                        dcc.Markdown(""" Black daisy albedo: """),
                                        dcc.Slider(
                                            id="Ab_2",
                                            min=0,
                                            max=0.5,
                                            step=0.05,
                                            value=init_vars["Albedo"]["b"],
                                            marks={0: "0", 0.5: "0.5"},
                                            tooltip={
                                                "always_visible": True,
                                                "placement": "topLeft",
                                            },
                                        ),
                                    ],
                                    style=slider_style,
                                ),
                                html.Div(
                                    [
                                        dcc.Markdown(""" Soil albedo """),
                                        dcc.Slider(
                                            id="Ap_2",
                                            min=0.3,
                                            max=0.7,
                                            step=0.01,
                                            value=init_vars["Albedo"]["none"],
                                            marks={0.3: "0.3", 0.7: "0.7"},
                                            tooltip={
                                                "always_visible": True,
                                                "placement": "topLeft",
                                            },
                                        ),
                                    ],
                                    style=slider_style,
                                ),
                                html.Div(
                                    [
                                        dcc.Markdown("""Insulation factor"""),
                                        dcc.Slider(
                                            id="ins_2",
                                            min=0,
                                            max=0.5,
                                            step=0.05,
                                            value=init_vars["ins_p"],
                                            marks={0: "0", 0.5: "0.5"},
                                            tooltip={
                                                "always_visible": True,
                                                "placement": "topRight",
                                            },
                                        ),
                                    ],
                                    style=slider_style,
                                ),
                                html.Button("Reset", id="reset_button_2", n_clicks=0),
                                dcc.Graph(id="varying_solar_flux_area"),
                                dcc.Graph(id="varying_solar_flux_temp"),
                            ],
                            style={"width": "100%", "display": "inline-block"},
                        ),
                    ],
                ),
            ]
        ),
        html.Div(
            [
                dcc.Markdown(children=attributions_md),
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
        dcc.Store(id="tab1_vars", data={}, storage_type="memory"),
        dcc.Store(id="tab2_vars", data={}, storage_type="memory"),
    ],
    style={"width": "1000px"},
)

#####################################################################
# Tab 1 Callbacks
#####################################################################
# update memory .json live_vars (dcc.Store(id='tab1_vars)')
@app.callback(
    Output(component_id="tab1_vars", component_property="data"),
    Input(component_id="Aw_1", component_property="value"),
    Input(component_id="Ab_1", component_property="value"),
    Input(component_id="Ap_1", component_property="value"),
    Input(component_id="ins_1", component_property="value"),
    Input(component_id="distance", component_property="value"),
)
def update_tab1_vars(Aw_1, Ab_1, Ap_1, ins_1, distance):
    live_vars["Albedo"]["w"] = Aw_1
    live_vars["Albedo"]["b"] = Ab_1
    live_vars["Albedo"]["none"] = Ap_1
    live_vars["ins_p"] = ins_1
    live_vars["Fsnom"] = calc.update_solar_constant(calc.fromAU(distance))
    return json.dumps(live_vars)  # return a json dict


# update figure using the jsonified tab1_vars:
@app.callback(
    Output(component_id="constant_flux_temp", component_property="figure"),
    Output(component_id="constant_flux_area", component_property="figure"),
    Input("tab1_vars", "data"),
)
def update_tab1(jsonified_tab1_vars):
    the_dict = json.loads(jsonified_tab1_vars)
    return plot.constant_flux_temp(**the_dict), plot.constant_flux_area(**the_dict)


# reset sliders on button input:
@app.callback(
    Output("Aw_1", "value"),
    Output("Ab_1", "value"),
    Output("Ap_1", "value"),
    Output("ins_1", "value"),
    Output("distance", "value"),
    Input("reset_button", "n_clicks"),
)
def reset_tab1(n_clicks):
    return (
        init_vars["Albedo"]["w"],
        init_vars["Albedo"]["b"],
        init_vars["Albedo"]["none"],
        init_vars["ins_p"],
        1,
    )


#####################################################################
# Tab 2 Callbacks
#####################################################################
# update memory .json live_vars (dcc.Store(id='tab2_vars)')
@app.callback(
    Output(component_id="tab2_vars", component_property="data"),
    Input(component_id="Aw_2", component_property="value"),
    Input(component_id="Ab_2", component_property="value"),
    Input(component_id="Ap_2", component_property="value"),
    Input(component_id="ins_2", component_property="value"),
)
def update_tab2_vars(Aw_2, Ab_2, Ap_2, ins_2):
    live_vars["Albedo"]["w"] = Aw_2
    live_vars["Albedo"]["b"] = Ab_2
    live_vars["Albedo"]["none"] = Ap_2
    live_vars["ins_p"] = ins_2
    return json.dumps(live_vars)  # return a json dict


# update the figures using the jsonified tab2_vars:
@app.callback(
    Output(component_id="varying_solar_flux_temp", component_property="figure"),
    Output(component_id="varying_solar_flux_area", component_property="figure"),
    Input("tab2_vars", "data"),
)
def update_tab2(jsonified_tab2_vars):
    the_dict = json.loads(jsonified_tab2_vars)
    return plot.varying_solar_flux_temp(**the_dict), plot.varying_solar_flux_area(
        **the_dict
    )


# Reset sliders on button input:
@app.callback(
    Output("Aw_2", "value"),
    Output("Ab_2", "value"),
    Output("Ap_2", "value"),
    Output("ins_2", "value"),
    Input("reset_button_2", "n_clicks"),
)
def reset_tab2(n_clicks):
    return (
        init_vars["Albedo"]["w"],
        init_vars["Albedo"]["b"],
        init_vars["Albedo"]["none"],
        init_vars["ins_p"],
    )


if __name__ == "__main__":
    app.run_server(debug=True)
