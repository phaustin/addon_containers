# UBC Earth, Ocean and Atmospheric Science Dashboards

This repository contains the source code and [traefik proxy](https://traefik.io/traefik/) configuration files to run a collection of [plotly](https://github.com/plotly/dash) dashboards.  Each dashboard is an individual docker container, built using this [docker-compose.yml](./docker-compose.yml) file.  Routing to the containers is currently done using [the digital ocean dns](https://docs.digitalocean.com/products/networking/dns/), with [lets encrypt's dns challenge](https://github.com/phaustin/addon_containers/blob/main/traefik/config/traefik.yml#L15-L22).


## Climate science & oceanography:

* **[ocgy-dataviewer](https://dashboard.eoas.ubc.ca/ocgy)**: observe and compare trace element and physical properties in the water column at selected locations in the Southern Ocean, the Atlantic and the North Pacific. [Source: ocgy-dataviewer](ocgy-dataviewer). Initially used as an assignment in [EOSC 372](https://www.eoas.ubc.ca/academics/courses/eosc372) in the Fall term, 2021.

* **[Global temperature](https://dashboard.eoas.ubc.ca/globaltemps)**: Contributions of several natural and anthropogenic factors to the global temperature anomaly are plotted for 1880-2005, with short explanations. Sketch interactivity is included. [Source: global-temps](globaltemp-factors). Initially used in [EOSC 112](https://www.eoas.ubc.ca/academics/courses/eosc11) and [EOSC 326](https://www.eoas.ubc.ca/academics/courses/eosc326) in the Fall term, 2021.

* **[Atmospheric CO2](https://dashboard.eoas.ubc.ca/co2mlo)**: Monthly averages at Mauna Loa and the South Pole, with user-defined straight line model for crude predictions. [Source: co2-mlo ](co2-mlo-spo). Initially used in [ENVR 300](https://www.eoas.ubc.ca/academics/courses/envr300) in Winter term 2021, then updated for Winter term 2022.

* **[Daisyworld](https://dashboard.eoas.ubc.ca/daisy)** displays inhabited area as a function of time when daisyworld parameters are varied. Both constant and varying solar flux situations are modeled.  [Source: daisy-world](daisy-world). Initially used in [EOSC 310](https://www.eoas.ubc.ca/academics/courses/eosc310) in Fall term, 2021.

### In development

* **[cmip6-lowcloud](https://dashdev.eoastest.xyz/cmip6-lowcloud)** compares the trend in fractional low cloud cover in the eastern Pacific for a range of CMIP6 models and scenarios. [Source: cmip6-lowcloud](cmip6_lowcloud)

* **[cmip6-dash](https://dashdev.eoastest.xyz/cmip6dash)**.  General tool for comparing regional changes between CMIP6 models and scenarios for different climae variables. [Source: cmip6dash](https://github.com/phaustin/cmip6_dash)

## Geology and hydrogeology

* **[Storativity](https://dashboard.eoas.ubc.ca/store)** compares hydrological storativity of various geologic materials. [Source: hydro-storativity](hydro-storativity) Initially used in [EOSC 325](https://www.eoas.ubc.ca/academics/courses/eosc325) in Fall term, 2021.

* **[Unconfined-flow](https://dashboard.eoas.ubc.ca/hydro)** interactive model of linar ("1D") groundwater flow in an unconfined acquifer between two sources, with surface recharge included.  
[Source: unconfined-flow](hydro-ucflow). Initially used in [EOSC 325](https://www.eoas.ubc.ca/academics/courses/eosc325) in Fall term, 2021.

* **[Drawdown](https://dashboard.eoas.ubc.ca/drawdown)** for confined and unconfined acquifers plots 2D drawdown curves for a well in a uniform acquifer with adjustable properties.  [Source: drawdown](hydro-drawdown). Initially used in [EOSC 325](https://www.eoas.ubc.ca/academics/courses/eosc325) in Fall term, 2021.

* **[Mohrs](https://dashboard.eoas.ubc.ca/mohrs)** for exploring Mohr's circle representation of stresses and failure within rocks.  [Source: mohrs](mohrs). Initially built for use in [EOSC 323](https://www.eoas.ubc.ca/academics/courses/eosc323), [422](https://www.eoas.ubc.ca/academics/courses/eosc422) and [424](https://www.eoas.ubc.ca/academics/courses/eosc424).

## Geophysics or "signals"

* **[timeseries-3signals](https://dashboard.eoas.ubc.ca/timeseries)** adjustable parameters illustrating noise and trend on a sinewave, with smoothing.  
[Source: timeseries](timeseries). Initially used in [ENVR 300](https://www.eoas.ubc.ca/academics/courses/envr300) in Winter term 2021, then updated for Winter term 2022.

# Traefik configuration

See [traefik/config](traefik/config) for static and dynamic route configuration.
