import numpy as np
from dataclasses import replace
from resistsim.stochastic import Stochastic, generate_acids, photons_per_nm2

OFF = dict(random_photons=False, random_yield=False, random_pag=False, random_quencher=False, blur_nm=0.0)


def test_smooth_pool_mean_field_is_below_hard_cap_and_has_right_limits():
    img = np.array([0.02, 0.3, 1.0, 3.0, 10.0])
    sto = Stochastic(pag_per_nm2=7.0, acids_per_photon=2.8, absorbed_fraction=0.14, pool="smooth", **OFF)
    hard = replace(sto, pool="hard")
    rng = np.random.default_rng(0)
    hs = generate_acids(img, 1.0, 13.5, 33.0, sto, 3, rng)[:, 0]
    hh = generate_acids(img, 1.0, 13.5, 33.0, hard, 3, rng)[:, 0]
    assert np.all(hs <= hh + 1e-12) and np.all(hs < 1.0)
    events = photons_per_nm2(33.0, 13.5) * 0.14 * 2.8 * img
    assert np.isclose(hs[0], 1 - np.exp(-events[0] / 7.0), rtol=1e-6)     # low dose: ~ events/pool
    assert hs[-1] > 0.99                                                   # high dose: pool full


def test_smooth_pool_binomial_mean_matches_poisson_generating_function():
    m, n = 3.0, 7.0
    sto = Stochastic(pag_per_nm2=n, acids_per_photon=1.0, absorbed_fraction=1.0, pool="smooth",
                     random_photons=False, random_yield=True, random_pag=False, random_quencher=False,
                     blur_nm=0.0)
    dose = m / photons_per_nm2(1.0, 13.5)                                  # gives m photons per pixel
    h = generate_acids(np.ones(4), 1.0, 13.5, dose, sto, 40000, np.random.default_rng(1))
    expected = (1 - np.exp(m * (np.exp(-1 / n) - 1)))                      # E[1 - exp(-E/N)], E ~ Poisson(m)
    assert np.isclose(h.mean(), expected, rtol=0.02)


def test_smooth_pool_deterministic_when_nothing_is_random_and_bounded():
    sto = Stochastic(pag_per_nm2=5.0, pool="smooth", **OFF)
    h = generate_acids(np.linspace(0.1, 3, 6), 1.0, 13.5, 60.0, sto, 20, np.random.default_rng(2))
    assert np.allclose(h, h[:, :1])
    noisy = replace(sto, random_yield=True, random_photons=True)
    hn = generate_acids(np.ones(4), 1.0, 13.5, 200.0, noisy, 500, np.random.default_rng(3))
    assert hn.max() <= 1.0 + 1e-12
