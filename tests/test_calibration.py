import numpy as np
import pytest
from resistsim import acid_fraction, peb_1d
from resistsim.calibration import apparent_ea, fit_k_ref
from resistsim.bake import arrhenius_scale


def test_apparent_ea_recovers_known_ea():
    s = arrhenius_scale(30.0, 90, 100)           # k(90)/k(100)
    assert np.isclose(apparent_ea(25 / s, 90, 25, 100), 30.0)


def test_fit_round_trip_clears_at_e0():
    k = fit_k_ref(25.0, 100, 33.5, c=0.05, quencher=0.1, d_clear=0.5)
    acid = acid_fraction(np.full(8, 1.0), dose=25.0, c=0.05)
    d = peb_1d(acid, 1.0, 60, 100, 33.5, k_ref=k, quencher=0.1)
    assert np.allclose(d, 0.5, atol=1e-6)


def test_fit_rejects_acid_below_quencher():
    with pytest.raises(ValueError):
        fit_k_ref(1.0, 100, 30.0, c=0.01, quencher=0.1)
