# Model Info - cl, cli, clw
## General
- clw: Mass Fraction of Cloud Liquid Water [kg kg-1], Table: Amon, CFsubhr
- cli: Mass Fraction of Cloud Ice [kg kg-1], Table: Amon, CFsubhr
- sftlf: Percentage of the grid cell occupied by land (including lakes) [%]
- cl: Percentage Cloud Cover [%]

---
## CESM2
- hot
- experiments: historical, piControl, abrupt-4xCO2, ssp585
- sftlf for all
- atmosphere hybrid sigma pressure coordinate: p = a\*p0 + b\*ps
### historical
- 1850 to 2014
- lev in hPa, pointing up
### piControl
- 0001 to 1200
- lev in hPa, pointing up
### abrupt-4xCO2
- 0001 to 0999
- lev in hPa, pointing up
### ssp585
- 2015 to 2100
- lev in bar(1), pointing down

---
## UKESM1-0-LL
- hot
- experiments: historical, piControl, abrupt-4xCO2, ssp585
- only sftlf is for piControl
- atmosphere hybrid height coordinate: z = a + b\*orog
### historical
- lev in m, points up
- 1850 to 2014
### piControl
- 1960 to 3059
- lev in m, points up
### abrupt-4xCO2
- 1850 to 1999
- lev in m, points up
### ssp585
- 2015 to 2100
- lev in m, points up

---
## CanESM5
- hot
- experiments: historical, piControl, abrupt-4xCO2, ssp585, hist-volc (only for cl)
- sftlf for all
- atmosphere hybrid sigma pressure coordinate: p = ap + b\*ps
### historical
- 1850 to 2014
- lev in bar(1), points down
### piControl
- 5550 to 5715
- lev in bar(1), points down
### abrupt-4xCO2
- 1850 to 2000
- lev in bar(1), points down
### ssp585
- 2015 to 2100
- lev in bar(1), points down
### hist-volc
- 1850 to 2020
- lev in bar(1), points down
- no clw

---
## GISS-E2-1-H
- cold
- experiments: historical, piControl, abrupt-4xCO2, ssp585
- only sftlf is for piControl
- atmosphere hybrid sigma pressure coordinate: p = a\*p0 + b\*ps
### historical
- 1850 to 2014
- lev in bar(1), points down
### piControl
- 3180 to 3980
- lev in bar(1), points down
### abrupt-4xCO2
- 1850 to 2000
- lev in bar(1), points down
### ssp585
- 2015 to 2500
- lev in bar(1), points down

---
## MRI-ESM2-0
- cold
- experiments: historical, piControl, abrupt-4xCO2, ssp585, hist-stratO3
- sftlf for all
- datetime
- atmosphere hybrid sigma pressure coordinate: p = a\*p0 + b\*ps
### historical
- 1850 to 2014
- lev in bar(1), points down
### piControl
- 1850 to 2100
- lev in bar(1), points down
### abrupt-4xCO2
- 1850 to 2000
- lev in bar(1), points down
### ssp585
- 2015 to 2100
- lev in bar(1), points down
### hist-stratO3
- 1850 to 2020
- lev in bar(1), points down
- no clw

---
## BCC-ESM1
- cold
- experiments: historical, piControl, abrupt-4xCO2
- only sftlf is for 1pctCO2
- atmosphere hybrid sigma pressure coordinate: p = a\*p0 + b\*ps
### historical
- 1850 to 2014
- lev in bar(1), points down
### piControl
- 1850 to 2300
- lev in bar(1), points down
### abrupt-4xCO2
- 1850 to 2000
- lev in bar(1), points down
