"""ILLUSTRATIVE, UNCALIBRATED: effect of acid diffusion length on the process window.

Generic EUV-like optics and placeholder chemistry. Diffusion length is an unsourced sweep
parameter. Do not read the numbers as predictions for any real resist.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from resistsim.pipeline import Optics, Chemistry, fem
from resistsim.process_window import process_window

o = Optics(wavelength=13.5, na=0.33, sigma_out=0.6, pitch=44, space=22)
doses = np.linspace(15, 40, 51)
defoci = np.arange(-200, 201, 10.0)
target = 22.0

fig, ax = plt.subplots(figsize=(6, 4))
print(f"{'diff. length (nm)':>18} {'dose@target (a.u.)':>20} {'EL (%)':>8} {'DOF (nm)':>9}")
for L in (0.0, 3.0, 6.0, 9.0):
    ch = Chemistry(c=0.05, ea_kcal=30.0, k_ref=0.05, diff_len_nm=L)
    cd = fem(o, ch, doses, defoci)
    pw = process_window(cd, doses, defoci, target)
    j0 = len(defoci) // 2
    d_t = np.interp(target, cd[:, j0], doses) if np.all(np.diff(cd[:, j0]) >= 0) else float("nan")
    print(f"{L:>18.1f} {d_t:>20.1f} {pw['el_pct']:>8.1f} {pw['dof_nm']:>9.0f}")
    ax.plot(defoci, cd[np.argmin(np.abs(doses - d_t)) if d_t == d_t else 0, :], label=f"L = {L:g} nm")
ax.axhspan(0.9 * target, 1.1 * target, color="grey", alpha=0.2)
ax.set(xlabel="defocus (nm)", ylabel="space CD (nm)", title="Through-focus CD at target dose (uncalibrated)")
ax.legend(); fig.tight_layout(); fig.savefig("examples/process_window.png", dpi=150)
