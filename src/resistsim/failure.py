"""Stochastic printing failures from voxel-scale statistics (after Hinsberg et al., JM3 20, 014603, 2021).

A positive-tone line/space pattern fails locally in two ways:
  bridge : the voxel at the SPACE centre stays insoluble (deprotection below threshold), so resist
           bridges the space;
  break  : the voxel at the LINE centre becomes soluble (deprotection at or above threshold), so the
           line breaks.
Voxels are averaged windows of `voxel_nm` (Hinsberg uses a 15 nm characteristic length). The failure
probabilities are estimated by counting over a simulated field, so rates far below 1/(number of
voxels) cannot be resolved: use the Wilson interval to see the resolution limit.
"""
import numpy as np


def voxel_average(d2d, ic, dx, voxel_nm):
    """Voxel-averaged deprotection at x index `ic` (periodic in x): a 1D array, one value per voxel along y."""
    nx, ny = d2d.shape
    w = max(1, int(round(voxel_nm / dx)))
    idx = (np.arange(w) - w // 2 + ic) % nx
    col = d2d[idx, :].mean(axis=0)
    m = (ny // w) * w
    return col[:m].reshape(-1, w).mean(axis=1)


def wilson_interval(k, n, z=1.96):
    """Wilson score interval for a proportion k/n."""
    if n <= 0:
        return (np.nan, np.nan)
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def count_failures(x, d2d, dx, d_th, voxel_nm=15.0):
    """Count bridge and break voxels. Space centre is at x = 0; the line centre is half a period away."""
    ic_space = int(np.argmin(np.abs(x)))
    ic_line = (ic_space + d2d.shape[0] // 2) % d2d.shape[0]
    space_v = voxel_average(d2d, ic_space, dx, voxel_nm)
    line_v = voxel_average(d2d, ic_line, dx, voxel_nm)
    n = len(space_v)
    k_bridge = int(np.sum(space_v < d_th))
    k_break = int(np.sum(line_v >= d_th))
    s_sd, l_sd = float(np.std(space_v, ddof=1)), float(np.std(line_v, ddof=1))
    margin = lambda gap, sd: gap / sd if sd > 0 else np.inf
    return {"n_voxels": n,
            "bridge": k_bridge / n, "bridge_ci": wilson_interval(k_bridge, n),
            "break": k_break / n, "break_ci": wilson_interval(k_break, n),
            # distance of the voxel mean from the threshold in standard deviations (indicative only:
            # the real tails are not Gaussian, so do not convert these into rates)
            "z_bridge": margin(float(space_v.mean()) - d_th, s_sd),
            "z_break": margin(d_th - float(line_v.mean()), l_sd)}
