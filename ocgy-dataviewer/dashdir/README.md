# Oceanography Dataviewer
This is a dashboard created as an assignment for the oceanography course, EOSC 372. The ocgy-dataviewer has an interactive world map so the user can plot depth profiles from various stations and cruises. Sources and attributions are at the bottome of the app's page. 

## Data Collection
- The data is from the eGEOTRACES project and is collected [here](https://www.egeotraces.org/) for the following parameters: nitrate, iron, salinity, temperature.
- The ratio of [nitrate] to [iron] is calculated from this data and added to the csv files.
- Density is calculated from salinity and temperature.
- Data collection and filtering is detailed in the "data_documentation" file.

## Version 2, summer 2022
- All cruises and the selected stations are plotted together so the user does not have to choose a cruise. This allows for comparison of water property profiles from different oceans.
- Colors and markers are clarified so they are easier to distinguish on profile plots.
- Hover labels (flyout labels when hovering over stations on the map) are more informative and better formatted.