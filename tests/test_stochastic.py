import numpy as np
from resistsim import aerial_image_1d, Chemistry
from resistsim.stochastic import (Stochastic, photons_per_nm2, generate_acids, mean_acid,
                                  mean_deprotection, stochastic_deprotection, threshold_for_cd,
                                  edge_arrays, roughness)


def test_photons_per_nm2_euv():
    assert np.isclose(photons_per_nm2(30.0, 13.5), 20.39, atol=0.05)


def test_acid_statistics_match_compound_poisson():
    sto = Stochastic(pag_per_nm2=1000.0, blur_nm=0.0)          # large PAG pool: no clipping
    rng = np.random.default_rng(1)
    h = generate_acids(np.ones(8), 1.0, 13.5, 30.0, sto, 20000, rng)
    counts = h * sto.pag_per_nm2
    mu = photons_per_nm2(30.0, 13.5) * sto.absorbed_fraction
    assert np.isclose(counts.mean(), mu * sto.acids_per_photon, rtol=0.03)
    assert np.isclose(counts.var() / counts.mean(), 1 + sto.acids_per_photon, rtol=0.05)


def test_mean_field_matches_average_of_noisy_field():
    img = np.linspace(0.2, 1.0, 16)
    sto = Stochastic(blur_nm=0.0)
    rng = np.random.default_rng(2)
    h = generate_acids(img, 1.0, 13.5, 20.0, sto, 20000, rng).mean(axis=1)
    assert np.allclose(h, mean_acid(img, 1.0, 13.5, 20.0, sto), atol=0.02)


def test_edges_and_roughness_on_clean_profile():
    x = np.arange(-22, 22, 1.0)
    d = np.repeat(np.clip(1 - np.abs(x) / 20, 0, None)[:, None], 50, axis=1)
    l, r = edge_arrays(x, d, 0.5)
    rg = roughness(l, r)
    assert np.isclose(rg["mean_cd"], 20.0, atol=0.1) and rg["swr_3s"] < 1e-9 and rg["fail_frac"] == 0
    l, r = edge_arrays(x, d * 0, 0.5)
    assert roughness(l, r)["fail_frac"] == 1.0


def test_roughness_falls_with_dose_at_fixed_cd():
    dx, pitch, space = 1.0, 44.0, 22.0
    x = np.arange(-pitch / 2, pitch / 2, dx)
    img = aerial_image_1d(pitch, space, 13.5, 0.33, 0.6, x)
    chem = Chemistry(c=0.0, ea_kcal=30.0, k_ref=0.05, diff_len_nm=3.0)
    sto = Stochastic()
    ler = {}
    for dose in (10.0, 40.0):
        th = threshold_for_cd(x, mean_deprotection(img, dx, 13.5, dose, sto, chem), space)
        d = stochastic_deprotection(img, dx, 13.5, dose, sto, chem, 512, np.random.default_rng(3))
        ler[dose] = roughness(*edge_arrays(x, d, th))["swr_3s"]
    assert 1.3 < ler[10.0] / ler[40.0] < 3.5
