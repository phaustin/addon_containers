import numpy as np


def UpdateAlbedo(x, Albedo):
    # define a function which updates the planetary albedo of the state vector (last entry)
    # Note that the state vector x is assumed to be a python dictionary
    # weighted sum of different planet cover
    x["Ap"] = Albedo["none"] * x["Su"] + Albedo["w"] * x["Sw"] + Albedo["b"] * x["Sb"]
    return x


def UpdateTemp(x, F, rat, em_p, sig, ins_p, Albedo):
    # function to update the state vector for the planetary temperature

    # outward flux of a planet with the average albedo (assume Black body)
    Fp = F * (1 - x["Ap"]) * rat / em_p

    # invert Stefan Boltzmann's law
    x["Tp"] = np.sqrt(np.sqrt((Fp / sig)))

    # now do the same for the regions with white and black daisies
    Fw = F * (1 - Albedo["w"]) * rat / em_p
    x["Tw"] = np.sqrt(np.sqrt((ins_p * (Fw - Fp) + Fp) / sig))

    # now do the same for the regions with white and black daisies
    Fb = F * (1 - Albedo["b"]) * rat / em_p
    x["Tb"] = np.sqrt(np.sqrt((ins_p * (Fb - Fp) + Fp) / sig))
    return x


def DaisyGrowth(T, bwtype, T_min, T_opt):
    Gw = 1 - ((T - T_opt[bwtype]) / (T_min[bwtype] - T_opt[bwtype])) ** 2
    # set negative values to 0
    if Gw < 0:
        return 0
    else:
        return Gw


# function to update areas based on growth rate and death rate
def UpdateAreas(x, death, minarea, T_min, T_opt):

    for Stype in ["w", "b"]:
        grwth = DaisyGrowth(x["T" + Stype], Stype, T_min, T_opt)
        ArType = "S" + Stype
        Ds = x[ArType] * (grwth * x["Su"] - death[Stype])
        # the following code applies 2 checks
        # (1) keep the area to zero if it has been
        # articifically set to exactly zero
        if x[ArType] > 0:
            x[ArType] += Ds
            # (2) apply the minimum area if the area comes below the threshold
            if x[ArType] < minarea:
                x[ArType] = minarea

    # update barren area (that what is left)
    x["Su"] = 1 - x["Sw"] - x["Sb"]


def NextState(x, F, rat, em_p, sig, ins_p, Albedo, death, minarea, T_min, T_opt):
    # make a copy of the previous statevector to work on
    xnew = x.copy()
    UpdateTemp(xnew, F, rat, em_p, sig, ins_p, Albedo)
    UpdateAreas(xnew, death, minarea, T_min, T_opt)
    UpdateAlbedo(xnew, Albedo)
    return xnew


# To aid this exercise write and additional function which updates
# the state vector until  no noticable change in temperature is happening
def Equi_state(x0, F, rat, em_p, sig, ins_p, Albedo, death, minarea, T_min, T_opt):
    dT = 2
    x = x0.copy()
    temp = x["Tp"]
    while dT > 0.05:
        x = NextState(x, F, rat, em_p, sig, ins_p, Albedo, death, minarea, T_min, T_opt)
        dT = abs(temp - x["Tp"])
        temp = x["Tp"]
    return x


def update_equi_flux(
    Fsnom, Albedo, rat, em_p, sig, ins_p, death, minarea, T_min, T_opt
):
    # Experiment 2 Planet response to varying solar flux

    # set up variation of solar radiation
    nt = 200
    # amount of steps
    Fracmin = 0.6
    Fracmax = 1.65
    dF = (Fracmax - Fracmin) / nt
    F = [dF * i + Fracmin for i in range(nt)]

    # set up initial condition
    # initial condition state vector
    x0 = {}
    x0["Sw"] = 0.01
    x0["Sb"] = 0.01
    # compute barren area automatically
    x0["Su"] = 1 - x0["Sw"] - x0["Sb"]

    # note that we also need to initiate the planetary Albedo
    UpdateAlbedo(x0, Albedo)
    # and the temperature
    UpdateTemp(x0, F[0] * Fsnom, rat, em_p, sig, ins_p, Albedo)

    # initial condition for a barren planet
    x0bar = {}
    x0bar["Sw"] = 0
    x0bar["Sb"] = 0
    x0bar["Su"] = 1
    # note that we also need to set the planetary Albedo
    UpdateAlbedo(x0bar, Albedo)
    # and the temperature
    UpdateTemp(x0bar, F[0] * Fsnom, rat, em_p, sig, ins_p, Albedo)

    # loop over radiation variation
    xeq = []
    xeq.append(x0)
    xeqbar = []
    xeqbar.append(x0bar)

    for Fr in F[1:]:
        xeq.append(
            Equi_state(
                xeq[-1],
                Fr * Fsnom,
                rat,
                em_p,
                sig,
                ins_p,
                Albedo,
                death,
                minarea,
                T_min,
                T_opt,
            )
        )
        xeqbar.append(
            Equi_state(
                xeqbar[-1],
                Fr * Fsnom,
                rat,
                em_p,
                sig,
                ins_p,
                Albedo,
                death,
                minarea,
                T_min,
                T_opt,
            )
        )

    # also run the  experiment backwards
    # (use the end value of the forward run as starting point)
    xeqinv = []
    xeqinv.append(xeq[-1])

    for Fr in F[::-1]:
        xeqinv.append(
            Equi_state(
                xeqinv[-1],
                Fr * Fsnom,
                rat,
                em_p,
                sig,
                ins_p,
                Albedo,
                death,
                minarea,
                T_min,
                T_opt,
            )
        )

    # reverse the vector
    xeqinv = xeqinv[::-1][1:]

    return (xeq, xeqbar, xeqinv, F)


def update_constant_flux(
    Fsnom, Albedo, rat, em_p, sig, ins_p, death, minarea, T_min, T_opt, areas
):
    # First experiment
    F = Fsnom * 1  # solar radiation

    # initial condition state vector
    x0 = {}
    x0["Sw"] = areas["w"]
    x0["Sb"] = areas["b"]
    x0["Su"] = 1 - x0["Sw"] - x0["Sb"]
    # note that we also need to initiate the planetary Albedo
    UpdateAlbedo(x0, Albedo)
    # and the temperature
    UpdateTemp(x0, F, rat, em_p, sig, ins_p, Albedo)

    # loop over generations
    ngen = 40

    xgens = []
    xgens.append(x0)
    for g in range(ngen - 1):
        xgens.append(
            NextState(
                xgens[-1],
                F,
                rat,
                em_p,
                sig,
                ins_p,
                Albedo,
                death,
                minarea,
                T_min,
                T_opt,
            )
        )

    gens = [i for i in range(ngen)]

    return xgens, gens


def update_solar_constant(solar_distance):
    luminosity = 10e26
    # nominal flux in W/m^2
    F = luminosity / (4 * np.pi * (solar_distance ** 2))
    return F


def toAU(distance):
    return distance / 1.496e11


def fromAU(distance):
    return distance * 1.496e11
