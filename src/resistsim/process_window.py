"""Process-window metrics from a focus-exposure matrix (sampled spans, so lower bounds)."""
import numpy as np


def _longest_run(mask):
    best = cur = 0
    for v in mask:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def process_window(cd, doses, defoci, target, tol=0.10):
    """DOF and exposure latitude where |CD - target| <= tol * target.

    Returns dict: in_spec (bool matrix), dof_nm (largest focus span at any dose),
    best_dose, el_pct (contiguous dose span at nominal focus, as % of its mid dose).
    """
    doses, defoci = np.asarray(doses, float), np.asarray(defoci, float)
    ok = np.abs(cd - target) <= tol * target
    dz = defoci[1] - defoci[0]
    runs = [_longest_run(ok[i, :]) for i in range(len(doses))]
    i_best = int(np.argmax(runs))
    dof = max(runs[i_best] - 1, 0) * dz
    j_best = int(np.argmin(np.abs(defoci)))              # nominal focus
    col = ok[:, j_best]
    el = 0.0
    if _longest_run(col) > 1:
        start = best = cur = 0
        for i, v in enumerate(col):
            cur = cur + 1 if v else 0
            if cur > best:
                best, start = cur, i - cur + 1
        lo, hi = doses[start], doses[start + best - 1]
        el = 100.0 * (hi - lo) / (0.5 * (hi + lo))
    return {"in_spec": ok, "dof_nm": float(dof), "best_dose": float(doses[i_best]), "el_pct": float(el)}
