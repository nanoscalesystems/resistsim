"""Exposure: photoacid generation in a chemically amplified resist (thin-resist, 1D)."""
import numpy as np


def acid_fraction(intensity, dose, c):
    """Fraction of photoacid generator converted, h = 1 - exp(-C * dose * I(x)).

    intensity : normalized aerial image (clear field = 1)
    dose      : clear-field dose, mJ/cm^2
    c         : Dill C (exposure rate constant), cm^2/mJ
    """
    return 1.0 - np.exp(-c * dose * np.asarray(intensity))
