"""Bamfield CTD archive dashboard.

Run in the ``notebook`` conda env and open http://127.0.0.1:8050/ :

    /Users/hjb62/miniconda3/bin/conda run -n notebook python app.py

Data come from ``data/``, written by ``build_dashboard_data.py``. Layout follows the EOSC 372
ocgy-dataviewer (map, hover-preview, click-to-pin, vertical depth slider, Clear button), but every
figure is rebuilt in its callback rather than patched by trace index.
"""
from pathlib import Path

import dash
from dash import Input, Output, State, ctx, dcc, html, no_update
from flask import Flask

import plotting as plot
import upload as up

HERE = Path(__file__).resolve().parent
instructions = (HERE / "instructions.md").read_text()
attributions = (HERE / "attributions.md").read_text()

MAX_DEPTH = 250
VARIABLE_OPTIONS = [{"label": plot.SHORT[v], "value": v} for v in plot.LABELS]
DEFAULT_VARIABLES = ["CT", "SA", "sigma0", "DO"]

server = Flask(__name__)
app = dash.Dash(
    __name__, server=server,
    # requests_pathname_prefix='/bamfield-ctd/',  # uncomment for deployment behind the server proxy
    title="Bamfield CTD archive",
)

label_style = {"fontWeight": "bold", "marginRight": "8px"}

app.layout = html.Div([
    dcc.Markdown(instructions),


    html.Div([
        html.H4("Compare your own casts", style={"margin": "0 0 6px"}),
        dcc.Markdown(
            "Put your binned downcasts into the CSV template, one row per depth bin. Start each "
            "cast with its label (the station name will do), position and date on its first "
            "row; several casts at one site are fine. Each cast is drawn in its own warm colour "
            "at its nearest site, alongside that site's casts and usual range. Rows at 1 m and "
            "shallower are left out, as they are for the archive (the surface soak). The file stays in "
            "your browser: nothing is stored on the server.\n\n"
            "**Units.** `depth_m` in metres; `temperature_c` is in-situ temperature in °C, and "
            "`practical_salinity` is Practical Salinity (no units), both as the CTD reports them. "
            "Do not convert them: the dashboard converts them to Conservative Temperature and "
            "Absolute Salinity (TEOS-10) itself, as it does for the archive. Optional: "
            "`oxygen_umol_l` in µmol L⁻¹ (from ml L⁻¹, multiply by 44.66), and `fluorescence` "
            "and `par` in any units.",
            style={"fontSize": "13px"}),
        html.Div([
            html.Button("Download the template", id="template_button"),
            dcc.Download(id="template_download"),
            dcc.Upload(id="upload_file", accept=".csv", max_size=up.MAX_BYTES, multiple=False,
                       children=html.Button("Upload casts (.csv)"),
                       style={"display": "inline-block"}),
            html.Button("Remove them", id="upload_remove"),
            dcc.Checklist(id="only_mine", value=[],
                          options=[{"label": " Show only my casts", "value": "only"}],
                          inputStyle={"marginRight": "4px"}),
        ], style={"display": "flex", "gap": "10px", "alignItems": "center",
                  "flexWrap": "wrap"}),
        html.Div([
            html.Span("Show:", style=label_style),
            dcc.Dropdown(id="upload_show", multi=True, options=[], value=[], clearable=True,
                         placeholder="Choose which of your casts to show",
                         style={"flex": "1", "minWidth": "300px"}),
        ], id="upload_show_box",
            style={"display": "none", "alignItems": "center", "marginTop": "8px"}),
        html.Div(id="upload_status", style={"marginTop": "6px", "fontSize": "13px"}),
    ], style={"border": "1px solid #ddd", "borderRadius": "6px", "padding": "10px 12px",
              "marginBottom": "10px"}),

    html.Div([
        html.Span("View", style=label_style),
        dcc.RadioItems(id="mode", value="site", inline=True,
                       options=[{"label": " One site, all years ", "value": "site"},
                                {"label": " One year, several sites ", "value": "year"}],
                       style={"display": "inline-block", "marginRight": "24px"}),
        html.Span("Year", style=label_style),
        dcc.Dropdown(id="year", options=[{"label": str(y), "value": int(y)} for y in plot.YEARS],
                     value=int(plot.YEARS[-1]), clearable=False,
                     style={"width": "110px", "display": "inline-block", "verticalAlign": "middle"}),
        html.Button("Clear", id="clear", style={"marginLeft": "24px"}),
    ], style={"display": "flex", "alignItems": "center", "flexWrap": "wrap", "gap": "4px",
              "marginBottom": "8px"}),

    html.Div([
        html.Div(dcc.Graph(id="map", clear_on_unhover=True,
                           config={"scrollZoom": True, "displayModeBar": False}),
                 style={"flex": "3 1 500px", "minWidth": "400px"}),
        html.Div(dcc.Graph(id="grid", config={"displayModeBar": False}),
                 style={"flex": "2 1 380px", "minWidth": "340px"}),
    ], style={"display": "flex", "flexWrap": "wrap", "gap": "10px"}),

    html.Div([
        html.Span("Variables", style=label_style),
        dcc.Checklist(id="variables", options=VARIABLE_OPTIONS, value=DEFAULT_VARIABLES,
                      inline=True, inputStyle={"marginLeft": "12px", "marginRight": "4px"}),
    ], style={"display": "flex", "alignItems": "center", "margin": "12px 0 4px"}),

    html.Div([
        html.Div([
            html.Div("Depth (m)", style={"fontWeight": "bold", "fontSize": "12px",
                                         "marginBottom": "6px"}),
            # Slider runs -MAX_DEPTH..0 so the deep end sits at the bottom; abs() is taken later.
            dcc.RangeSlider(id="depth", min=-MAX_DEPTH, max=0, step=1, value=[-MAX_DEPTH, 0],
                            vertical=True, verticalHeight=440,
                            marks={-d: str(d) for d in range(0, MAX_DEPTH + 1, 50)}),
        ], style={"width": "70px", "paddingTop": "20px"}),
        html.Div(dcc.Graph(id="profiles", config={"displayModeBar": "hover",
                                                  "toImageButtonOptions": {"format": "png",
                                                                           "filename": "ctd_profiles",
                                                                           "scale": 2}}),
                 style={"flex": "1 1 auto", "minWidth": "0"}),
    ], style={"display": "flex"}),

    html.H4("Several variables on one depth axis", style={"marginTop": "24px"}),
    dcc.Markdown(
        "Colour marks the variable, each with its own axis along the top; line style marks the "
        f"cast (up to {plot.MAX_MULTIAX_CASTS}). Casts come from the sites selected on the map "
        "(that year only in the year view). The slider beside it sets its depth range."),
    html.Div([
        html.Span("Variables", style=label_style),
        dcc.Checklist(id="multiax_variables", options=VARIABLE_OPTIONS, value=["CT", "DO"],
                      inline=True, inputStyle={"marginLeft": "12px", "marginRight": "4px"}),
    ], style={"display": "flex", "alignItems": "center", "margin": "4px 0"}),
    html.Div([
        html.Span("Casts", style=label_style),
        dcc.Dropdown(id="multiax_casts", multi=True, options=[], value=[],
                     placeholder="Select a site on the map first",
                     style={"flex": "1 1 auto"}),
    ], style={"display": "flex", "alignItems": "center", "margin": "4px 0"}),
    html.Div([
        html.Div([
            html.Div("Depth (m)", style={"fontWeight": "bold", "fontSize": "12px",
                                         "marginBottom": "6px"}),
            dcc.RangeSlider(id="multiax_depth", min=-MAX_DEPTH, max=0, step=1,
                            value=[-MAX_DEPTH, 0], vertical=True,
                            verticalHeight=plot.MULTIAX_PLOT_PX,
                            marks={-d: str(d) for d in range(0, MAX_DEPTH + 1, 50)}),
        ], style={"width": "70px"}),
        html.Div(dcc.Graph(id="multiax", config={"displayModeBar": "hover",
                                                 "toImageButtonOptions": {"format": "png",
                                                                          "filename": "ctd_multiaxis",
                                                                          "scale": 2}}),
                 style={"flex": "1 1 auto", "minWidth": "0"}),
    ], style={"display": "flex", "alignItems": "flex-end"}),

    html.H4("Temperature–salinity diagram", style={"marginTop": "24px"}),
    dcc.Markdown(
        "The casts chosen above, over the depth range of the slider beside them: every 0.5 m bin as "
        "Conservative Temperature against Absolute Salinity, with dashed σ₀ isopycnals. Each cast "
        "has its own marker; colour is the variable chosen here, on one scale for all casts."),
    html.Div([
        html.Span("Colour by", style=label_style),
        dcc.Dropdown(id="ts_colour", value="DO", clearable=False,
                     options=[{"label": lab.split(" (")[0], "value": v}
                              for v, (lab, _) in plot.TS_COLOUR_OPTIONS.items()],
                     style={"width": "220px"}),
    ], style={"display": "flex", "alignItems": "center", "margin": "4px 0"}),
    dcc.Graph(id="ts", config={"displayModeBar": "hover", "responsive": False,
                               "toImageButtonOptions": {"format": "png", "filename": "ctd_ts",
                                                        "scale": 2}},
              style={"width": "fit-content"}),

    html.H4("Year to year, with the site effect taken out", style={"marginTop": "24px"}),
    dcc.Markdown(
        "Each cast's mean over the chosen layer, taken relative to its own site's typical value "
        "(median polish over sites × years, sites with at least five years only). The open grey "
        "circles are the naive median of every cast that year, wherever it was taken: where the "
        "two disagree, the year sampled unusual places."),
    html.Div([
        html.Span("Variable", style=label_style),
        dcc.Dropdown(id="index_variable", value="DO", clearable=False,
                     options=[{"label": plot.SHORT[v], "value": v}
                              for v in ["CT", "SA", "sigma0", "DO"]],
                     style={"width": "150px", "display": "inline-block", "verticalAlign": "middle"}),
        html.Span("Layer", style={**label_style, "marginLeft": "24px"}),
        dcc.RadioItems(id="index_layer", value="below 150 m", inline=True,
                       options=[{"label": f" {l} ", "value": l}
                                for l in plot.anomalies["layer"].unique()]),
    ], style={"display": "flex", "alignItems": "center", "gap": "4px"}),
    dcc.Graph(id="index", config={"displayModeBar": False}),

    dcc.Markdown(attributions, style={"marginTop": "24px", "fontSize": "12px", "color": "#555"}),
    dcc.Store(id="selected", data=[]),
    dcc.Store(id="upload", storage_type="session", data=None),   # the viewer's browser only
    dcc.Store(id="upload_view", data=None),   # the uploaded casts chosen in "Show:"
], style={"maxWidth": "1300px", "margin": "0 auto", "padding": "12px",
          "fontFamily": "Helvetica, Arial, sans-serif"})


def _site_from_point(data):
    """The site_id under a map hover or click, or None.

    Map traces do not always carry ``customdata`` into their click and hover events (a typed
    array is silently dropped), so fall back on the point's position, which is always sent:
    every marker sits exactly at its site's median position.
    """
    if not data or not data.get("points"):
        return None
    pt = data["points"][0]
    cd = pt.get("customdata")
    if cd is not None:
        return int(cd[0] if isinstance(cd, list) else cd)
    if pt.get("lat") is None or pt.get("lon") is None:
        return None
    d2 = (plot.sites["latitude"] - pt["lat"]) ** 2 + (plot.sites["longitude"] - pt["lon"]) ** 2
    best = d2.idxmin()
    return int(best) if d2[best] < 1e-8 else None


_NAME_TO_ID = {name: int(s) for s, name in plot.sites["name"].items()}


@app.callback(
    Output("selected", "data"), Output("mode", "value"), Output("year", "value"),
    Input("map", "clickData"), Input("grid", "clickData"), Input("clear", "n_clicks"),
    Input("mode", "value"),
    State("selected", "data"), State("year", "value"),
    prevent_initial_call=True,
)
def update_selection(map_click, grid_click, _clear, mode, selected, year):
    trigger = ctx.triggered_id
    selected = list(selected or [])
    if trigger == "clear":
        return [], mode, year
    if trigger == "mode":
        # Keep at most one site when switching to the single-site view.
        return (selected[:1] if mode == "site" else selected), mode, year
    if trigger == "grid" and grid_click:
        pt = grid_click["points"][0]
        site, clicked_year = _NAME_TO_ID[pt["y"]], int(pt["x"])
        if pt.get("z") is None:      # an empty cell: nothing was cast there that year
            return selected, mode, year
        # A grid cell is one site in one year, so open the year view on it.
        if mode == "year" and clicked_year == year:
            if site not in selected:
                selected.append(site)
            return selected, "year", year
        return [site], "year", clicked_year
    if trigger == "map":
        site = _site_from_point(map_click)
        if site is None:
            return selected, mode, year
        if mode == "site":
            return ([] if selected == [site] else [site]), mode, year
        if site in selected:
            selected.remove(site)
        else:
            selected.append(site)
        return selected, mode, year
    return selected, mode, year


@app.callback(Output("template_download", "data"), Input("template_button", "n_clicks"),
              prevent_initial_call=True)
def download_template(_):
    return dict(content=up.template_csv(), filename="ctd_cast_template.csv")


@app.callback(
    Output("upload", "data"), Output("upload_status", "children"),
    Output("selected", "data", allow_duplicate=True), Output("mode", "value", allow_duplicate=True),
    Output("upload_show", "options"), Output("upload_show", "value"),
    Output("upload_show_box", "style"),
    Input("upload_file", "contents"), Input("upload_remove", "n_clicks"),
    State("upload_file", "filename"), State("selected", "data"), State("mode", "value"),
    prevent_initial_call=True,
)
def receive_upload(contents, _remove, filename, selected, mode):
    hidden = {"display": "none"}
    if ctx.triggered_id == "upload_file" and not contents:   # emptied by reset_upload_box
        return (no_update,) * 7
    if ctx.triggered_id == "upload_remove":
        return None, "", selected, mode, [], [], hidden
    try:
        uploads = up.read_upload(contents, filename or "")
    except ValueError as err:
        return (None, html.Span(str(err), style={"color": "#b00020"}), selected, mode,
                [], [], hidden)
    lines = []
    for c in uploads:
        c["site_id"], c["site_km"] = up.nearest_site(c, plot.sites)
        far = " (more than 1 km away: compare with care)" if c["site_km"] > 1.0 else ""
        lines.append(html.Li(
            f"{plot.upload_label(c)}: {c['n']} bins to {c['max_depth']:.1f} m; nearest site "
            f"{plot.site_name(c['site_id'])}, {c['site_km']:.2f} km{far}",
            style={"color": plot.upload_colour(c, uploads)}))
    sites_hit = list(dict.fromkeys(c["site_id"] for c in uploads))
    status = html.Div([f"{len(uploads)} cast(s) read from {filename}:",
                       html.Ul(lines, style={"margin": "2px 0"})])
    # One site: open it. Several: the year-free site view can show only one, so open the first
    # and let the user click the others (each shows the casts nearest it).
    options = [{"label": f"{plot.upload_label(c)}, at {plot.site_name(c['site_id'])}",
                "value": c["id"]} for c in uploads]
    shown = {"display": "flex", "alignItems": "center", "marginTop": "8px"}
    return (uploads, status, sites_hit[:1], "site", options, [c["id"] for c in uploads], shown)


# After every read or removal, empty the upload box, both its contents and the browser's file
# input. A browser does not report choosing the same file again in the same input, so without
# this a removed (or edited and saved) file could not be uploaded a second time.
app.clientside_callback(
    """function(_data, _remove) {
        document.querySelectorAll('#upload_file input[type=file]').forEach(i => { i.value = ''; });
        return null;
    }""",
    Output("upload_file", "contents", allow_duplicate=True),
    Input("upload_status", "children"), Input("upload_remove", "n_clicks"),
    prevent_initial_call=True,
)


@app.callback(
    Output("upload_view", "data"), Output("selected", "data", allow_duplicate=True),
    Input("upload", "data"), Input("upload_show", "value"),
    State("selected", "data"), State("mode", "value"),
    prevent_initial_call=True,
)
def choose_uploads(uploads, show, selected, mode):
    """The uploaded casts to draw. If none of them is at the open site, open the first one's."""
    view = [c for c in (uploads or []) if c["id"] in (show or [])]
    if (ctx.triggered_id == "upload_show" and view and mode == "site"
            and not plot.uploads_at(view, selected or [])):
        return view, [view[0]["site_id"]]
    return view, selected


@app.callback(Output("map", "figure"),
              Input("mode", "value"), Input("year", "value"), Input("selected", "data"),
              Input("upload_view", "data"), Input("only_mine", "value"))
def update_map(mode, year, selected, cast, only_mine):
    return plot.make_map(mode, year, selected or [], cast, bool(only_mine))


@app.callback(Output("grid", "figure"), Input("selected", "data"))
def update_grid(selected):
    return plot.make_grid(selected or [])


@app.callback(
    Output("profiles", "figure"),
    Input("mode", "value"), Input("year", "value"), Input("selected", "data"),
    Input("map", "hoverData"), Input("variables", "value"), Input("depth", "value"),
    Input("upload_view", "data"), Input("only_mine", "value"),
)
def update_profiles(mode, year, selected, hover, variables, depth, cast, only_mine):
    depth_range = sorted(abs(d) for d in depth)
    ordered = [v for v in plot.LABELS if v in (variables or [])]
    return plot.make_profiles(mode, year, selected or [], _site_from_point(hover),
                              ordered, depth_range, cast, bool(only_mine))


@app.callback(
    Output("multiax_casts", "options"), Output("multiax_casts", "value"),
    Input("mode", "value"), Input("year", "value"), Input("selected", "data"),
    Input("upload_view", "data"), Input("only_mine", "value"), State("multiax_casts", "value"),
)
def update_multiax_casts(mode, year, selected, uploads, only_mine, current):
    if only_mine and uploads:               # your casts only: offer all of them
        options = [{"label": plot.upload_label(c), "value": c["id"]} for c in uploads]
        ids = [c["id"] for c in uploads]
        kept = ids if ctx.triggered_id in ("only_mine", "upload_view") else ([p for p in (current or []) if p in ids] or ids)
        return options, kept[:plot.MAX_MULTIAX_CASTS]
    offered = plot.multiax_cast_options(mode, year, selected or [])
    options = [{"label": plot.cast_label(p), "value": p} for p in offered]
    mine = [c["id"] for c in plot.uploads_at(uploads, selected or [])]
    if mine:
        offered = mine + offered
        options = [{"label": plot.upload_label(c), "value": c["id"]}
                   for c in plot.uploads_at(uploads, selected or [])] + options
    kept = [p for p in (current or []) if p in offered]
    if ctx.triggered_id in ("upload_view", "selected", "only_mine") and mine:
        kept = mine + [p for p in kept if p not in mine]
    if not kept and offered:
        # Default: your casts, then the latest cast at each selected site.
        latest = {}
        for p in offered:
            if p.startswith(plot.UPLOAD_PREFIX):
                latest[p] = p
                continue
            latest[plot.casts.loc[plot.casts["profile"] == p, "site_id"].iloc[0]] = p
        kept = list(latest.values())
    return options, kept[:plot.MAX_MULTIAX_CASTS]


@app.callback(Output("multiax", "figure"),
              Input("multiax_casts", "value"), Input("multiax_variables", "value"),
              Input("multiax_depth", "value"), Input("upload_view", "data"))
def update_multiax(chosen, variables, depth, cast):
    depth_range = sorted(abs(d) for d in depth)
    ordered = [v for v in plot.LABELS if v in (variables or [])]
    ids = {c["id"] for c in (cast or [])}
    chosen = [p for p in (chosen or []) if not p.startswith(plot.UPLOAD_PREFIX) or p in ids]
    return plot.make_multiax(chosen, ordered, depth_range, cast)


@app.callback(Output("ts", "figure"),
              Input("multiax_casts", "value"), Input("ts_colour", "value"),
              Input("multiax_depth", "value"), Input("upload_view", "data"))
def update_ts(chosen, colour, depth, cast):
    depth_range = sorted(abs(d) for d in depth)
    ids = {c["id"] for c in (cast or [])}
    chosen = [p for p in (chosen or []) if not p.startswith(plot.UPLOAD_PREFIX) or p in ids]
    return plot.make_ts(chosen, colour, depth_range, cast)


@app.callback(Output("index", "figure"),
              Input("index_variable", "value"), Input("index_layer", "value"))
def update_index(variable, layer):
    return plot.make_index(variable, layer)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
