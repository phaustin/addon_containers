# ocgy-dataviewer
A dashboard utility for displaying depth profiles of oceanographic data.

Initially for use in EOSC 372 "Introductory Oceanography: Circulation and Plankton", https://www.eoas.ubc.ca/academics/courses/eosc372

### Outline
The desired depth profiles are as follows:
- From the GIPY04 and GIPY05e cruises: 4 depth profiles south of 65S and 4 depth profiles north of 45S.
- From the GA03w cruise: 2 depth profiles in the Sargasso Sea and 2 depth profiles close to the Sahara Desert.
- From the GP02w cruise: 2 depth profiles closest to the east side and 2 depth profiles closest to the west side.
### Data Collection
- The data is collected [here](https://www.egeotraces.org/) for the following parameters: nitrate, iron, salinity, temperature.
- The ratio of [nitrate] to [iron] is calculated from this data and added to the csv files.
- Density is calculated from salinity and temperature.
- Data collection and filtering is detailed in the "data_documentation" file.
### Plotting the Data
- The Dash shows a map of the stations for the chosen cruise. Hovering over the stations produces the depth profiles (temperature, salinity, nitrate, iron, ratio of nitrate to iron, density) on subplots below. Clicking on a station creates fixed depth profiles on the subplots below. 
- The subplots show the depth profiles from 0 to 500m depth. This can be adjusted with a slider to the left of the subplots. 
- There are radiobuttons to select a cruise to plot.
- The x-axis range can be changed by radiobuttons. 'default' selects a constant x-axis, and 'fit to data' chooses an x-axis for the current plot.
- The subplots can be saved as a png file to submit.