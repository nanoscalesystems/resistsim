"""1D partially coherent (Abbe) imaging of a periodic line/space mask.

Thin-mask approximation. All lengths in nm. The mask is binary: a clear
space of width `space` centred at x=0, repeating with period `pitch`.
"""
import numpy as np


def source_samples(sigma_out, sigma_in=0.0, n=101):
    """Source points projected onto the x axis, with normalized weights.

    A circular (sigma_in=0) or annular source is a 2D disk; for a grating
    with lines along y, only the x coordinate matters, so each x is
    weighted by the source chord length at that x.
    """
    if sigma_out == 0:
        return np.array([0.0]), np.array([1.0])
    sx = np.linspace(-sigma_out, sigma_out, n)
    w = 2 * (np.sqrt(np.clip(sigma_out**2 - sx**2, 0, None))
             - np.sqrt(np.clip(sigma_in**2 - sx**2, 0, None)))
    return sx, w / w.sum()


def aerial_image_1d(pitch, space, wavelength, na, sigma_out, x,
                    sigma_in=0.0, defocus=0.0, n_source=101):
    """Aerial image intensity at positions x (nm), normalized to clear field = 1."""
    x = np.asarray(x, dtype=float)
    fc = na / wavelength                       # pupil cutoff (1/nm)
    max_order = int(np.ceil(2 * fc * pitch)) + 2
    n = np.arange(-max_order, max_order + 1)

    # Fourier coefficients of the mask
    safe_n = np.where(n == 0, 1, n)
    c = np.where(n == 0, space / pitch, np.sin(np.pi * n * space / pitch) / (np.pi * safe_n))

    sx, w = source_samples(sigma_out, sigma_in, n_source)
    fx = n[None, :] / pitch + (sx * fc)[:, None]          # (source, order)
    passed = np.abs(fx) <= fc
    phase = 2 * np.pi * defocus * (np.sqrt(np.clip(1 / wavelength**2 - fx**2, 0, None)) - 1 / wavelength)
    amp = c[None, :] * passed * np.exp(1j * phase)

    field = amp @ np.exp(2j * np.pi * np.outer(n, x) / pitch)   # (source, x)
    return (np.abs(field) ** 2 * w[:, None]).sum(axis=0)
