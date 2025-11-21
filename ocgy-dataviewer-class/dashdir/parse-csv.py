# This file is called separately from the rest of the program. This file takes the original data and creates cleaner csvs for app.py to use

import gsw
import numpy as np
import pandas as pd

# all of the parameters from the full data: 'Cruise' 'Station'	'yyyy-mm-ddThh:mm:ss.sss'	'Longitude [degrees_east]'	'Latitude [degrees_north]'	'CTDPRS_T_VALUE_SENSOR [dbar]'	'DEPTH [m]'	'CTDTMP_T_VALUE_SENSOR [deg C]'	'CTDSAL_D_CONC_SENSOR [pss-78]'	'PHOSPHATE_D_CONC_BOTTLE [umol/kg]'	'NITRATE_D_CONC_BOTTLE [umol/kg]'	'Fe_D_CONC_BOTTLE [nmol/kg]'

# averages data with the exact same depth.
def average_data(cruise_data):
    # from https://stackoverflow.com/questions/48830324/pandas-average-columns-with-same-value-in-other-columns
    cruise_data["Depth"] = (cruise_data["Depth"]/5).round() * 5
    cruise_data = cruise_data.groupby(
        ["Latitude", "Longitude", "Station", "Depth"], as_index=False
    ).mean()
    return cruise_data


# removes stations with specifically empty iron data.
def remove_empty_data(cruise_data):
    grouped_data = cruise_data.groupby(["Latitude", "Longitude", "Station", "Date"])
    for name, group in grouped_data:
        if group["Iron"].isna().values.all():
            cruise_data = cruise_data.drop(grouped_data.get_group(name).index)
    return cruise_data

# gets the average nitrate and phosphate values that are used to get NSTAR data.
def get_nitrate_and_phosphate(cruise_data, index, row):
    current_depth = row["Depth"]
    min = None
    max = None
    if row["Depth"] <= 100:  # for under 100m, we average nitrates between +/- 5m
        min, max = current_depth - 5, current_depth + 5
    elif row["Depth"] > 100:  # for over 100m, we average nitrates between +/- 10m
        min, max = current_depth - 10, current_depth + 10

    lon = row["Longitude"]
    lat = row["Latitude"]
    avg_nitrate = cruise_data["Nitrate"][
        (
            (cruise_data.Depth <= max)
            & (cruise_data.Depth >= min)
            & (cruise_data.Longitude == lon)
            & (cruise_data.Latitude == lat)
        )
    ].mean()

    avg_phosphate = cruise_data["Phosphate"][
        (
            (cruise_data.Depth <= max)
            & (cruise_data.Depth >= min)
            & (cruise_data.Longitude == lon)
            & (cruise_data.Latitude == lat)
        )
    ].mean()

    return avg_nitrate, avg_phosphate

# create the ratio data
def add_ratio_data(cruise_data):
    averaged_nitrate = []

    # get averaged nitrate data at each point
    for index, row in cruise_data.iterrows():
        nitrate = get_nitrate_and_phosphate(cruise_data, index, row)
        averaged_nitrate.append(nitrate[0])

    ratio = (
        np.array(averaged_nitrate) / cruise_data["Iron"]
    )  # calculate ratio by dividing averaged nitrate by iron
    cruise_data[
        "Averaged Nitrate"
    ] = averaged_nitrate  # add a column of averaged nitrate
    cruise_data["Ratio"] = ratio  # add the ratio column


# create the NSTAR data
def add_NSTAR_data(cruise_data):
    # averaged_nitrate = []
    # averaged_phosphate = []

    # # get averaged nitrate data at each point
    # for index, row in cruise_data.iterrows():
    #     nitrate, phosphate = cruise_data.Nitrate, cruise_data.Phosphate

    # NSTAR = (
    #     np.array(nitrate) - np.array(phosphate) + 2.90
    # )  # calculate N* (N-16P+2.9)
    # cruise_data["NSTAR"] = NSTAR  # add the NSTAR column
    cruise_data["NSTAR"] = cruise_data["Nitrate"] - (cruise_data["Phosphate"]*16) + 2.90

# add the column of density data
def add_density_data(cruise_data):
    # Uses the gsw library: http://www.teos-10.org/pubs/gsw/html/gsw_sigma0.html
    practical_salinity = cruise_data["Salinity"]
    pressure = cruise_data["Pressure"]
    longitude = cruise_data["Longitude"]
    latitude = cruise_data["Latitude"]
    absolute_salinity = gsw.SA_from_SP(
        practical_salinity, pressure, longitude, latitude
    )
    temperature = cruise_data["Temperature"]
    sigma0 = gsw.sigma0(absolute_salinity, temperature)

    cruise_data["Density"] = sigma0

combined_df = pd.read_csv("./data/filtered_data_.csv",low_memory=False)

# read in original data
GA03_data = combined_df[combined_df['Cruise'] == 'GA03']
GIPY05_data = combined_df[combined_df['Cruise'] == 'GIPY05']
GP02_data = combined_df[combined_df['Cruise'] == 'GP02']
GIPY04_data = combined_df[combined_df['Cruise'] == 'GIPY04']

maxdepth=2500

# the headers for our clean data
headers = [
    "Station",
    "Date",
    "Latitude",
    "Longitude",
    "Depth",
    "Temperature",
    "Salinity",
    "Nitrate",
    "Phosphate",
    "Oxygen",
    "Iron",
    "Pressure",
]

# make combined dataframe and csv
data = [
    GA03_data["Station"],
    GA03_data["yyyy-mm-ddThh:mm:ss.sss"],
    GA03_data["Latitude [degrees_north]"],
    GA03_data["Longitude [degrees_east]"],
    GA03_data["DEPTH [m]"],
    GA03_data["CTDTMP_T_VALUE_SENSOR [deg C]"],
    GA03_data["CTDSAL_D_CONC_SENSOR [pss-78]"],
    GA03_data["NITRATE_D_CONC_BOTTLE [umol/kg]"],
    GA03_data["PHOSPHATE_D_CONC_BOTTLE [umol/kg]"],
    GA03_data["CTDOXY_D_CONC_SENSOR [umol/kg]"],
    GA03_data["Fe_D_CONC_BOTTLE [nmol/kg]"],
    GA03_data["CTDPRS_T_VALUE_SENSOR [dbar]"],
]


GA03 = pd.concat(data, axis=1, keys=headers)
GA03["Date"] = pd.to_datetime(GA03["Date"])
# remove unwanted lons and lats
#GA03 = GA03[
#    ((GA03.Longitude <= 360 - 60) & (GA03.Longitude >= 360 - 65))
#    | ((GA03.Longitude >= 360 - 23) & (GA03.Latitude < 20))
#]
# print(pd.unique(GA03.Station))
GA03 = average_data(GA03)
add_NSTAR_data(GA03)
add_density_data(GA03)
add_ratio_data(GA03)
GA03 = remove_empty_data(GA03)  # remove empty iron data
GA03 = GA03[(GA03.Depth <= maxdepth)]  # only keep data less than 500m depth
GA03["Date"] = GA03.Date.dt.date  # only keep the day,month,year of the date

GA03.loc[(GA03.Station == "Station 10") & (GA03.Longitude < -50), "Station"] = (
    GA03.loc[(GA03.Station == "Station 10") & (GA03.Longitude < -50), "Station"].astype(
        str
    )
    + "W"
)
GA03.loc[(GA03.Station == "Station 11") & (GA03.Longitude < -50), "Station"] = (
    GA03.loc[(GA03.Station == "Station 11") & (GA03.Longitude < -50), "Station"].astype(
        str
    )
    + "W"
)
GA03.loc[(GA03.Station == "Station 10") & (GA03.Longitude > -50), "Station"] = (
    GA03.loc[(GA03.Station == "Station 10") & (GA03.Longitude > -50), "Station"].astype(
        str
    )
    + "E"
)
GA03.loc[(GA03.Station == "Station 11") & (GA03.Longitude > -50), "Station"] = (
    GA03.loc[(GA03.Station == "Station 11") & (GA03.Longitude > -50), "Station"].astype(
        str
    )
    + "E"
)

stations = []
positions = []
for i in range(len(GA03)):
    station = GA03["Station"].values[i]
    lat = GA03["Latitude"].values[i]
    lon = GA03["Longitude"].values[i]
    if len(positions) == 0 or [lat, lon] != positions[-1]:
        positions.append([lat, lon])
        stations.append(station)
print(stations)
#choose stations
#chosenstations = ['Station 10W', 'Station 10E', 'Station 11E', 'Station 11W','Station 9']
#droppedstations = [i for i, x in enumerate(stations) if x not in chosenstations]
#for i in droppedstations:  # dropping specific profiles
#    GA03 = GA03.drop(
#        GA03[
#            (GA03.Latitude == positions[i][0]) & (GA03.Longitude == positions[i][1])
#        ].index
#    )
GA03.to_csv("./data/GA03_filtered.csv", index=False)

# make GIPY05 dataframe and csv
data = [
    GIPY05_data["Station"],
    GIPY05_data["yyyy-mm-ddThh:mm:ss.sss"],
    GIPY05_data["Latitude [degrees_north]"],
    GIPY05_data["Longitude [degrees_east]"],
    GIPY05_data["DEPTH [m]"],
    GIPY05_data["CTDTMP_T_VALUE_SENSOR [deg C]"],
    GIPY05_data["CTDSAL_D_CONC_SENSOR [pss-78]"],
    GIPY05_data["NITRATE_D_CONC_BOTTLE [umol/kg]"],
    GIPY05_data["PHOSPHATE_D_CONC_BOTTLE [umol/kg]"],
    GIPY05_data["CTDOXY_D_CONC_SENSOR [umol/kg]"],
    GIPY05_data["Fe_D_CONC_BOTTLE [nmol/kg]"],
    GIPY05_data["CTDPRS_T_VALUE_SENSOR [dbar]"],
]
GIPY05 = pd.concat(data, axis=1, keys=headers)
GIPY05["Date"] = pd.to_datetime(GIPY05["Date"])

# remove unwanted lons and lats
GIPY05 = GIPY05[(GIPY05.Latitude >= -45) | (GIPY05.Latitude <= -65)]

GIPY05 = average_data(GIPY05)
add_NSTAR_data(GIPY05)
add_density_data(GIPY05)
add_ratio_data(GIPY05)
GIPY05 = remove_empty_data(GIPY05)
GIPY05 = GIPY05[(GIPY05.Depth <= maxdepth)]
GIPY05["Date"] = GIPY05.Date.dt.date

positions = []
stations = []
for i in range(len(GIPY05)):
    station = GIPY05["Station"].values[i]
    lat = GIPY05["Latitude"].values[i]
    lon = GIPY05["Longitude"].values[i]
    if len(positions) == 0 or [lat, lon] != positions[-1]:
        positions.append([lat, lon])
        stations.append(station)
print(stations)
#choose stations
#chosenstations = ['161', '163', '167', '175','178']
#droppedstations = [i for i, x in enumerate(stations) if x not in chosenstations]
#for i in droppedstations:  # dropping specific profiles
#    GIPY05 = GIPY05.drop(
#        GIPY05[
#            (GIPY05.Latitude == positions[i][0]) & (GIPY05.Longitude == positions[i][1])
#        ].index
#    )
GIPY05.to_csv("./data/GIPY05_filtered.csv", index=False)

# make GP02 dataframe and csv
data = [
    GP02_data["Station"],
    GP02_data["yyyy-mm-ddThh:mm:ss.sss"],
    GP02_data["Latitude [degrees_north]"],
    GP02_data["Longitude [degrees_east]"],
    GP02_data["DEPTH [m]"],
    GP02_data["CTDTMP_T_VALUE_SENSOR [deg C]"],
    GP02_data["CTDSAL_D_CONC_SENSOR [pss-78]"],
    GP02_data["NITRATE_D_CONC_BOTTLE [umol/kg]"],
    GP02_data["PHOSPHATE_D_CONC_BOTTLE [umol/kg]"],
    GP02_data["CTDOXY_D_CONC_SENSOR [umol/kg]"],
    GP02_data["Fe_D_CONC_BOTTLE [nmol/kg]"],
    GP02_data["CTDPRS_T_VALUE_SENSOR [dbar]"],
]
GP02 = pd.concat(data, axis=1, keys=headers)
GP02["Date"] = pd.to_datetime(GP02["Date"])
# remove unwanted lons and lats
GP02 = GP02[(GP02.Longitude <= 155) | (GP02.Longitude >= 180)]
GP02 = average_data(GP02)
add_NSTAR_data(GP02)
add_density_data(GP02)
add_ratio_data(GP02)
GP02 = remove_empty_data(GP02)
GP02 = GP02[(GP02.Depth <= maxdepth)]
GP02["Date"] = GP02.Date.dt.date

positions = []
stations = []
for i in range(len(GP02)):
    station = GP02["Station"].values[i]
    lat = GP02["Latitude"].values[i]
    lon = GP02["Longitude"].values[i]
    if len(positions) == 0 or [lat, lon] != positions[-1]:
        positions.append([lat, lon])
        stations.append(station)
print(stations)
#choose stations
#chosenstations = ['BD04', 'BD05', 'BD06', 'BD15','BD16']
#droppedstations = [i for i, x in enumerate(stations) if x not in chosenstations]
#for i in droppedstations:  # dropping specific profiles
#        GP02 = GP02.drop(GP02[(GP02.Latitude == positions[i][0]) & (GP02.Longitude == positions[i][1])].index)
GP02.to_csv("./data/GP02_filtered.csv", index=False)

# make GIPY04 dataframe and csv
data = [
    GIPY04_data["Station"],
    GIPY04_data["yyyy-mm-ddThh:mm:ss.sss"],
    GIPY04_data["Latitude [degrees_north]"],
    GIPY04_data["Longitude [degrees_east]"],
    GIPY04_data["DEPTH [m]"],
    GIPY04_data["CTDTMP_T_VALUE_SENSOR [deg C]"],
    GIPY04_data["CTDSAL_D_CONC_SENSOR [pss-78]"],
    GIPY04_data["NITRATE_D_CONC_BOTTLE [umol/kg]"],
    GIPY04_data["PHOSPHATE_D_CONC_BOTTLE [umol/kg]"],
    GIPY04_data["CTDOXY_D_CONC_SENSOR [umol/kg]"],
    GIPY04_data["Fe_D_CONC_BOTTLE [nmol/kg]"],
    GIPY04_data["CTDPRS_T_VALUE_SENSOR [dbar]"],
]
GIPY04 = pd.concat(data, axis=1, keys=headers)
GIPY04["Date"] = pd.to_datetime(GIPY04["Date"])
# remove unwanted lons and lats
#GIPY04 = GIPY04[(GIPY04.Latitude >= -45)]
GIPY04 = average_data(GIPY04)
add_NSTAR_data(GIPY04)
add_density_data(GIPY04)
add_ratio_data(GIPY04)
GIPY04 = remove_empty_data(GIPY04)
GIPY04 = GIPY04[(GIPY04.Depth <= maxdepth)]
# remove specific noisy data
indexes = GIPY04[
    (GIPY04.Station == "18 (Super 1)")
    & (
        (GIPY04.Depth == 78.6)
        | (GIPY04.Depth == 98.6)
        | (GIPY04.Depth == 149.8)
        | (GIPY04.Depth == 172.8)
    )
].index
GIPY04.drop(indexes, inplace=True)
GIPY04["Date"] = GIPY04.Date.dt.date

positions = []
stations = []
for i in range(len(GIPY04)):
    station = GIPY04["Station"].values[i]
    lat = GIPY04["Latitude"].values[i]
    lon = GIPY04["Longitude"].values[i]
    if len(positions) == 0 or [lat, lon] != positions[-1]:
        positions.append([lat, lon])
        stations.append(station)
print(stations)
#choose stations
#chosenstations = ['18 (Super 1)', '34 (Super 2)']
#droppedstations = [i for i, x in enumerate(stations) if x not in chosenstations]
#for i in droppedstations:  # dropping specific profiles
#    GIPY04 = GIPY04.drop(
#        GIPY04[
#            (GIPY04.Latitude == positions[i][0]) & (GIPY04.Longitude == positions[i][1])
#        ].index
#    )
GIPY04.to_csv("./data/GIPY04_filtered.csv", index=False)
