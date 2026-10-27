"""ILLUSTRATIVE, UNCALIBRATED: which stochastic term limits roughness?

Switches on one source of randomness at a time (photons, acid yield, PAG count, quencher
count) and then all together, at a fixed target CD, using the Naulleau et al. (2026) Table 1
CAR inputs. Their paper reports LWR for 16 nm lines/spaces with aerial-image parameters not
given there, so only the RANKING of terms is comparable, not the absolute values.
Diffusion length and the chemistry are placeholders.
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

cases = {"photon": dict(random_photons=True), "acid yield": dict(random_yield=True),
         "PAG count": dict(random_pag=True), "quencher count": dict(random_quencher=True),
         "ALL": dict(random_photons=True, random_yield=True, random_pag=True, random_quencher=True)}
print(f"{'term':>15} {'mean CD':>8} {'SWR 3s':>8}")
for name, on in cases.items():
    sto = replace(NAULLEAU_CAR, **{**off, **on})
    rng = np.random.default_rng(11)
    pilot = stochastic_deprotection(img, dx, wl, dose, sto, chem, 512, rng)
    th = threshold_for_cd(x, pilot.mean(axis=1), space)
    d = stochastic_deprotection(img, dx, wl, dose, sto, chem, 1024, rng)
    r = roughness(*edge_arrays(x, d, th))
    print(f"{name:>15} {r['mean_cd']:>8.2f} {r['swr_3s']:>8.2f}")
