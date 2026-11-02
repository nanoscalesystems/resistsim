"""ILLUSTRATIVE, UNCALIBRATED: are the stochastic terms additive in quadrature?

For each dose, measures the roughness from each noise source alone and from all together (finite-rate
quenching, k_n = 10 nm^3/s, quencher diffusion 5 nm), and reports ALL divided by the quadrature sum
of the individual terms. A ratio near 1 means independent, additive noise (as in Naulleau and
Gallatin 2018); larger means the sources interact nonlinearly. 'events/PAG' is the mean number of
acid-generating events per pixel at the image maximum relative to the PAG pool (above 1 = pool-limited).
Runs both PAG-pool models: "hard" (acids capped at the pool size) and "smooth" (each event hits a
random PAG, so repeated hits are wasted). Diffusion lengths and chemistry are placeholders; read
trends, not numbers.
"""
from dataclasses import replace
import numpy as np
from resistsim import aerial_image_1d, Chemistry
from resistsim.stochastic import (NAULLEAU_CAR, photons_per_nm2, stochastic_deprotection,
                                  threshold_for_cd, edge_arrays, roughness)

dx, pitch, space, wl = 1.0, 44.0, 22.0, 13.5
x = np.arange(-pitch / 2, pitch / 2, dx)
img = aerial_image_1d(pitch, space, wl, 0.33, 0.6, x)
chem = Chemistry(c=0.0, ea_kcal=30.0, k_ref=0.05, diff_len_nm=5.0)
off = dict(random_photons=False, random_yield=False, random_pag=False, random_quencher=False)
single = {"photon": dict(random_photons=True), "yield": dict(random_yield=True),
          "PAG": dict(random_pag=True), "quencher": dict(random_quencher=True)}
allon = {k: True for k in off}


def swr(sto, dose):
    rng = np.random.default_rng(11)
    pilot = stochastic_deprotection(img, dx, wl, dose, sto, chem, 512, rng)
    th = threshold_for_cd(x, pilot.mean(axis=1), space)
    d = stochastic_deprotection(img, dx, wl, dose, sto, chem, 1024, rng)
    return roughness(*edge_arrays(x, d, th))["swr_3s"]


for pool in ("hard", "smooth"):
    print(f"\npool model: {pool}")
    print(f"{'dose':>5} {'events/PAG':>11} {'photon':>7} {'yield':>6} {'PAG':>5} {'quench':>7} {'quad':>6} {'ALL':>6} {'ALL/quad':>9}")
    for dose in (10.0, 20.0, 33.0, 60.0):
        base = replace(NAULLEAU_CAR, quencher_rate_nm3_s=10.0, quencher_diff_nm=5.0, pool=pool)
        sat = (photons_per_nm2(dose, wl) * base.absorbed_fraction * base.acids_per_photon * img.max()) / base.pag_per_nm2
        vals = [swr(replace(base, **{**off, **v}), dose) for v in single.values()]
        quad = float(np.sqrt(np.sum(np.square(vals))))
        total = swr(replace(base, **allon), dose)
        print(f"{dose:>5.0f} {sat:>11.2f} " + " ".join(f"{v:>6.2f}" for v in vals) + f" {quad:>6.2f} {total:>6.2f} {total / quad:>9.2f}")
