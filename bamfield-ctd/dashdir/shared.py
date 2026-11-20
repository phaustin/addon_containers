"""Settings and helpers shared by the build (build_dashboard_data.py) and the running app
(upload.py). Kept separate so the server copy of the app needs neither the build script nor its
local data paths."""
import numpy as np

# Bins centred at or above this depth are dropped, in the archive and in uploaded casts (HB,
# 20 Nov 2026). The processing skips a fixed number of scans for the surface soak, and whatever
# the operator held beyond that lands in the top bins: in 86% of the reprocessed casts a bin
# shallower than 5 m holds more than 5x the usual scans, nearly always at 0.5-1.5 m. Dropping
# the 0.5 and 1.0 m bins removes the whole soak in 81% of those casts, and every cast then
# starts at the same depth (1.5 m).
SURFACE_CUT_M = 1.0


def km_between(lat1, lon1, lat2, lon2):
    """Equirectangular distance in km; plenty accurate over a 30 km sound."""
    kx = 111.32 * np.cos(np.radians(48.87))
    return np.hypot((lat2 - lat1) * 110.57, (lon2 - lon1) * kx)
