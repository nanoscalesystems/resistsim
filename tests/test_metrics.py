import numpy as np
from resistsim import aerial_image_1d, contrast, nils, acid_fraction

EUV = dict(wavelength=13.5, na=0.33)
P = dict(pitch=44, space=22, sigma_out=0.6)


def test_contrast_bounds():
    x = np.linspace(-22, 22, 201)
    assert 0 < contrast(aerial_image_1d(x=x, **P, **EUV)) < 1
    assert contrast(np.ones(10)) == 0


def test_nils_falls_with_defocus():
    assert nils(**P, **EUV, defocus=0) > nils(**P, **EUV, defocus=100)


def test_acid_fraction_limits():
    h = acid_fraction(np.array([0.0, 1.0, 50.0]), dose=30, c=0.05)
    assert h[0] == 0 and 0 < h[1] < 1 and h[2] > 0.999
