"""ILLUSTRATIVE, UNCALIBRATED: bridge and break failure rates versus dose.

The development threshold is fixed at the value that gives the target CD at the reference dose
(a stand-in for a real resist's fixed solubility threshold), then the dose is varied: more dose
trades bridges for breaks. Rates are voxel counts with 95% Wilson intervals, so anything below
about 1/(number of voxels) is unresolved; the z columns give the distance of the voxel mean from the
threshold in standard deviations, a trend indicator beyond that resolution (not a rate). Smooth PAG
pool, finite-rate quenching (k_n = 10 nm^3/s, quencher diffusion 5 nm), 15 nm voxels. All chemistry
and diffusion values are placeholders; read trends, not numbers.
"""
from dataclasses import replace
import numpy as np
from resistsim import aerial_image_1d, Chemistry
from resistsim.failure import count_failures
from resistsim.stochastic import NAULLEAU_CAR, stochastic_deprotection, threshold_for_cd

dx, pitch, space, wl = 1.0, 44.0, 22.0, 13.5
x = np.arange(-pitch / 2, pitch / 2, dx)
img = aerial_image_1d(pitch, space, wl, 0.33, 0.6, x)
chem = Chemistry(c=0.0, ea_kcal=30.0, k_ref=0.05, diff_len_nm=5.0)
sto = replace(NAULLEAU_CAR, pool="smooth", quencher_rate_nm3_s=10.0, quencher_diff_nm=5.0)
rng = np.random.default_rng(21)

ref_dose = 33.0
pilot = stochastic_deprotection(img, dx, wl, ref_dose, sto, chem, 1024, rng)
d_th = threshold_for_cd(x, pilot.mean(axis=1), space)
print(f"development threshold (fixed): {d_th:.3f}\n")

fmt = lambda p, ci: f"{p:7.4f} [{ci[0]:.4f}, {ci[1]:.4f}]"
print(f"{'dose':>5} {'voxels':>7} {'bridge  [95% CI]':>26} {'break  [95% CI]':>26} {'z_bridge':>9} {'z_break':>8}")
for dose in (20.0, 27.0, 33.0, 45.0, 60.0, 90.0, 130.0):
    d = stochastic_deprotection(img, dx, wl, dose, sto, chem, 6144, rng)
    r = count_failures(x, d, dx, d_th, voxel_nm=15.0)
    print(f"{dose:>5.0f} {r['n_voxels']:>7} {fmt(r['bridge'], r['bridge_ci']):>26} {fmt(r['break'], r['break_ci']):>26} {r['z_bridge']:>9.2f} {r['z_break']:>8.2f}")
