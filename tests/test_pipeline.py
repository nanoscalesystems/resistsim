import numpy as np
from resistsim.pipeline import Optics, Chemistry, space_cd, fem
from resistsim.process_window import process_window


def test_space_cd_triangle():
    x = np.arange(-22, 22, 0.05); w = 10.0
    d = np.clip(1 - np.abs(x) / w, 0, None)
    assert np.isclose(space_cd(x, d, 0.5), 2 * w * 0.5, atol=0.1)


def test_space_cd_limits():
    x = np.arange(-22, 22, 0.25)
    assert space_cd(x, np.zeros_like(x), 0.5) == 0.0
    assert space_cd(x, np.ones_like(x), 0.5) >= 44.0


def test_cd_grows_with_dose():
    o = Optics(13.5, 0.33, 0.6, 44, 22)
    ch = Chemistry(c=0.05, ea_kcal=30.0, k_ref=0.05)
    cd = fem(o, ch, doses=[20, 30, 40, 50], defoci=[0.0])[:, 0]
    assert np.all(np.diff(cd) >= 0) and cd[-1] > cd[0]


def test_process_window_metrics():
    doses = np.array([10., 20., 30., 40., 50.]); defoci = np.array([-20., 0., 20.])
    cd = np.array([[10, 12, 10], [21, 22, 21], [22, 22, 22], [23, 22, 23], [30, 32, 30]], float)
    pw = process_window(cd, doses, defoci, target=22.0, tol=0.10)
    assert pw["dof_nm"] == 40.0 and np.isclose(pw["el_pct"], 100 * 20 / 30)
