**Data.** UBC EOSC 473/573 field-school CTD casts, Bamfield Marine Sciences Centre, 2001–2026
(none in 2010 or 2019–2022): Sea-Bird SBE19, SBE19plus and SBE25 profilers, read with
`Past_CTD_data/seabird.py`, and for 2025 an AML-6, read after HB's AML-CTD-Tools. 2025 has no
fluorescence or PAR, and its oxygen is from a different sensor (an optode). Variables are TEOS-10 (IOC, SCOR and IAPSO, 2010), converted from the files' in-situ temperature
and practical salinity with `gsw`: Conservative Temperature, Absolute Salinity and σ₀. Oxygen is in µmol L⁻¹.
Fluorescence is an uncalibrated relative index, and 2012's
values are omitted because they sit on a different scale from every other year. Five cast positions are corrected by hand (four deep casts with no usable position placed at
Sarita Hole, one latitude typo); 23 casts with impossible positions are set aside. Values outside
plausible ranges are dropped, not corrected; `build_dashboard_data.py` prints how many.

**Layout** adapted from the EOSC 372 ocgy-dataviewer; the multi-axis profile follows AML-CTD-Tools.
