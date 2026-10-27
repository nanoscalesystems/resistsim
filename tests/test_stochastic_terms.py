import numpy as np
from resistsim.stochastic import Stochastic, NAULLEAU_CAR, generate_acids


def test_from_volumetric_matches_source_numbers():
    assert np.isclose(NAULLEAU_CAR.absorbed_fraction, 1 - np.exp(-0.0042 * 35))
    assert np.isclose(NAULLEAU_CAR.pag_per_nm2, 7.0) and np.isclose(NAULLEAU_CAR.quencher_per_nm2, 3.15)
    assert NAULLEAU_CAR.acids_per_photon == 2.8


def test_no_randomness_gives_identical_rows():
    off = Stochastic(random_photons=False, random_yield=False, random_pag=False, random_quencher=False,
                     quencher_per_nm2=2.0, blur_nm=0.0)
    h = generate_acids(np.linspace(0.3, 1, 8), 1.0, 13.5, 30.0, off, 50, np.random.default_rng(0))
    assert np.allclose(h, h[:, :1])


def test_each_term_alone_adds_noise():
    base = dict(random_photons=False, random_yield=False, random_pag=False, random_quencher=False,
                quencher_per_nm2=2.0, blur_nm=0.0)
    img = np.ones(4)
    for term in ("random_photons", "random_yield", "random_pag", "random_quencher"):
        sto = Stochastic(**{**base, term: True})
        h = generate_acids(img, 1.0, 13.5, 30.0, sto, 2000, np.random.default_rng(1))
        assert h.std(axis=1).min() > 0, term


def test_acids_never_exceed_pag_pool():
    sto = Stochastic(pag_per_nm2=2.0, acids_per_photon=5.0, blur_nm=0.0)
    h = generate_acids(np.ones(4), 1.0, 13.5, 100.0, sto, 500, np.random.default_rng(2))
    assert h.max() <= 1.0 + 1e-12
