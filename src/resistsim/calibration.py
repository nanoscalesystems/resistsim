"""Calibration of effective deprotection rates against dose-to-clear (E0) data.

Assumptions (all placeholders unless sourced): Dill C, quencher loading and the
deprotection extent at which the film clears. Rates are fitted so that each
(resist, PAG) pair reproduces its own measured E0 at its measured PEB.
"""
import numpy as np
from .bake import arrhenius_scale, R_KCAL


def apparent_ea(e0_a, temp_a_c, e0_b, temp_b_c):
    """Apparent activation energy (kcal/mol) from E0 at two PEB temperatures.

    Low-conversion limit, where E0 is proportional to 1/k(T).
    """
    ta, tb = temp_a_c + 273.15, temp_b_c + 273.15
    return R_KCAL * np.log(e0_a / e0_b) / (1 / ta - 1 / tb)


def fit_k_ref(e0, temp_c, ea_kcal, c=0.05, quencher=0.10, d_clear=0.5,
              time_s=60.0, ref_temp_c=100.0):
    """Effective deprotection rate k_ref (1/s, per unit acid fraction, at ref_temp_c).

    Open-frame model: acid = 1 - exp(-c*E0) - quencher; film clears when
    1 - exp(-k_eff * acid * time) = d_clear.
    """
    acid = 1.0 - np.exp(-c * e0) - quencher
    if acid <= 0:
        raise ValueError("acid at E0 does not exceed the quencher loading; adjust c or quencher")
    k_eff = -np.log(1.0 - d_clear) / (acid * time_s)
    return k_eff / arrhenius_scale(ea_kcal, temp_c, ref_temp_c)
