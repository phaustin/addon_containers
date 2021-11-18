# Oceanography Dataviewer
This is a dashboard created as an assignment for the oceanography course, EOSC 372. The ocgy-dataviewer has interactive maps so the user can plot depth profiles from various stations and cruises. The dashboard is hosted [here](https://ocgy-dataviewer.herokuapp.com/).

## Data Collection
- The data is from the eGEOTRACES project and is collected [here](https://www.egeotraces.org/) for the following parameters: nitrate, iron, salinity, temperature.
- The ratio of [nitrate] to [iron] is calculated from this data and added to the csv files.
- Density is calculated from salinity and temperature.
- Data collection and filtering is detailed in the "data_documentation" file.