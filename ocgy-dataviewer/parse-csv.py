# any work with the data file
# make a nicer csv to pull from
import pandas as pd
import gsw


# all of the parameters from the full data: 'Longitude [degrees_east]', 'Latitude [degrees_north]',
# 'PRESSURE [dbar]', 'DEPTH [m]', 'CTDTMP [deg C]', 'CTDSAL', 'SALINITY_D_CONC_BOTTLE', 'SALINITY_D_CONC_PUMP',
# 'SALINITY_D_CONC_FISH', 'SALINITY_D_CONC_UWAY', 'NITRATE_D_CONC_BOTTLE [umol/kg]', 'NITRATE_D_CONC_PUMP [umol/kg]',
# 'NITRATE_D_CONC_FISH [umol/kg]', 'NITRATE_D_CONC_UWAY [umol/kg]', 'NITRATE_LL_D_CONC_BOTTLE [umol/kg]',
# 'NITRATE_LL_D_CONC_FISH [umol/kg]', 'NO2+NO3_D_CONC_BOTTLE [umol/kg]', 'NO2+NO3_D_CONC_FISH [umol/kg]',
# 'Fe_D_CONC_BOTTLE [nmol/kg]', 'Fe_D_CONC_FISH [nmol/kg]', 'Fe_II_D_CONC_BOTTLE [nmol/kg]', 'Fe_II_D_CONC_FISH [nmol/kg]',
# 'Fe_S_CONC_BOTTLE [nmol/kg]', 'Fe_S_CONC_FISH [nmol/kg]'

def average_data(cruise_data):
    # from https://stackoverflow.com/questions/48830324/pandas-average-columns-with-same-value-in-other-columns
    cruise_data = cruise_data.groupby(['Latitude', 'Longitude', 'Station', 'Depth'], as_index=False).mean()
    return cruise_data


# removes specifically empty iron data.
def remove_empty_data(cruise_data):
    grouped_data = cruise_data.groupby(['Latitude', 'Longitude', 'Station'])
    for name, group in grouped_data:
        if (group['Iron'].isna().values.all()):
            cruise_data = cruise_data.drop(grouped_data.get_group(name).index)
    return cruise_data


# add data for [Nitrate] : [Fe] or [Nitrate]/[Fe]
def add_ratio_data(cruise_data):
    nit = cruise_data['Nitrate']
    iron = cruise_data['Iron']
    ratio = nit/iron

    cruise_data['Ratio'] = ratio


def add_density_data(cruise_data):
    #from: http://www.teos-10.org/pubs/gsw/html/gsw_sigma0.html
    practical_salinity = cruise_data['Salinity']
    pressure = cruise_data['Pressure']
    longitude = cruise_data['Longitude']
    latitude = cruise_data['Latitude']
    absolute_salinity = gsw.SA_from_SP(practical_salinity, pressure, longitude, latitude)
    temperature = cruise_data['Temperature']
    sigma0 = gsw.sigma0(absolute_salinity, temperature)

    cruise_data['Density'] = sigma0

'''
def add_test_density_data(cruise_data):
    practical_salinity = cruise_data['Salinity']
    temperature = cruise_data['Temperature']
    sigma0 = gsw.sigma0(practical_salinity, temperature)

    cruise_data['Density'] = sigma0
'''

# read in original data
GA03_data = pd.read_csv("./data/GA03w.csv")
GIPY05_data = pd.read_csv("./data/GIPY05e.csv")
GP02_data = pd.read_csv("./data/GP02w.csv")
GIPY04_data = pd.read_csv("./data/GIPY04.csv")
#TEST_data = pd.read_csv("./data/TestCruise.csv")

headers = ['Station', 'Latitude', 'Longitude', 'Depth', 'Temperature', 'Salinity', 'Nitrate', 'Iron', 'Pressure']

'''
#make TEST dataframe
data = [TEST_data['Station'], TEST_data['Latitude [degrees_north]'], TEST_data['Longitude [degrees_east]'],
        TEST_data['DEPTH [m]'], TEST_data['CTDTMP [deg C]'], TEST_data['CTDSAL'], TEST_data['NO2+NO3_D_CONC_BOTTLE [umol/kg]'],
        TEST_data['Fe_D_CONC_BOTTLE [nmol/kg]'], TEST_data['PRESSURE [dbar]']]
TEST = pd.concat(data, axis=1, keys=headers)
add_density_data(TEST)
TEST.to_csv('TEST_filtered.csv', index=False)
'''


# make GA03 dataframe and csv
data = [GA03_data['Station'], GA03_data['Latitude [degrees_north]'], GA03_data['Longitude [degrees_east]'],
        GA03_data['DEPTH [m]'], GA03_data['CTDTMP [deg C]'], GA03_data['CTDSAL'], GA03_data['NITRATE_D_CONC_BOTTLE [umol/kg]'],
        GA03_data['Fe_D_CONC_BOTTLE [nmol/kg]'], GA03_data['PRESSURE [dbar]']]
GA03 = pd.concat(data, axis=1, keys=headers)
# remove unwanted lons and lats
GA03 = GA03[((GA03.Longitude <= 360 - 60) & (GA03.Longitude >= 360 - 65)) | (GA03.Longitude >= 360 - 25)]
GA03 = average_data(GA03)
add_ratio_data(GA03)
add_density_data(GA03)
GA03 = remove_empty_data(GA03)
GA03 = GA03[(GA03.Depth <= 500)]

stations = []
positions = []
for i in range(len(GA03)):
    station = GA03['Station'].values[i]
    lat = GA03['Latitude'].values[i]
    lon = GA03['Longitude'].values[i]
    if len(positions) == 0 or [lat, lon] != positions[-1]:
        positions.append([lat, lon])
        stations.append(station)
# print(stations)
for i in [4]:  # choosing specific profiles
    GA03 = GA03.drop(GA03[(GA03.Latitude == positions[i][0]) & (GA03.Longitude == positions[i][1])].index)
GA03.to_csv('./data/GA03_filtered.csv', index=False)

# make GIPY05 dataframe and csv
data = [GIPY05_data['Station'], GIPY05_data['Latitude [degrees_north]'], GIPY05_data['Longitude [degrees_east]'],
        GIPY05_data['DEPTH [m]'],
        GIPY05_data['CTDTMP [deg C]'], GIPY05_data['CTDSAL'], GIPY05_data['NO2+NO3_D_CONC_BOTTLE [umol/kg]'],
        GIPY05_data['Fe_D_CONC_BOTTLE [nmol/kg]'], GIPY05_data['PRESSURE [dbar]']]
GIPY05 = pd.concat(data, axis=1, keys=headers)
# remove unwanted lons and lats
GIPY05 = GIPY05[(GIPY05.Latitude >= -45) | (GIPY05.Latitude <= -65)]
GIPY05 = average_data(GIPY05)
add_ratio_data(GIPY05)
add_density_data(GIPY05)
GIPY05 = remove_empty_data(GIPY05)
GIPY05 = GIPY05[(GIPY05.Depth <= 500)]

positions = []
stations = []
for i in range(len(GIPY05)):
    station = GIPY05['Station'].values[i]
    lat = GIPY05['Latitude'].values[i]
    lon = GIPY05['Longitude'].values[i]
    if len(positions) == 0 or [lat, lon] != positions[-1]:
        positions.append([lat, lon])
        stations.append(station)
# print(stations)
# for i in []: #choosing specific profiles
#        GIPY05 = GIPY05.drop(GIPY05[(GIPY05.Latitude == positions[i][0]) & (GIPY05.Longitude == positions[i][1])].index)
GIPY05.to_csv('./data/GIPY05_filtered.csv', index=False)

# make GP02 dataframe and csv
data = [GP02_data['Station'], GP02_data['Latitude [degrees_north]'], GP02_data['Longitude [degrees_east]'],
        GP02_data['DEPTH [m]'],
        GP02_data['CTDTMP [deg C]'], GP02_data['CTDSAL'], GP02_data['NO2+NO3_D_CONC_BOTTLE [umol/kg]'],
        GP02_data['Fe_D_CONC_BOTTLE [nmol/kg]'], GP02_data['PRESSURE [dbar]']]
GP02 = pd.concat(data, axis=1, keys=headers)
# remove unwanted lons and lats
GP02 = GP02[(GP02.Longitude <= 155) | (GP02.Longitude >= 180)]
GP02 = average_data(GP02)
add_ratio_data(GP02)
add_density_data(GP02)
GP02 = remove_empty_data(GP02)
GP02 = GP02[(GP02.Depth <= 500)]

positions = []
stations = []
for i in range(len(GP02)):
    station = GP02['Station'].values[i]
    lat = GP02['Latitude'].values[i]
    lon = GP02['Longitude'].values[i]
    if len(positions) == 0 or [lat, lon] != positions[-1]:
        positions.append([lat, lon])
        stations.append(station)
# print(stations)
# for i in []: #choosing specific profiles
#        GP02 = GP02.drop(GP02[(GP02.Latitude == positions[i][0]) & (GP02.Longitude == positions[i][1])].index)
GP02.to_csv('./data/GP02_filtered.csv', index=False)

# make GIPY04 dataframe and csv
data = [GIPY04_data['Station'], GIPY04_data['Latitude [degrees_north]'], GIPY04_data['Longitude [degrees_east]'],
        GIPY04_data['DEPTH [m]'],
        GIPY04_data['CTDTMP [deg C]'], GIPY04_data['CTDSAL'], GIPY04_data['NITRATE_D_CONC_BOTTLE [umol/kg]'],
        GIPY04_data['Fe_D_CONC_BOTTLE [nmol/kg]'], GIPY04_data['PRESSURE [dbar]']]
GIPY04 = pd.concat(data, axis=1, keys=headers)
# remove unwanted lons and lats
GIPY04 = GIPY04[(GIPY04.Latitude >= -45)]
GIPY04 = average_data(GIPY04)
add_ratio_data(GIPY04)
add_density_data(GIPY04)
GIPY04 = remove_empty_data(GIPY04)
GIPY04 = GIPY04[(GIPY04.Depth <= 500)]

positions = []
stations = []
for i in range(len(GIPY04)):
    station = GIPY04['Station'].values[i]
    lat = GIPY04['Latitude'].values[i]
    lon = GIPY04['Longitude'].values[i]
    if len(positions) == 0 or [lat, lon] != positions[-1]:
        positions.append([lat, lon])
        stations.append(station)
# print(stations)
for i in [0, 2, 4]:  # choosing specific profiles
    GIPY04 = GIPY04.drop(GIPY04[(GIPY04.Latitude == positions[i][0]) & (GIPY04.Longitude == positions[i][1])].index)
GIPY04.to_csv('./data/GIPY04_filtered.csv', index=False)
