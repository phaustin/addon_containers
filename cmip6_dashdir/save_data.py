import xarray as xr
import pooch
import pandas as pd
import fsspec
from pathlib import Path
import json
import dask
import time
import numpy as np

dask.config.set({"array.slicing.split_large_chunks": True})

# get esm datastore
odie = pooch.create(
    path="./.cache",  # create a cache to save the pangeo csv
    base_url="https://storage.googleapis.com/cmip6/",
    # The registry specifies the files that can be fetched
    registry={
        "pangeo-cmip6.csv": "3431e658603318a603e78d16be5e3fa636fc6817562d06ddbf67a976925afb9c",
    },
)

file_path = odie.fetch("pangeo-cmip6.csv")
df_og = pd.read_csv(file_path)  # the pangeo dataframe

# this line is only necessary if caching the data. The data will cache under .cache/files
fs = fsspec.filesystem(
    "filecache",
    target_protocol="gs",
    target_options={"anon": True},
    cache_storage="./.cache/files/",
)


def get_pressure_field(mod_id, ds):
    if (
        (mod_id == "CESM2")
        | (mod_id == "GISS-E2-1-H")
        | (mod_id == "MRI-ESM2-0")
        | (mod_id == "BCC-ESM1")
    ):
        ds["p"] = ds.a * ds.p0 + ds.b * ds.ps
        ds = ds.drop_vars(["a", "p0", "b", "ps"])
    elif mod_id == "UKESM1-0-LL":
        # the pressure field for this model has units of meters. I used the formula below to convert to Pa
        # barometric formula: https://link.springer.com/article/10.1007/s40828-020-0111-6
        p0 = 101325  # Pa
        rho0 = 1.225
        g = 9.81
        h = ds.lev + ds.b * ds.orog
        p = p0 * np.exp(-(rho0 * g * h) / p0)
        ds["p"] = p.expand_dims({"time": ds.time}, axis=0)
        ds = ds.drop_vars(["b", "orog"])
    elif mod_id == "CanESM5":
        ds["p"] = ds.ap + ds.b * ds.ps
        ds = ds.drop_vars(["ap", "b", "ps"])
    return ds


def save_model(var_id, mod_id, exp_id):
    # the experiments with the sftlf variable don't line up with the cl variable. sftlf is a fixed variable
    # so I just chose an experiment that has sftlf for all the models.
    lp_exp_id = "piControl"

    # the path where we will save the data
    model_path = Path("models/" + var_id + "/" + mod_id + "_" + exp_id + ".zarr")

    # get the data for the sftlf variable: percentage of the grid cell occupied by land
    query = (
        "variable_id=='"
        + lp_var_id
        + "' & experiment_id=='"
        + lp_exp_id
        + "' & source_id=='"
        + mod_id
        + "' & table_id=='"
        + lp_monthly_table
        + "'"
    )
    lp_df = df_og.query(query)
    zstore_url = lp_df["zstore"].values[0]
    the_mapper = fs.get_mapper(zstore_url)
    # to not use caching, replace the above line with:
    # the_mapper=fsspec.get_mapper(zstore_url)
    lp_ds = xr.open_zarr(the_mapper, consolidated=True)

    # get the data for the cl variable: percentage cloud cover
    query = (
        "variable_id=='"
        + var_id
        + "' & experiment_id=='"
        + exp_id
        + "' & source_id=='"
        + mod_id
        + "' & table_id=='"
        + monthly_table
        + "'"
    )
    cloud_df = df_og.query(query)
    zstore_url = cloud_df["zstore"].values[0]
    the_mapper = fs.get_mapper(zstore_url)
    # to not use caching, replace the above line with:
    # the_mapper=fsspec.get_mapper(zstore_url)
    ds = xr.open_zarr(the_mapper, consolidated=True)
    lp_ds = lp_ds.reindex_like(ds, method="nearest")

    if len(ds.time) > 3000:
        ds = ds.isel(time=slice(0, 3000))  # 250 years max

    ds = ds.where(lp_ds.sftlf == 0.0)  # only values over water
    ds = ds.sel(lat=slice(21, 47), lon=slice(200, 243))  # choose specific lats, lons

    ds = get_pressure_field(mod_id, ds)
    ds = ds.where(ds.p < 700000, drop=False)  # values where the pressure is <700hPa

    ds.to_zarr(model_path, mode="w")


# sea area percentage parameters:
lp_var_id = (
    "sftlf"  # Percentage of the grid cell occupied by land (including lakes) [%]
)
lp_monthly_table = "fx"  # fixed variables

# model parameters:
var_id = "cl"  # percentage cloud cover
monthly_table = "Amon"  # monthly atmospheric data

# read in the model csv to loop over all the models to save them.
models_df = pd.read_csv("models.csv")

query = "variable_id=='" + var_id + "'"
models = models_df.query(query).drop_duplicates(["source_id"])["source_id"]

model_list = ["CESM2", "UKESM1-0-LL", "CanESM5"]

# This loops over all the models in the dict and saves them. Usually there is not enough space to download all of the models if the data
# is being cached. If it runs out of space, you can delete the file folder under .cache.

for mod_id in models:
    if mod_id in model_list:
        query = "variable_id=='" + var_id + "' & source_id=='" + mod_id + "'"
        exp_id_list = models_df.query(query)["experiment_id"].values

        for i in range(len(exp_id_list)):
            t0 = time.time()
            print("model: " + mod_id + " exp: " + exp_id_list[i])
            save_model(var_id, mod_id, exp_id_list[i])
            t1 = time.time()
            print("model time: " + str(t1 - t0))
