"""Upload-and-compare: read a user's binned casts from the dashboard's CSV template.

One row per depth bin. A row with something in the `cast` column starts a new cast; rows below
it with that cell blank belong to the same cast. The label can be just the station or location
("Sarita Hole", "TC1"); two casts may share a label, since each filled cell starts a new one.
Each cast gives its position, and optionally its date, on its first row. Column names are not
case-sensitive:

    cast                  label for the cast, e.g. a station name (first row of each cast)
    latitude, longitude   decimal degrees, west negative (required, first row of each cast)
    date                  YYYY-MM-DD (optional)
    depth_m               bin depth in metres (required)
    temperature_c         in-situ temperature, ITS-90 (required)
    practical_salinity    Practical Salinity (PSS-78), as the CTD reports it, not Absolute
                          Salinity (required; a column named `salinity` is read the same way)
    oxygen_umol_l         dissolved oxygen in umol/L; from ml/L multiply by 44.66 (optional)
    fluorescence, par     optional, any units

A file without a `cast` column is read as a single cast named after the file.

The profiles are taken as given: the uploader is trusted to supply binned downcasts (HB, 20 Nov
2026). The only processing is sorting by depth and the TEOS-10 conversion the comparison needs
(SA and CT at the cast's position, then sigma0), as for the archive's casts. Everything happens
in memory; the result lives in the viewer's browser (dcc.Store), never on the server.
"""
import base64
import io

import gsw
import numpy as np
import pandas as pd

from shared import SURFACE_CUT_M, km_between

MAX_BYTES = 2_000_000            # a binned cast is a few kB
MAX_CASTS = 30
LAT_LIM, LON_LIM = (48.0, 50.0), (-127.0, -123.0)   # generous: anywhere near Barkley Sound
UPLOAD_PREFIX = "__upload__"     # profile ids of uploaded casts: __upload__0, __upload__1, ...

COLUMNS = {   # template column -> name used inside the dashboard
    "depth_m": "z", "temperature_c": "TempCT", "practical_salinity": "Salinity",
    "oxygen_umol_l": "DO", "fluorescence": "Fluorescence", "par": "PAR",
}
REQUIRED = ["latitude", "longitude", "depth_m", "temperature_c", "practical_salinity"]
# Older column names still accepted (the template said `salinity` until 20 Nov 2026).
ALIASES = {"salinity": "practical_salinity"}
TEMPLATE_COLUMNS = ["cast", "latitude", "longitude", "date", *COLUMNS]


def template_csv() -> str:
    """The template, with two short example casts to show the layout."""
    # Starts at 1.5 m: rows at 1 m and shallower are dropped (SURFACE_CUT_M).
    rows = [["Sarita Hole", 48.8975, -125.0501, "2027-02-18", 1.5, 8.61, 30.12, 281.0, "", ""],
            ["", "", "", "", 2.0, 8.60, 30.15, 280.4, "", ""],
            ["", "", "", "", 2.5, 8.58, 30.31, 279.9, "", ""],
            ["Aguilar Point", 48.8403, -125.1407, "2027-02-19", 1.5, 8.20, 29.80, 290.2, "", ""],
            ["", "", "", "", 2.0, 8.22, 29.95, 289.7, "", ""]]
    return pd.DataFrame(rows, columns=TEMPLATE_COLUMNS).to_csv(index=False)


def _one_cast(rows: pd.DataFrame, label: str) -> dict:
    lat = pd.to_numeric(rows["latitude"], errors="coerce").iloc[0]
    lon = pd.to_numeric(rows["longitude"], errors="coerce").iloc[0]
    if not (np.isfinite(lat) and np.isfinite(lon)):
        raise ValueError(f"{label}: put its latitude and longitude on its first row.")
    if lon > 0:
        raise ValueError(f"{label}: longitude must be negative (degrees west), e.g. -125.05.")
    if not (LAT_LIM[0] <= lat <= LAT_LIM[1] and LON_LIM[0] <= lon <= LON_LIM[1]):
        raise ValueError(f"{label}: the position {lat:.4f}, {lon:.4f} is not near Barkley "
                         "Sound; check it is in decimal degrees.")
    date = ""
    if "date" in rows and pd.notna(rows["date"].iloc[0]):
        date = str(rows["date"].iloc[0]).strip()

    data = pd.DataFrame({new: pd.to_numeric(rows[old], errors="coerce") if old in rows else np.nan
                         for old, new in COLUMNS.items()})
    data = data.dropna(subset=["z"]).sort_values("z")
    data = data[data["z"] > SURFACE_CUT_M]      # as for the archive: the surface soak
    if data.empty:
        raise ValueError(f"{label}: no rows deeper than {SURFACE_CUT_M:g} m.")
    if data[["TempCT", "Salinity"]].dropna().empty:
        raise ValueError(f"{label}: no rows have both temperature and salinity.")
    p = gsw.p_from_z(-data["z"], lat)
    data["SA"] = gsw.SA_from_SP(data["Salinity"], p, lon, lat)
    data["CT"] = gsw.CT_from_t(data["SA"], data["TempCT"], p)
    data["sigma0"] = gsw.sigma0(data["SA"], data["CT"])
    out = data[["z", "CT", "SA", "sigma0", "DO", "Fluorescence", "PAR"]].round(4)
    out = out.astype(object).where(out.notna(), None)            # NaN is not valid JSON
    return {"name": label, "date": date, "latitude": float(lat), "longitude": float(lon),
            "max_depth": float(data["z"].max()), "n": len(data), "data": out.to_dict("list")}


def read_upload(contents: str, filename: str) -> list[dict]:
    """Parse a dcc.Upload payload into a JSON-able list of casts for dcc.Store.

    Each cast carries an ``id`` (UPLOAD_PREFIX + index). Raises ValueError with a message meant
    for the person uploading.
    """
    if not filename.lower().endswith(".csv"):
        raise ValueError("Please upload the CSV template (a .csv file).")
    raw = base64.b64decode(contents.split(",", 1)[1])
    if len(raw) > MAX_BYTES:
        raise ValueError(f"The file is larger than {MAX_BYTES // 1_000_000} MB; "
                         "binned casts should be far smaller.")
    try:
        df = pd.read_csv(io.StringIO(raw.decode("utf-8-sig", errors="replace")), dtype=str)
    except Exception as err:                                     # noqa: BLE001
        raise ValueError(f"Could not read the file as CSV ({err}).") from None
    df.columns = [str(c).strip().lower() for c in df.columns]
    df = df.rename(columns={old: new for old, new in ALIASES.items() if new not in df})
    missing = [c for c in REQUIRED if c not in df]
    if missing:
        raise ValueError("Missing column(s): " + ", ".join(missing)
                         + ". Download the template to see the layout.")
    df = df.dropna(how="all")
    if df.empty:
        raise ValueError("The file has no rows.")

    if "cast" in df:
        starts = df["cast"].fillna("").str.strip() != ""
        if not starts.iloc[0]:
            raise ValueError("The first row needs a cast label (the station name will do).")
        block = starts.cumsum()
    else:
        block = pd.Series(1, index=df.index)
    groups = list(df.groupby(block, sort=True))
    if len(groups) > MAX_CASTS:
        raise ValueError(f"{len(groups)} casts in one file; the limit is {MAX_CASTS}.")

    casts, seen = [], {}
    for k, (_, rows) in enumerate(groups):
        label = (str(rows["cast"].iloc[0]).strip() if "cast" in rows
                 else filename.rsplit(".", 1)[0])
        cast = _one_cast(rows, label)
        # Repeat casts at one station: the date tells them apart; number them if it does not.
        key = (label, cast["date"])
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 1:
            cast["name"] = f"{label} ({seen[key]})"
        cast["id"] = f"{UPLOAD_PREFIX}{k}"
        casts.append(cast)
    return casts


def nearest_site(cast: dict, sites: pd.DataFrame) -> tuple[int, float]:
    """(site_id, distance in km) of the site nearest an uploaded cast."""
    d = np.asarray(km_between(cast["latitude"], cast["longitude"],
                              sites["latitude"], sites["longitude"]))
    i = int(np.argmin(d))
    return int(sites.index[i]), float(d[i])
