import numpy as np
from resistsim.bake import arrhenius_scale, diffuse_periodic, peb_1d, R_KCAL
from resistsim.registry import RESISTS, PAGS, E0_TABLE


def test_arrhenius_ratio():
    r = arrhenius_scale(33.5, 100, 90)
    assert np.isclose(r, np.exp(33.5 / R_KCAL * (1 / 363.15 - 1 / 373.15)))
    assert r > 1 and arrhenius_scale(33.5, 100, 100) == 1


def test_uniform_acid_matches_analytic():
    a = np.full(64, 0.3)
    p = peb_1d(a, 1.0, 60, 100, 30.0, k_ref=0.02, diff_len_nm=5.0)
    assert np.allclose(p, 1 - np.exp(-0.02 * 0.3 * 60))


def test_diffusion_conserves_mean_and_matches_gaussian_decay():
    x = np.arange(0, 44, 0.25); lam, L = 44.0, 6.0
    f = 1 + 0.5 * np.cos(2 * np.pi * x / lam)
    g = diffuse_periodic(f, 0.25, L)
    assert np.isclose(g.mean(), f.mean())
    amp = (g.max() - g.min()) / (f.max() - f.min())
    assert np.isclose(amp, np.exp(-2 * np.pi**2 * L**2 / lam**2), rtol=1e-3)


def test_quencher_blocks_subthreshold_acid():
    a = np.array([0.05, 0.05, 0.4, 0.4])
    p = peb_1d(a, 1.0, 60, 100, 30.0, k_ref=0.05, quencher=0.1)
    assert p[0] == 0 and p[2] > 0


def test_more_diffusion_lowers_deprotection_contrast():
    x = np.arange(0, 44, 0.25)
    a = 0.4 * (1 + np.cos(2 * np.pi * x / 44)) / 2
    c = [np.ptp(peb_1d(a, 0.25, 60, 100, 30.0, 0.05, diff_len_nm=L)) for L in (0, 5, 10)]
    assert c[0] > c[1] > c[2]


def test_registry_is_consistent():
    assert all(r in RESISTS and p in PAGS for r, p, _, _ in E0_TABLE)
    assert all(v.status in {"literature", "estimated", "measured"} for v in list(RESISTS.values()) + list(PAGS.values()))
