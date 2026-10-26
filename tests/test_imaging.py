import numpy as np
from resistsim import aerial_image_1d

EUV = dict(wavelength=13.5, na=0.33)


def test_clear_field_is_unity():
    x = np.linspace(-20, 20, 81)
    I = aerial_image_1d(pitch=40, space=40, sigma_out=0.8, x=x, **EUV)
    assert np.allclose(I, 1.0)


def test_coherent_three_beam_matches_analytic():
    pitch, space = 44.0, 22.0
    x = np.linspace(-pitch / 2, pitch / 2, 101)
    I = aerial_image_1d(pitch, space, sigma_out=0.0, x=x, **EUV)
    c0, c1 = space / pitch, np.sin(np.pi * space / pitch) / np.pi
    expected = (c0 + 2 * c1 * np.cos(2 * np.pi * x / pitch)) ** 2
    assert np.allclose(I, expected)


def test_below_cutoff_has_no_modulation():
    x = np.linspace(-20, 20, 81)
    I = aerial_image_1d(pitch=40, space=20, sigma_out=0.0, x=x, **EUV)
    assert np.ptp(I) < 1e-12          # first order blocked: flat image


def test_image_is_symmetric():
    x = np.linspace(-30, 30, 121)
    I = aerial_image_1d(pitch=60, space=30, sigma_out=0.6, x=x, defocus=50, **EUV)
    assert np.allclose(I, I[::-1])
