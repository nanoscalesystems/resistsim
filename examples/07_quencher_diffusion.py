"""ILLUSTRATIVE, UNCALIBRATED: does quencher mobility tame the quencher noise?

Finite-rate quenching (k_n = 10 nm^3/s, the Naulleau and Gallatin 2018 value) with the quencher
rms diffusion length over the bake swept from 0 (immobile, as Houle et al. 2004 assumed) upward.
Quencher mobility has no sourced value here: it is a sweep parameter. Chemistry and acid diffusion
are placeholders; read trends, not numbers.
"""
from dataclasses import replace
import numpy as np
from resistsim import aerial_image_1d, Chemistry
from resistsim.stochastic import (NAULLEAU_CAR, stochastic_deprotection, threshold_for_cd,
                                  edge_arrays, roughness)

dx, pitch, space, wl, dose = 1.0, 44.0, 22.0, 13.5, 33.0
x = np.arange(-pitch / 2, pitch / 2, dx)
img = aerial_image_1d(pitch, space, wl, 0.33, 0.6, x)
chem = Chemistry(c=0.0, ea_kcal=30.0, k_ref=0.05, diff_len_nm=5.0)
off = dict(random_photons=False, random_yield=False, random_pag=False, random_quencher=False)
terms = {"quencher only": dict(random_quencher=True),
         "ALL": dict(random_photons=True, random_yield=True, random_pag=True, random_quencher=True)}

print(f"{'quencher diff (nm)':>19} {'term':>14} {'mean CD':>8} {'SWR 3s':>8}")
for qd in (0.0, 3.0, 6.0, 10.0):
    for name, on in terms.items():
        sto = replace(NAULLEAU_CAR, quencher_rate_nm3_s=10.0, quencher_diff_nm=qd, **{**off, **on})
        rng = np.random.default_rng(11)
        pilot = stochastic_deprotection(img, dx, wl, dose, sto, chem, 512, rng)
        th = threshold_for_cd(x, pilot.mean(axis=1), space)
        d = stochastic_deprotection(img, dx, wl, dose, sto, chem, 1024, rng)
        r = roughness(*edge_arrays(x, d, th))
        print(f"{qd:>19g} {name:>14} {r['mean_cd']:>8.2f} {r['swr_3s']:>8.2f}")
