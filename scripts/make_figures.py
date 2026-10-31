"""Generate the figures used on the Nanoscale Systems resistsim page.

Run from the repo root:  python scripts/make_figures.py
Writes PNGs to docs/figures/. Everything here is ILLUSTRATIVE and UNCALIBRATED (see README).
"""
import os
from dataclasses import replace
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from resistsim import aerial_image_1d, nils, Optics, Chemistry, fem, process_window
from resistsim.stochastic import (NAULLEAU_CAR, Stochastic, stochastic_deprotection, threshold_for_cd,
                                  edge_arrays, roughness)

OUT = "docs/figures"
os.makedirs(OUT, exist_ok=True)
BG, TXT, CYAN, GRID, MUTED = "#0c1219", "#dbe6ee", "#22d3ee", "#1b2733", "#8296a6"
plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
                     "text.color": TXT, "axes.labelcolor": TXT, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.edgecolor": GRID, "grid.color": GRID, "axes.grid": True, "font.size": 11,
                     "legend.frameon": False, "axes.spines.top": False, "axes.spines.right": False})
SHADES = [CYAN, "#67e8f9", "#a5f3fc"]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(f"{OUT}/{name}.png", dpi=160)
    plt.close(fig)
    print("wrote", f"{OUT}/{name}.png")


# 1. aerial image through focus -------------------------------------------------------------
EUV = dict(wavelength=13.5, na=0.33)
P = dict(pitch=44, space=22, sigma_out=0.6)
x = np.linspace(-44, 44, 881)
fig, ax = plt.subplots(figsize=(7, 3.8))
for z, c in zip((0, 50, 100), SHADES):
    ax.plot(x, aerial_image_1d(x=x, defocus=z, **P, **EUV), color=c, lw=2,
            label=f"defocus {z} nm (NILS {nils(**P, **EUV, defocus=z):.1f})")
ax.set(xlabel="position (nm)", ylabel="relative intensity",
       title="Aerial image, 22 nm lines and spaces, 13.5 nm, NA 0.33")
ax.legend()
save(fig, "01_aerial_image")

# 2. exposure latitude versus acid diffusion length -----------------------------------------
o = Optics(wavelength=13.5, na=0.33, sigma_out=0.6, pitch=44, space=22)
doses, defoci = np.linspace(15, 40, 51), np.arange(-200, 201, 10.0)
Ls, els = (0.0, 3.0, 6.0, 9.0), []
for L in Ls:
    cd = fem(o, Chemistry(c=0.05, ea_kcal=30.0, k_ref=0.05, diff_len_nm=L), doses, defoci)
    els.append(process_window(cd, doses, defoci, 22.0)["el_pct"])
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.bar([f"{L:g}" for L in Ls], els, color=CYAN, width=0.55)
ax.set(xlabel="acid diffusion length (nm, sweep parameter)", ylabel="exposure latitude (%)",
       title="More acid blur, less process margin")
save(fig, "02_exposure_latitude")

# 3. roughness versus dose ------------------------------------------------------------------
dx, pitch, space, wl = 1.0, 44.0, 22.0, 13.5
xs = np.arange(-pitch / 2, pitch / 2, dx)
img = aerial_image_1d(pitch, space, wl, 0.33, 0.6, xs)
chem = Chemistry(c=0.0, ea_kcal=30.0, k_ref=0.05, diff_len_nm=3.0)
rng = np.random.default_rng(7)
dl, lers = [10.0, 20.0, 40.0, 80.0], []
for dose in dl:
    pilot = stochastic_deprotection(img, dx, wl, dose, Stochastic(), chem, 512, rng)
    th = threshold_for_cd(xs, pilot.mean(axis=1), space)
    d = stochastic_deprotection(img, dx, wl, dose, Stochastic(), chem, 1024, rng)
    r = roughness(*edge_arrays(xs, d, th))
    lers.append(0.5 * (r["ler_left_3s"] + r["ler_right_3s"]))
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.loglog(dl, lers, "o-", color=CYAN, lw=2, label="simulated LER (3 sigma)")
ax.loglog(dl, lers[0] * (np.array(dl) / dl[0]) ** -0.5, "--", color=MUTED, label="pure shot-noise slope (-0.5)")
ax.set(xlabel="dose (mJ/cm$^2$)", ylabel="line-edge roughness (nm)", title="Photon shot noise lowers roughness with dose")
ax.legend()
save(fig, "03_roughness_vs_dose")

# 4. which noise source dominates -----------------------------------------------------------
off = dict(random_photons=False, random_yield=False, random_pag=False, random_quencher=False)
cases = {"photon": dict(random_photons=True), "acid yield": dict(random_yield=True),
         "PAG count": dict(random_pag=True), "quencher\ncount": dict(random_quencher=True),
         "all\ntogether": {k: True for k in off}}
chem5 = Chemistry(c=0.0, ea_kcal=30.0, k_ref=0.05, diff_len_nm=5.0)
vals = []
for on in cases.values():
    sto = replace(NAULLEAU_CAR, **{**off, **on})
    rng = np.random.default_rng(11)
    pilot = stochastic_deprotection(img, dx, wl, 33.0, sto, chem5, 512, rng)
    th = threshold_for_cd(xs, pilot.mean(axis=1), space)
    d = stochastic_deprotection(img, dx, wl, 33.0, sto, chem5, 1024, rng)
    vals.append(roughness(*edge_arrays(xs, d, th))["swr_3s"])
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.bar(list(cases), vals, color=[CYAN] * 4 + ["#a5f3fc"], width=0.55)
ax.set(ylabel="space-width roughness, 3 sigma (nm)", title="Which source of randomness limits roughness")
save(fig, "04_noise_terms")
