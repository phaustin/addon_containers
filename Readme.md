# UBC Earth, Ocean and Atmospheric Science Dashboards

This repository contains the source code and [traefik proxy](https://traefik.io/traefik/) configuration files to run a collection of [plotly](https://github.com/plotly/dash) dashboards on a [digital ocean](https://www.digitalocean.com/) host.  Each dashboard is an individual docker container, built using this [docker-compose.yml](./docker-compose.yml) file


## Climate science & oceanography:

* **[ocgy-dataviewer](https://dashboard.eoastest.xyz/ocgy)**: observe and compare trace element and physical properties in the water column at selected locations in the Southern Ocean, the Atlantic and the North Pacific. [Source: ocgy-dataviewer](ocgy-dataviewer). Initially used as an assignment in [EOSC 372](https://www.eoas.ubc.ca/academics/courses/eosc372) in the Fall term, 2021.

* **[Global temperature](https://dashboard.eoastest.xyz/globaltemps)**: Contributions of several natural and anthropogenic factors to the global temperature anomaly are plotted for 1880-2005, with short explanations. Sketch interactivity is included. [Source: global-temps](global-temps). Initially used in [EOSC 112](https://www.eoas.ubc.ca/academics/courses/eosc11) and [EOSC 326](https://www.eoas.ubc.ca/academics/courses/eosc326) in the Fall term, 2021.

* **[Atmospheric CO2](https://dashboard.eoastest.xyz/co2mlo)**: Monthly averages at Mauna Loa and the South Pole, with user-defined straight line model for crude predictions. [Source: co2-mlo ](co2-mlo-spo). Initially used in [ENVR 300](https://www.eoas.ubc.ca/academics/courses/envr300) in Winter term 2021, then updated for Winter term 2022.

* **[Daisyworld](https://dashboard.eoastest.xyz/daisy)** displays inhabited area as a function of time when daisyworld parameters are varied. Both constant and varying solar flux situations are modeled.  [Source: daisy-world](daisy-world). Initially used in [EOSC 310](https://www.eoas.ubc.ca/academics/courses/eosc310) in Fall term, 2021.

## Geology and hydrogeology

* **[Storativity](https://dashboard.eoastest.xyz/store)** compares hydrological storativity of various geologic materials. [Source: hydro-storativity](hydro-storativity) Initially used in [EOSC 325](https://www.eoas.ubc.ca/academics/courses/eosc325) in Fall term, 2021.

* **[Unconfined-flow](https://dashboard.eoastest.xyz/hydro)** interactive model of linar ("1D") groundwater flow in an unconfined acquifer between two sources, with surface recharge included.  
[Source: unconfined-flow](hydro). Initially used in [EOSC 325](https://www.eoas.ubc.ca/academics/courses/eosc325) in Fall term, 2021.

* **[Drawdown](https://dashboard.eoastest.xyz/drawdown)** for confined and unconfined acquifers plots 2D drawdown curves for a well in a uniform acquifer with adjustable properties.  [Source: drawdown](drawdown). Initially used in [EOSC 325](https://www.eoas.ubc.ca/academics/courses/eosc325) in Fall term, 2021.

## Geophysics or "signals"

* **[timeseries-3signals](https://dashboard.eoastest.xyz/timeseries)** adjustable parameters illustrating noise and trend on a sinewave, with smoothing.  
[Source: timeseries](timeseries). Initially used in [ENVR 300](https://www.eoas.ubc.ca/academics/courses/envr300) in Winter term 2021, then updated for Winter term 2022.

