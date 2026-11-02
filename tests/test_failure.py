import numpy as np
from resistsim.failure import voxel_average, wilson_interval, count_failures


def _field(nx=44, ny=300, space=0.95, line=0.05):
    x = np.arange(-nx / 2, nx / 2, 1.0)
    d = np.full((nx, ny), line)
    d[np.abs(x) < 8, :] = space                      # soluble space around x = 0
    return x, d


def test_clean_field_has_no_failures():
    x, d = _field()
    out = count_failures(x, d, 1.0, d_th=0.8, voxel_nm=15)
    assert out["n_voxels"] == 20 and out["bridge"] == 0 and out["break"] == 0
    assert out["z_bridge"] == np.inf and out["z_break"] == np.inf         # no spread: infinite margin


def test_margins_are_positive_for_noisy_but_healthy_field_and_respond_to_threshold():
    x, d = _field(ny=3000)
    d = d + np.random.default_rng(0).normal(0, 0.05, d.shape)
    lo = count_failures(x, d, 1.0, d_th=0.5, voxel_nm=15)
    hi = count_failures(x, d, 1.0, d_th=0.8, voxel_nm=15)
    assert lo["z_bridge"] > hi["z_bridge"] > 0 and hi["z_break"] > lo["z_break"] > 0


def test_injected_failures_are_counted_and_periodic_wrap_works():
    x, d = _field()
    d[18:26, 0:15] = 0.1          # block at the space centre (x = -4..3) for the first voxel row -> bridge
    d[0:8, 30:45] = 0.95          # line centre sits at x = -22 (index 0): the 15-wide window wraps
    d[37:44, 30:45] = 0.95        # across the period edge (indices 37..43 and 0..7)
    out = count_failures(x, d, 1.0, d_th=0.8, voxel_nm=15)
    assert out["bridge"] == 1 / 20 and out["break"] == 1 / 20


def test_voxel_average_is_a_mean_over_the_window():
    d = np.zeros((10, 6)); d[4:7, :] = 1.0
    v = voxel_average(d, 5, 1.0, 3.0)
    assert v.shape == (2,) and np.allclose(v, 1.0)


def test_wilson_interval_limits():
    lo, hi = wilson_interval(0, 100)
    assert lo == 0.0 and 0.03 < hi < 0.05                 # about 3.7% for zero events in 100
    lo, hi = wilson_interval(50, 100)
    assert lo < 0.5 < hi and hi - lo < 0.21
