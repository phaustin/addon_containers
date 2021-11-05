# This is the file where all the calculations are done. This file is called by app.py.

import numpy as np

g = 9.81  # gravitational acceleration in m/s^2
beta = 4.40 * 10 ** (-10)  # water compressibility in m^2/N

# all arrays are in order: Clay, Sand, Gravel, Jointed Rock, Sound Rock


def alpha(inp_alpha):
    # convert alpha from a qualitative value to a quantitative.
    if inp_alpha == "min":
        a = np.array(
            [(10 ** (-8)), (10 ** (-9)), (10 ** (-10)), (10 ** (-10)), (10 ** (-11))]
        )
    elif inp_alpha == "avg":
        a = np.array(
            [(10 ** (-7)), (10 ** (-8)), (10 ** (-9)), (10 ** (-8)), (10 ** (-10))]
        )
    elif inp_alpha == "max":
        a = np.array(
            [(10 ** (-6)), (10 ** (-7)), (10 ** (-8)), (10 ** (-8)), (10 ** (-9))]
        )
    return a  # m^2/N


def porosity(inp_porosity):
    # Clay: 0.45, 0.5, 0.55
    # Sand: 0.26, 0.38, 0.5
    # Gravel: 0.25, 0.3, 0.35
    # Jointed: 0.05, 0.175, 0.30 #using values for fractured basalt
    # Sound: 0.0001, 0.015, 0.03 #using values for fresh granite and gneiss
    if inp_porosity == "min":
        p = np.array([0.45, 0.26, 0.25, 0.05, 0.0001])
    elif inp_porosity == "mid":
        p = np.array([0.5, 0.38, 0.3, 0.175, 0.015])
    elif inp_porosity == "max":
        p = np.array([0.55, 0.5, 0.35, 0.3, 0.03])
    return p  # dimensionless


def density(inp_density):
    # sea water: 1.025kg/L
    # brine: 1088
    if inp_density == "potable":
        d = 1000
    elif inp_density == "sea_water":
        d = 1025
    elif inp_density == "brine":
        d = 1088
    return d  # kg/m^3


def specific_storage(alpha, porosity, density):
    Ss = density * g * (alpha + porosity * beta)
    return Ss  # m^-1


def storativity_aquifer_compressibility(density):
    Sa = density * g * beta
    return Sa  # dimensionless


def storativity_water_compressibility(porosity, density, thickness):
    Sw = density * g * (porosity * beta) * thickness
    return Sw  # dimensionless


def storativity(alpha, porosity, density, thickness):
    S = specific_storage(alpha, porosity, density) * thickness
    return S
