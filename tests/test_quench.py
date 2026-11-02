import numpy as np
from dataclasses import replace
from resistsim import peb_1d, peb_quench, Chemistry
from resistsim.bake import _neutralize
from resistsim.stochastic import NAULLEAU_CAR, stochastic_deprotection


def test_neutralize_conserves_difference_and_matches_limits():
    u, v = np.array([0.6, 0.2, 0.4, 0.0]), np.array([0.2, 0.6, 0.4, 0.3])
    u2, v2 = _neutralize(u, v, 0.5)
    assert np.allclose(u2 - v2, u - v)
    assert np.all(u2 >= 0) and np.all(v2 >= 0) and np.all(u2 <= u + 1e-12)
    u3, v3 = _neutralize(u, v, 1e4)                       # fast limit
    assert np.allclose(u3, np.clip(u - v, 0, None), atol=2e-4)   # equal u=v decays only as 1/(kt)
    assert np.allclose(_neutralize(np.array([0.4]), np.array([0.4]), 2.0)[0], 0.4 / (1 + 2.0 * 0.4))
    u4, _ = _neutralize(u, v, 1e-6)                       # slow limit
    assert np.allclose(u4, u - 1e-6 * u * v, atol=1e-9)


def test_fast_rate_matches_instant_subtraction():
    acid = np.linspace(0.05, 0.9, 40)
    q = 0.2
    fast = peb_quench(acid, np.full(40, q), 1.0, 60, 100, 30.0, 0.05, kappa_ref=1e4)
    inst = peb_1d(acid, 1.0, 60, 100, 30.0, 0.05, quencher=q)
    assert np.allclose(fast, inst, atol=1e-6)


def test_slow_rate_matches_no_quencher_and_deprotection_falls_with_rate():
    acid = np.linspace(0.05, 0.9, 40)
    q = np.full(40, 0.2)
    free = peb_1d(acid, 1.0, 60, 100, 30.0, 0.05)
    assert np.allclose(peb_quench(acid, q, 1.0, 60, 100, 30.0, 0.05, kappa_ref=1e-9), free, atol=1e-6)
    d = [peb_quench(acid, q, 1.0, 60, 100, 30.0, 0.05, kappa_ref=k).mean() for k in (0.0, 0.02, 0.2, 2.0)]
    assert d[0] > d[1] > d[2] > d[3]


def test_stochastic_finite_rate_runs_and_slower_rate_means_more_deprotection():
    img = np.ones(16)
    chem = Chemistry(c=0.0, ea_kcal=30.0, k_ref=0.05)
    out = {}
    for k in (0.1, 10.0):
        sto = replace(NAULLEAU_CAR, quencher_rate_nm3_s=k)
        d = stochastic_deprotection(img, 1.0, 13.5, 33.0, sto, chem, 64, np.random.default_rng(5))
        assert d.shape == (16, 64)
        out[k] = d.mean()
    assert out[0.1] > out[10.0]
