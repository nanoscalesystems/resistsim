"""ILLUSTRATIVE, UNCALIBRATED: finite-rate acid-quencher reaction versus instant quenching.

Sweeps the neutralization rate constant k_n (nm^3/s) over the range anchored by Houle et al. 2004
(measured TBAH about 0.1 nm^3/s at 85 C, diffusion-limited estimate about 2.5 nm^3/s) up to the
10 nm^3/s of Naulleau and Gallatin 2018, and compares with instant quenching. Quencher count noise
only, and all noise terms together. Quencher diffusion is zero (immobile, as assumed by Houle).
Chemistry and diffusion length are placeholders; read trends, not numbers.
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

print(f"{'k_n (nm3/s)':>12} {'term':>14} {'mean CD':>8} {'SWR 3s':>8}")
for k in (None, 0.1, 1.0, 10.0):
    for name, on in terms.items():
        sto = replace(NAULLEAU_CAR, quencher_rate_nm3_s=k, **{**off, **on})
        rng = np.random.default_rng(11)
        pilot = stochastic_deprotection(img, dx, wl, dose, sto, chem, 512, rng)
        th = threshold_for_cd(x, pilot.mean(axis=1), space)
        d = stochastic_deprotection(img, dx, wl, dose, sto, chem, 1024, rng)
        r = roughness(*edge_arrays(x, d, th))
        label = "instant" if k is None else f"{k:g}"
        print(f"{label:>12} {name:>14} {r['mean_cd']:>8.2f} {r['swr_3s']:>8.2f}")
