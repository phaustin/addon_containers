# Data Documentation

## Selecting Parameters:
- For all of the data, PUMP, FISH, and UWAY either have no data in range or only a few points.
- For salinity, CTDSAL provides enough profiles for each of the cruises, and BOTTLE does not have data for GIPY05, so I used CTDSAL.
- For nitrate, NITRATE_D_CONC_BOTTLE has profiles for GIPY04 and GA03 but not the other two, and NO2+NO3_D_CONC_BOTTLE has profiles for GIPY05 and GP02 but not the other two.
- For temperature and iron there is only one choice and it has sufficient profiles.

## Fetching and Preparing the Data
- Data is collected from the [geotraces site](https://geotraces.webodv.awi.de/) and downloaded as a .txt
- Remove all the lines in the file that begin with "//" in Powershell, using the command:  
`Get-Content data.txt | Where { $_ -notmatch "^//" } | Set-Content filtered_data_.txt`
- The new .txt is converted to a csv using Excel

## Filtering the Data
- The data file downloaded gave the entire GIPY05 cruise, so I manually removed stations so the file only contained GIPY05e. Similarly with the other cruises.
- I used pandas to create filtered versions of the csv files for each cruise. The filtering process:
    - Selects data within a specified latitude and longitude range
    - Removes stations with no iron data
    - Removes data lower than 500m depth
    - Averages data collected at the exact same depth
    - Creates a column and adds the ratio data
    - Creates a column and adds the density data
    - Removes specific stations that have been indicated
    - Removes specific data points that have been indicated

## Calculated Data
The ratio and density data were both calculated. 
- The ratio data could not be calculated simply by dividing nitrate by iron, since there were not enough data calculate at the same depth. Instead an average nitrate value was calculated first. This is the average of nitrate for +/- 5m for values <= 100m depth, and +/- 10m for values > 100m depth. This averaged nitrate is then divided by iron to produce the ratio column.
- The density data is calculated using the [gsw library](http://www.teos-10.org/pubs/gsw/html/gsw_contents.html). Potential density anomoly is calculated using the `gsw.sigma0` function which takes in absolute salinity and temperature. The salinity from the original data is potential salinity, so the `gsw.SA_from_SP` function was used to get absolute salinity from potential salinity first. 
