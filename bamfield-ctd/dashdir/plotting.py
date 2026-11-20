"""Figures for the CTD archive dashboard. Called by app.py; every function returns a fresh figure."""
from pathlib import Path

import gsw
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import cmocean, sample_colorscale
from plotly.subplots import make_subplots

DATA = Path(__file__).resolve().parent / "data"

sites = pd.read_csv(DATA / "sites.csv", index_col="site_id")
casts = pd.read_csv(DATA / "casts.csv")
profiles = pd.read_csv(DATA / "profiles.csv.gz")
envelopes = pd.read_csv(DATA / "envelopes.csv.gz")
anomalies = pd.read_csv(DATA / "anomalies.csv")

YEARS = sorted(casts["year"].unique())
PROFILE_GROUPS = {p: g for p, g in profiles.groupby("profile")}
CASTS_BY_SITE = {s: g.sort_values("time") for s, g in casts.groupby("site_id")}
MAP_CENTER = {"lat": 48.865, "lon": -125.135}

LABELS = {
    "CT": "Conservative Temperature (°C)",
    "SA": "Absolute Salinity (g kg⁻¹)",
    "sigma0": "σ₀ (kg m⁻³)",
    "DO": "Oxygen (µmol L⁻¹)",
    "Fluorescence": "Fluorescence (relative index)",
    "PAR": "PAR (instrument units)",
}
# Axis titles as in the EOSC 372 class dashboard: bold quantity, units on the line below.
AXIS_TITLES = {
    "CT": "<b>Conservative Temperature</b><br>(°C)",
    "SA": "<b>Absolute Salinity</b><br>(g kg⁻¹)",
    "sigma0": "<b>σ₀</b><br>(kg m⁻³)",
    "DO": "<b>Oxygen</b><br>(µmol L⁻¹)",
    "Fluorescence": "<b>Fluorescence</b><br>(relative index)",
    "PAR": "<b>PAR</b><br>(instrument units)",
}
TEMPLATE = "simple_white"      # the class dashboard's template
SHORT = {"CT": "Conservative Temperature", "SA": "Absolute Salinity", "sigma0": "σ₀", "DO": "Oxygen",
         "Fluorescence": "Fluorescence", "PAR": "PAR"}
# Clicked-station colours from the class dashboard (ocgy-dataviewer station.py), extended.
SITE_COLOURS = ["darkviolet", "limegreen", "darkorange", "deeppink", "darkred", "darkgreen",
                "royalblue", "goldenrod", "teal", "saddlebrown"]
GRID_MIN_YEARS = 5   # the occupancy grid shows sites with at least this many years


def year_colour(year: int) -> str:
    frac = (year - YEARS[0]) / (YEARS[-1] - YEARS[0])
    return sample_colorscale("Viridis", [frac])[0]


def site_name(site_id: int) -> str:
    return sites.loc[site_id, "name"]


# ---- uploaded casts ----------------------------------------------------------------------
# Uploads are a list of casts held in the viewer's browser and passed into each figure. Each has
# an id starting with UPLOAD_PREFIX, which stands in for a profile id in the cast lists.
UPLOAD_PREFIX = "__upload__"
# Warm colours, distinct from the viridis years and the site colours, one per uploaded cast.
UPLOAD_COLOURS = ["red", "darkorange", "magenta", "saddlebrown", "deeppink", "chocolate"]


def upload_label(cast: dict) -> str:
    return f"Your cast: {cast['name']}" + (f" ({cast['date']})" if cast.get("date") else "")


def _upload_by_id(profile: str, uploads):
    return next((c for c in (uploads or []) if c["id"] == profile), None)


def upload_colour(cast: dict, uploads=None) -> str:
    """Colour from the cast's own number, so it keeps its colour when others are hidden."""
    k = int(cast["id"][len(UPLOAD_PREFIX):])
    return UPLOAD_COLOURS[k % len(UPLOAD_COLOURS)]


def _group(profile: str, uploads):
    if profile.startswith(UPLOAD_PREFIX):
        cast = _upload_by_id(profile, uploads)
        return pd.DataFrame(cast["data"]).astype(float) if cast else None
    return PROFILE_GROUPS.get(profile)


def _label(profile: str, uploads) -> str:
    cast = _upload_by_id(profile, uploads) if profile.startswith(UPLOAD_PREFIX) else None
    return upload_label(cast) if cast else cast_label(profile)


def uploads_at(uploads, site_ids) -> list[dict]:
    """The uploaded casts whose nearest site is one of site_ids (all of them if none chosen)."""
    if not site_ids:
        return list(uploads or [])
    return [c for c in (uploads or []) if c["site_id"] in site_ids]


def _upload_traces(fig, cast, uploads, variables):
    g = _group(cast["id"], uploads)
    colour = upload_colour(cast, uploads)
    first = True
    for i, v in enumerate(variables, start=1):
        sub = g[["z", v]].dropna()
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub[v], y=sub["z"], mode="lines", line={"color": colour, "width": 3},
            name=upload_label(cast), legendgroup=cast["id"], showlegend=first,
            hovertemplate=f"{upload_label(cast)}<br>%{{x}} at %{{y:.1f}} m<extra></extra>"),
            row=1, col=i)
        first = False


# ---- map --------------------------------------------------------------------------------

def make_map(mode: str, year: int | None, selected: list[int], uploads=None,
             only_mine: bool = False) -> go.Figure:
    fig = go.Figure()
    if only_mine and uploads:
        _upload_markers(fig, uploads)
        return _finish_map(fig)
    if mode == "year" and year is not None:
        visited = set(casts.loc[casts["year"] == year, "site_id"])
    else:
        visited = set(sites.index)
    shown = sites.loc[sorted(visited)]
    others = sites.loc[sorted(set(sites.index) - visited)]

    if len(others):
        fig.add_trace(go.Scattermap(
            lat=others["latitude"], lon=others["longitude"], mode="markers",
            marker={"size": 6, "color": "lightgrey"}, hoverinfo="skip", showlegend=False))

    if mode == "year" and year is not None:
        n_that_year = casts[casts["year"] == year].groupby("site_id").size()
        text = [f"<b>{site_name(s)}</b><br>{n_that_year[s]} cast(s) in {year}"
                for s in shown.index]
        marker = {"size": 11, "color": "#444"}
    else:
        text = [f"<b>{r.name_}</b><br>{r.n_casts} casts in {r.n_years} years<br>{r.years}"
                + (f"<br><i>logged as: {r.labels}</i>" if isinstance(r.labels, str) and r.labels else "")
                for r in shown.rename(columns={"name": "name_"}).itertuples()]
        marker = {"size": 6 + 1.2 * shown["n_years"], "color": shown["n_years"],
                  "colorscale": "Blues", "cmin": 0, "cmax": len(YEARS),
                  "colorbar": {"title": {"text": "Years"}, "thickness": 12, "len": 0.6}}
    fig.add_trace(go.Scattermap(
        lat=shown["latitude"], lon=shown["longitude"], mode="markers", marker=marker,
        customdata=[int(s) for s in shown.index], text=text,
        hovertemplate="%{text}<br>lat: %{lat:.3f}<br>lon: %{lon:.3f}<extra></extra>",
        showlegend=False))

    for k, s in enumerate(selected):
        fig.add_trace(go.Scattermap(
            lat=[sites.loc[s, "latitude"]], lon=[sites.loc[s, "longitude"]], mode="markers",
            marker={"size": 16, "color": SITE_COLOURS[k % len(SITE_COLOURS)]},
            customdata=[int(s)], text=[f"<b>{site_name(s)}</b>"],
            hovertemplate="%{text}<br>lat: %{lat:.3f}<br>lon: %{lon:.3f}<extra></extra>",
            showlegend=False))

    if uploads:
        _upload_markers(fig, uploads)
    return _finish_map(fig)


def _upload_markers(fig, uploads):
    fig.add_trace(go.Scattermap(
        lat=[c["latitude"] for c in uploads], lon=[c["longitude"] for c in uploads],
        mode="markers", hoverinfo="text", showlegend=False,
        marker={"size": 14, "color": [upload_colour(c, uploads) for c in uploads]},
        text=[f"<b>{upload_label(c)}</b><br>{c['latitude']:.4f}, {c['longitude']:.4f}"
              for c in uploads]))


def _finish_map(fig):
    fig.update_layout(map={"style": "open-street-map", "center": MAP_CENTER, "zoom": 11},
                      margin={"l": 0, "r": 0, "t": 0, "b": 0}, height=520,   # OSM credit placed by assets/maplibre_controls.css
                      uirevision="map")
    return fig


# ---- occupancy grid ---------------------------------------------------------------------

def make_grid(selected: list[int]) -> go.Figure:
    keep = sites[sites["n_years"] >= GRID_MIN_YEARS].sort_values("latitude", ascending=False)
    counts = (casts[casts["site_id"].isin(keep.index)]
              .groupby(["site_id", "year"]).size().unstack("year")
              .reindex(index=keep.index, columns=YEARS))
    names = [site_name(s) for s in counts.index]
    fig = go.Figure(go.Heatmap(
        z=counts.to_numpy(dtype=float), x=[str(y) for y in YEARS], y=names,
        colorscale="Blues", zmin=0, zmax=6, xgap=1, ygap=1,   # 6+ saturates; the inlet site has up to 19
        colorbar={"title": {"text": "Casts"}, "thickness": 12,
                  "tickvals": [0, 2, 4, 6], "ticktext": ["0", "2", "4", "6+"]},
        hovertemplate="%{y}<br>%{x}: %{z} cast(s)<extra></extra>"))
    for k, s in enumerate(selected):
        if s in counts.index:
            fig.add_shape(type="rect", xref="paper", x0=0, x1=1, yref="y",
                          y0=names.index(site_name(s)) - 0.5, y1=names.index(site_name(s)) + 0.5,
                          line={"color": SITE_COLOURS[k % len(SITE_COLOURS)], "width": 2})
    fig.update_layout(template=TEMPLATE, height=520, margin={"l": 10, "r": 10, "t": 10, "b": 40},
                      yaxis={"autorange": "reversed", "tickfont": {"size": 10}},
                      xaxis={"title": {"text": "Year"}, "tickangle": -60})
    return fig


# ---- profiles ---------------------------------------------------------------------------

def _empty_profiles(variables, depth_range, message):
    """A blank panel with a prompt; empty subplots would collapse into one squashed axis."""
    fig = go.Figure()
    fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5,
                       showarrow=False, font={"size": 16, "color": "grey"})
    fig.update_layout(template=TEMPLATE, height=500, xaxis={"visible": False},
                      yaxis={"visible": False}, margin={"l": 60, "r": 100, "t": 80, "b": 20})
    return fig


def _finish_profiles(fig, variables, depth_range):
    """Class-dashboard look: simple_white, x axes along the top, three ticks, bold titles.

    A panel whose variable no cast carries (oxygen in 2001-2003, for example) gets an invisible
    placeholder trace, so Plotly still draws its axes and its letter lands on it rather than on
    panel A, and a note saying there are no data.
    """
    for i, v in enumerate(variables, start=1):
        axis = "x" if i == 1 else f"x{i}"
        has_data = any(getattr(t, "xaxis", None) == axis and t.x is not None
                       and any(x is not None for x in t.x) for t in fig.data)
        if not has_data:
            fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", showlegend=False,
                                     hoverinfo="skip"), row=1, col=i)
            fig.add_annotation(text=f"No {SHORT[v].lower() if v != 'sigma0' else SHORT[v]}<br>"
                                    "data in<br>these casts",
                               xref=f"{axis} domain", yref="y domain", x=0.5, y=0.6,
                               showarrow=False, font={"color": "grey"})
            fig.update_xaxes(tickfont={"color": "rgba(0,0,0,0)"}, ticks="", row=1, col=i)   # keep the title level with its neighbours
    for i, v in enumerate(variables, start=1):
        fig.update_xaxes(title_text=AXIS_TITLES[v], side="top", nticks=3, row=1, col=i,
                         type="log" if v == "PAR" else "linear")
        fig.add_annotation(text=f"<b>{chr(64 + i)}</b>", xref=f"x{i if i > 1 else ''} domain",
                           yref="y domain", x=0.03, y=0.01, showarrow=False,
                           xanchor="left", yanchor="bottom")
    fig.update_yaxes(range=[depth_range[1], depth_range[0]], row=1, col=1,
                     title_text="<b>Depth</b> (m)")
    fig.update_layout(template=TEMPLATE, height=500,
                      margin={"l": 60, "b": 20, "r": 100, "t": 80},
                      legend={"font": {"size": 10}}, hovermode="closest")
    return fig


def _cast_traces(fig, profile, variables, colour, name, group, showlegend, width=1.2, dash=None):
    g = PROFILE_GROUPS.get(profile)
    if g is None:
        return
    meta = casts.loc[casts["profile"] == profile].iloc[0]
    text = f"{profile}<br>{meta['date']}  {meta['station']}<br>{meta['model']}"
    if isinstance(meta.get("position_note"), str) and meta["position_note"]:
        text += "<br><i>Position corrected by hand</i>"
    for i, v in enumerate(variables, start=1):
        sub = g[["z", v]].dropna()
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub[v], y=sub["z"], mode="lines", line={"color": colour, "width": width, "dash": dash},
            name=name, legendgroup=group, showlegend=showlegend,
            hovertemplate=f"{text}<br>%{{x}} at %{{y:.0f}} m<extra></extra>"), row=1, col=i)
        showlegend = False


def _envelope_traces(fig, site_id, variables, show_legend):
    env = envelopes[envelopes["site_id"] == site_id]
    for i, v in enumerate(variables, start=1):
        e = env[env["variable"] == v].sort_values("z")
        if e.empty:
            continue
        y = e["z"]
        band = e[e["n_years"] >= 3]          # sd is blank where fewer than 3 years
        if not band.empty:
            fig.add_trace(go.Scatter(
                # mode must be explicit: under 20 points Plotly defaults to lines+markers, which
                # put a coloured dot on every corner of the band at shallow sites.
                x=np.r_[band["mean"] - band["sd"], (band["mean"] + band["sd"])[::-1]],
                y=np.r_[band["z"], band["z"][::-1]], fill="toself", mode="lines",
                fillcolor="rgba(120,120,120,0.22)", line={"width": 0}, hoverinfo="skip",
                name="± 1 sd across years", legendgroup="env", showlegend=show_legend and i == 1),
                row=1, col=i)
        fig.add_trace(go.Scatter(
            x=e["mean"], y=y, mode="lines", line={"color": "black", "width": 2.5},
            name="mean across years", legendgroup="med", showlegend=show_legend and i == 1,
            hovertemplate="mean of %{text} years<br>%{x:.3f} at %{y:.1f} m<extra></extra>",
            text=e["n_years"]), row=1, col=i)


def make_profiles(mode, year, selected, hover_site, variables, depth_range,
                  uploads=None, only_mine: bool = False) -> go.Figure:
    if not variables:
        return _empty_profiles(["TempCT"], depth_range, "Choose at least one variable")
    fig = make_subplots(rows=1, cols=len(variables), shared_yaxes=True,
                        horizontal_spacing=0.03)
    if only_mine and uploads:               # your casts only, all of them, no archive
        for cast in uploads:
            _upload_traces(fig, cast, uploads, variables)
        return _finish_profiles(fig, variables, depth_range)

    if mode == "site":
        if not selected and hover_site is None and not uploads:
            return _empty_profiles(variables, depth_range, "Click a site on the map")
        if selected:
            s = selected[0]
            _envelope_traces(fig, s, variables, show_legend=True)
            site_casts = CASTS_BY_SITE[s]
            seen = set()
            for row in site_casts.itertuples():
                first = row.year not in seen
                seen.add(row.year)
                _cast_traces(fig, row.profile, variables, year_colour(row.year), str(row.year),
                             f"y{row.year}", showlegend=first)
        if hover_site is not None and hover_site not in selected:
            env = envelopes[envelopes["site_id"] == hover_site]
            for i, v in enumerate(variables, start=1):
                e = env[env["variable"] == v].sort_values("z")
                if not e.empty:
                    fig.add_trace(go.Scatter(
                        x=e["mean"], y=e["z"], mode="lines",
                        line={"color": "grey", "width": 2, "dash": "dash"},
                        name=f"hover: {site_name(hover_site)} mean", legendgroup="hov",
                        showlegend=i == 1, hoverinfo="skip"), row=1, col=i)
    else:
        if year is None:
            return _empty_profiles(variables, depth_range, "Choose a year")
        if not selected and hover_site is None and not uploads:
            return _empty_profiles(variables, depth_range,
                                   f"Click sites visited in {year} to compare them")
        for k, s in enumerate(selected):
            these = CASTS_BY_SITE[s]
            these = these[these["year"] == year]
            colour = SITE_COLOURS[k % len(SITE_COLOURS)]
            first = True
            for row in these.itertuples():
                _cast_traces(fig, row.profile, variables, colour, site_name(s), f"s{s}", first)
                first = False
        if hover_site is not None and hover_site not in selected:
            these = CASTS_BY_SITE[hover_site]
            first = True
            for row in these[these["year"] == year].itertuples():
                _cast_traces(fig, row.profile, variables, "grey", f"hover: {site_name(hover_site)}",
                             "hov", first, dash="dash")
                first = False
    # Your casts at the site(s) shown; all of them when no site is chosen.
    for cast in uploads_at(uploads, selected[:1] if mode == "site" else selected):
        _upload_traces(fig, cast, uploads, variables)
    return _finish_profiles(fig, variables, depth_range)


# ---- several variables on one depth axis -------------------------------------------------
# After the multi-variable profile in HB's AML-CTD-Tools (CTD_Data_Extraction.ipynb): colour
# encodes the variable, each variable has its own x axis stacked along the top in that colour,
# and line style encodes the cast.

MULTIAX_COLOURS = {"CT": "#1f77b4", "SA": "#ff7f0e", "sigma0": "#8c564b", "DO": "#2ca02c",
                   "Fluorescence": "#17becf", "PAR": "#bcbd22"}      # matplotlib tab: colours
CAST_DASHES = ["solid", "dash", "dot", "dashdot", "longdash", "longdashdot"]
MAX_MULTIAX_CASTS = len(CAST_DASHES)
MULTIAX_PLOT_PX = 650  # height of the depth axis itself, whatever the number of variables
AXIS_GAP_PX = 65       # room for each extra x axis stacked above it
MULTIAX_MARGIN = {"l": 60, "r": 20, "t": 70, "b": 20}


def cast_label(profile: str) -> str:
    m = casts.loc[casts["profile"] == profile].iloc[0]
    return f"{str(m['time'])[:16]}  {site_name(m['site_id']).split(' (')[0]}  ({m['model']})"


def multiax_cast_options(mode, year, selected) -> list[str]:
    """Casts offered for the multi-axis plot: the selected sites, that year in the year view."""
    out = []
    for s in selected:
        these = CASTS_BY_SITE[s]
        if mode == "year" and year is not None:
            these = these[these["year"] == year]
        out += list(these["profile"])
    return out


def make_multiax(profiles_chosen, variables, depth_range, uploads=None) -> go.Figure:
    if not variables or not profiles_chosen:
        return _empty_profiles(variables, depth_range,
                               "Choose at least one variable" if not variables
                               else "Click a site on the map, then choose casts")
    profiles_chosen = profiles_chosen[:MAX_MULTIAX_CASTS]
    n = len(variables)
    # Fixed pixel sizes, so the depth axis keeps its height (and lines up with the slider) as
    # axes are added; the figure grows instead.
    height = (MULTIAX_PLOT_PX + AXIS_GAP_PX * (n - 1)
              + MULTIAX_MARGIN["t"] + MULTIAX_MARGIN["b"])
    gap = AXIS_GAP_PX / (height - MULTIAX_MARGIN["t"] - MULTIAX_MARGIN["b"])
    top = 1.0 - gap * (n - 1)
    fig = go.Figure()
    layout = {}
    for i, v in enumerate(variables):
        key = "xaxis" if i == 0 else f"xaxis{i + 1}"
        colour = MULTIAX_COLOURS[v]
        axis = {"title": {"text": f"<b>{LABELS[v]}</b>", "font": {"color": colour}},
                "side": "top", "color": colour, "linecolor": colour, "showline": True,
                "nticks": 4, "type": "log" if v == "PAR" else "linear", "showgrid": False,
                "zeroline": False, "ticks": "outside"}
        if i == 0:
            axis["anchor"] = "y"
        else:
            axis.update(overlaying="x", anchor="free", position=top + gap * i)
        layout[key] = axis
        for k, prof in enumerate(profiles_chosen):
            g = _group(prof, uploads)
            if g is None:
                continue
            sub = g[["z", v]].dropna()
            if sub.empty:
                continue
            fig.add_trace(go.Scatter(
                x=sub[v], y=sub["z"], mode="lines", xaxis="x" if i == 0 else f"x{i + 1}",
                line={"color": colour, "dash": CAST_DASHES[k],
                      "width": 3 if prof.startswith(UPLOAD_PREFIX) else 2}, showlegend=False,
                hovertemplate=f"{_label(prof, uploads)}<br>{SHORT[v]}: %{{x:.3f}} at %{{y:.0f}} m"
                              "<extra></extra>"))
    # Legend: one grey entry per cast showing its line style, as in the notebook.
    for k, prof in enumerate(profiles_chosen):
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=_label(prof, uploads),
                                 line={"color": "#555", "dash": CAST_DASHES[k]}))
    fig.update_layout(
        template=TEMPLATE, height=height, hovermode="closest", margin=MULTIAX_MARGIN,
        yaxis={"domain": [0, top], "range": [depth_range[1], depth_range[0]],
               "title": {"text": "<b>Depth</b> (m)"}},
        legend={"orientation": "v", "x": 1.02, "y": top / 2, "yanchor": "middle",
                "title": {"text": "Cast (line style)"}, "font": {"size": 11}},
        **layout)
    return fig


# ---- T-S diagram ------------------------------------------------------------------------
# After the T-S cell in HB's AML-CTD-Tools (CTD_Data_Extraction.ipynb): every bin as Conservative
# Temperature against Absolute Salinity, dashed labelled sigma0 isopycnals from gsw on a grid
# padded around the data, points coloured by a chosen variable on one shared scale, and a
# different marker for each cast (the notebook's o, s, ^, D, v, P).

TS_PLOT_PX = 540        # the plotting area is square: SA and CT axes the same length
TS_MARGIN = {"l": 80, "r": 440, "t": 20, "b": 70}  # r: colour bar, then the cast legend
TS_LEGEND_X = 1 + 120 / TS_PLOT_PX                  # legend starts 120 px right of the plot
TS_MARKERS = ["circle", "square", "triangle-up", "diamond", "triangle-down", "cross"]
TS_COLOUR_OPTIONS = {   # key: (label, colour scale); cmocean where the notebook used it
    "DO": (LABELS["DO"], "Viridis"),
    "depth": ("Depth (m)", cmocean.deep),
    "sigma0": (LABELS["sigma0"], cmocean.dense),
    "Fluorescence": (LABELS["Fluorescence"], cmocean.algae),
    "PAR": (LABELS["PAR"], cmocean.solar),
}


def _nice_step(span: float) -> float:
    """An isopycnal interval giving roughly six to ten lines across the plotted range."""
    for step in (0.1, 0.2, 0.25, 0.5, 1.0, 2.0):
        if span / step <= 10:
            return step
    return 5.0


def make_ts(profiles_chosen, colour_var, depth_range, uploads=None) -> go.Figure:
    if not profiles_chosen:
        fig = _empty_profiles([], depth_range, "Click a site on the map, then choose casts above")
        fig.update_layout(height=300)
        return fig
    profiles_chosen = profiles_chosen[:MAX_MULTIAX_CASTS]
    frames = []
    for k, prof in enumerate(profiles_chosen):
        g = _group(prof, uploads)
        if g is None:
            continue
        g = g[(g["z"] >= depth_range[0]) & (g["z"] <= depth_range[1])]
        g = g.dropna(subset=["SA", "CT"]).assign(k=k, depth=g["z"])
        frames.append(g)
    data = pd.concat(frames) if frames else pd.DataFrame()
    if data.empty:
        fig = _empty_profiles([], depth_range, "No temperature and salinity in this depth range")
        fig.update_layout(height=300)
        return fig

    # Isopycnal grid, padded around the data as in the notebook.
    sa0, sa1 = data["SA"].min(), data["SA"].max()
    ct0, ct1 = data["CT"].min(), data["CT"].max()
    pad_sa, pad_ct = max(0.1, 0.05 * (sa1 - sa0)), max(0.1, 0.05 * (ct1 - ct0))
    si = np.linspace(sa0 - pad_sa, sa1 + pad_sa, 120)
    ti = np.linspace(ct0 - pad_ct, ct1 + pad_ct, 120)
    dens = gsw.sigma0(*np.meshgrid(si, ti))
    step = _nice_step(float(np.nanmax(dens) - np.nanmin(dens)))
    fig = go.Figure(go.Contour(
        x=si, y=ti, z=dens, showscale=False, hoverinfo="skip", name="σ₀",
        contours={"coloring": "lines", "showlabels": True, "start": np.ceil(np.nanmin(dens) / step) * step,
                  "end": np.nanmax(dens), "size": step,
                  "labelfont": {"size": 11, "color": "black"}},
        colorscale=[[0, "black"], [1, "black"]], line={"dash": "dash", "width": 1}))

    label, scale = TS_COLOUR_OPTIONS[colour_var]
    cvals = data[colour_var] if colour_var != "depth" else data["depth"]
    cmin, cmax = float(np.nanmin(cvals)) if cvals.notna().any() else 0, \
        float(np.nanmax(cvals)) if cvals.notna().any() else 1
    for k, prof in enumerate(profiles_chosen):
        d = data[data["k"] == k]
        if d.empty:
            continue
        c = d[colour_var] if colour_var != "depth" else d["depth"]
        fig.add_trace(go.Scatter(
            x=d["SA"], y=d["CT"], mode="markers", name=_label(prof, uploads), showlegend=False,
            marker={"symbol": TS_MARKERS[k], "size": 7, "color": c, "colorscale": scale,
                    "cmin": cmin, "cmax": cmax, "showscale": k == 0,
                    "line": {"width": 0.3, "color": "#333"},
                    "colorbar": {"title": {"text": label, "side": "right"}, "thickness": 14,
                                 "x": 1.03, "len": 0.8}},
            customdata=np.c_[d["depth"], c],
            hovertemplate=(f"{_label(prof, uploads)}<br>SA %{{x:.3f}}, CT %{{y:.3f}}"
                           "<br>%{customdata[0]:.0f} m"
                           + ("" if colour_var == "depth"
                              else f"<br>{SHORT[colour_var]}: %{{customdata[1]:.3f}}")
                           + "<extra></extra>")))
    # Legend: one grey marker per cast, since the points' colour is the variable, not the cast.
    for k, prof in enumerate(profiles_chosen):
        if (data["k"] == k).any():
            fig.add_trace(go.Scatter(
                x=[None], y=[None], mode="markers", name=_label(prof, uploads),
                marker={"symbol": TS_MARKERS[k], "size": 9, "color": "#888",
                        "line": {"width": 0.5, "color": "#333"}}))
    margin = TS_MARGIN
    fig.update_layout(
        template=TEMPLATE, hovermode="closest", autosize=False, margin=margin,
        width=TS_PLOT_PX + margin["l"] + margin["r"],
        height=TS_PLOT_PX + margin["t"] + margin["b"],
        xaxis={"title": {"text": AXIS_TITLES["SA"]}, "range": [si[0], si[-1]]},
        yaxis={"title": {"text": AXIS_TITLES["CT"]}, "range": [ti[0], ti[-1]]},
        legend={"orientation": "v", "x": TS_LEGEND_X, "xanchor": "left", "y": 0.5,
                "yanchor": "middle", "itemsizing": "constant",
                "title": {"text": "Cast (marker)"}, "font": {"size": 11}})
    return fig


# ---- year index -------------------------------------------------------------------------

def make_index(variable: str, layer: str) -> go.Figure:
    a = anomalies[(anomalies["variable"] == variable) & (anomalies["layer"] == layer)]
    fig = go.Figure()
    if a.empty:
        fig.add_annotation(text="No sites carry this layer in enough years", showarrow=False,
                           xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    fig.add_trace(go.Scatter(
        x=a["year"], y=a["naive"], mode="markers", name="naive median of all casts",
        marker={"symbol": "circle-open", "color": "grey", "size": 9},
        customdata=a["naive_n_casts"],
        hovertemplate="%{x}: %{y:.2f}<br>%{customdata} casts, any site<extra>naive</extra>"))
    fig.add_trace(go.Scatter(
        x=a["year"], y=a["adjusted"], mode="lines+markers", name="site-adjusted year level",
        line={"color": "darkviolet"}, marker={"line": {"color": "black", "width": 0.3}},
        connectgaps=False, customdata=a["n_sites"],
        hovertemplate="%{x}: %{y:.2f}<br>from %{customdata} site(s)<extra>adjusted</extra>"))
    n_index = int(a["n_index_sites"].iloc[0])
    fig.update_layout(
        template=TEMPLATE, height=380, margin={"l": 70, "r": 10, "t": 30, "b": 50},
        xaxis={"title": {"text": "<b>Year</b>"}, "dtick": 2},
        yaxis={"title": {"text": f"{AXIS_TITLES[variable]}<br>{layer} mean"}},
        legend={"orientation": "h", "y": 1.12, "x": 0},
        annotations=[{"text": f"{n_index} site(s) with ≥5 years enter the adjusted level",
                      "xref": "paper", "yref": "paper", "x": 1, "y": 1.1,
                      "showarrow": False, "xanchor": "right", "font": {"size": 11, "color": "grey"}}])
    return fig
