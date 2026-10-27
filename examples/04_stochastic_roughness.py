"""ILLUSTRATIVE, UNCALIBRATED: roughness versus dose from photon shot noise.

For each dose the development threshold is set so the mean CD equals the target, which is
equivalent to resists of different sensitivity (dose-to-size). All stochastic parameters,
diffusion lengths and the chemistry are placeholders; read the trend, not the numbers.
"""
import numpy as np
from resistsim import aerial_image_1d, Chemistry, Stochastic
from resistsim.stochastic import (mean_deprotection, stochastic_deprotection,
                                  threshold_for_cd, edge_arrays, roughness)

dx, pitch, space, wl = 1.0, 44.0, 22.0, 13.5
x = np.arange(-pitch / 2, pitch / 2, dx)
img = aerial_image_1d(pitch, space, wl, 0.33, 0.6, x)
chem = Chemistry(c=0.0, ea_kcal=30.0, k_ref=0.05, diff_len_nm=3.0)   # c unused here
sto = Stochastic()
rng = np.random.default_rng(7)

doses, lers = [10.0, 20.0, 40.0, 80.0], []
print(f"{'dose (mJ/cm2)':>14} {'mean CD':>8} {'LER 3s':>8} {'SWR 3s':>8} {'fail':>6}")
for dose in doses:
    th = threshold_for_cd(x, mean_deprotection(img, dx, wl, dose, sto, chem), space)
    d = stochastic_deprotection(img, dx, wl, dose, sto, chem, 1024, rng)
    left, right = edge_arrays(x, d, th)
    r = roughness(left, right)
    ler = 0.5 * (r["ler_left_3s"] + r["ler_right_3s"]); lers.append(ler)
    print(f"{dose:>14.0f} {r['mean_cd']:>8.2f} {ler:>8.2f} {r['swr_3s']:>8.2f} {r['fail_frac']:>6.2f}")
slope = np.polyfit(np.log(doses), np.log(lers), 1)[0]
print(f"\nlog-log slope of LER vs dose: {slope:.2f}  (pure shot noise would give about -0.5)")
