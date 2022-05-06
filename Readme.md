# UBC Earth, Ocean and Atmospheric Science Dashboards

This repository contains the source code and [traefik proxy](https://traefik.io/traefik/) configuration files to run a collection of [plotly](https://github.com/plotly/dash) dashboards on a [digital ocean](https://www.digitalocean.com/) host.  Each dashboard is an individual docker container, built using this [docker-compose.yml](./docker-compose.yml) file


## Climate science & oceanography:

* **[ocgy-dataviewer](https://dashboard.eoastest.xyz/ocgy)**: observe and compare trace element and physical properties in the water column at selected locations in the Southern Ocean, the Atlantic and the North Pacific. [ocgy-dataviewer source](./ocgy_dataviewr). Initially used as an assignment in [EOSC 372](https://www.eoas.ubc.ca/academics/courses/eosc372) in the Fall term, 2021.

* **[Global temperature](https://dashboard.eoastest.xyz/globaltemps)**: Contributions of several natural and anthropogenic factors to the global temperature anomaly are plotted for 1880-2005, with short explanations. Sketch interactivity is included. [global-temps source](./global_temps). Initially used in [EOSC 112](https://www.eoas.ubc.ca/academics/courses/eosc11) and [EOSC 326](https://www.eoas.ubc.ca/academics/courses/eosc326) in the Fall term, 2021.

* **[Atmospheric CO2](https://dashboard.eoastest.xyz/co2mlo)**: Monthly averages at Mauna Loa and the South Pole, with user-defined straight line model for crude predictions. [co2-mlo source](./co2-mlo-spo). Initially used in [ENVR 300](https://www.eoas.ubc.ca/academics/courses/envr300) in Winter term 2021, then updated for Winter term 2022.

* **[Daisyworld](https://dashboard.eoastest.xyz/daisy)** displays inhabited area as a function of time when daisyworld parameters are varied. Both constant and varying solar flux situations are modeled.[daisy-world source](./daisy-world). Initially used in [EOSC 310](https://www.eoas.ubc.ca/academics/courses/eosc310) in Fall term, 2021.

## Geology and hydrogeology

* **[Storativity](https://dashboard.eoastest.xyz/store)** compares hydrological storativity of various geologic materials. [hydro-storativity source](./hydro-storativity) Initially used in [EOSC 325](https://www.eoas.ubc.ca/academics/courses/eosc325) in Fall term, 2021.

* **[Unconfined-flow](https://dashboard.eoastest.xyz/hydro)** interactive model of linar ("1D") groundwater flow in an unconfined acquifer between two sources, with surface recharge included. Github repository is the "hydro" folder [here](https://github.com/phaustin/addon_containers). Initially used in [EOSC 325](https://www.eoas.ubc.ca/academics/courses/eosc325) in Fall term, 2021.

* **[Drawdown](https://dashboard.eoastest.xyz/drawdown)** for confined and unconfined acquifers plots 2D drawdown curves for a well in a uniform acquifer with adjustable properties. Github repository is the "drawdown" folder [here](https://github.com/phaustin/addon_containers). Initially used in [EOSC 325](https://www.eoas.ubc.ca/academics/courses/eosc325) in Fall term, 2021.

* **[Mohr's circles](https://mohrs.herokuapp.com/)**; plots Mohr's circles and failure envelopes by interactively adjusting stress. Github [repo](https://github.com/fhmjones/mohrs).

## Geophysics or "signals"

* **[timeseries-3signals](https://dashboard.eoastest.xyz/timeseries)** adjustable parameters illustrating noise and trend on a sinewave, with smoothing. Github repository is the "timeseries" folder [here](https://github.com/phaustin/addon_containers). Initially used in [ENVR 300](https://www.eoas.ubc.ca/academics/courses/envr300) in Winter term 2021, then updated for Winter term 2022.

* **timeseries-FFT** (not online). On github at [repo](https://github.com/fhmjones/timeseries-fft); works, but incomplete.

* **[interactive images](https://clickimage.herokuapp.com/)** is an initial experiment exploring how to interact with figures for future dashboards planned for paleontology and other disciplines. Github repo [here](https://github.com/fhmjones/ClickImage).

* **[gpglabs](https://gpg.geosci.xyz/content/appendix/apps.html)** is an extensive collection of interactive Jupyter Notebooks illustrating concepts in applied geophysics including forward & inverse modeling and physics. See the [GPG applied geophysics textbook](https://gpg.geosci.xyz/) or the interactive NoteBooks collection [repository](https://github.com/geoscixyz/gpgLabs), both with links for running NoteBooks using Binder, Azure Notebooks, or locally on your own computer.
