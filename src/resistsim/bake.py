"""Post-exposure bake (PEB): acid diffusion, quenching and acid-catalysed deprotection.

1D or 2D periodic domain, thin-resist approximation.
Acid is a fraction of the PAG loading (0..1), as returned by exposure.acid_fraction.

NOTE: `diff_len_nm` is an UNSOURCED sweep parameter, not a measured value.
"""
import numpy as np

R_KCAL = 1.987204e-3  # gas constant, kcal/(mol K)


def arrhenius_scale(ea_kcal, temp_c, ref_c):
    """Rate multiplier k(T)/k(T_ref) for activation energy ea_kcal (kcal/mol)."""
    t, tr = temp_c + 273.15, ref_c + 273.15
    return np.exp(-ea_kcal / R_KCAL * (1.0 / t - 1.0 / tr))


def _kernel(shape, dx, length_nm):
    """Fourier-space Gaussian multiplier for an N-D periodic grid (rfftn layout)."""
    freqs = [np.fft.fftfreq(n, d=dx) for n in shape[:-1]] + [np.fft.rfftfreq(shape[-1], d=dx)]
    grids = np.meshgrid(*[2 * np.pi * f for f in freqs], indexing="ij")
    k2 = sum(g ** 2 for g in grids)
    return np.exp(-0.5 * k2 * length_nm ** 2)


def diffuse_periodic(field, dx, length_nm):
    """Gaussian blur with rms length `length_nm` (= sqrt(2 D t)) on a periodic N-D grid."""
    field = np.asarray(field, dtype=float)
    if length_nm <= 0:
        return field
    axes = tuple(range(field.ndim))
    return np.fft.irfftn(np.fft.rfftn(field, axes=axes) * _kernel(field.shape, dx, length_nm), s=field.shape, axes=axes)


def peb_1d(acid, dx, time_s, temp_c, ea_kcal, k_ref, ref_temp_c=100.0,
           diff_len_nm=0.0, quencher=0.0, n_steps=200):
    """Return the deprotected fraction (0..1) after a bake. Works on 1D or 2D arrays.

    k_ref       : deprotection rate per unit acid fraction at ref_temp_c (1/s)
    diff_len_nm : acid rms diffusion length over the whole bake (sweep parameter)
    quencher    : base loading, same units as acid; fast stoichiometric neutralization
    """
    a = np.clip(np.asarray(acid, dtype=float) - quencher, 0.0, None)
    k_eff = k_ref * arrhenius_scale(ea_kcal, temp_c, ref_temp_c)
    dt = time_s / n_steps
    step_len = diff_len_nm / np.sqrt(n_steps)       # variances add: L^2 = n * step^2
    axes = tuple(range(a.ndim))
    kern = _kernel(a.shape, dx, step_len) if step_len > 0 else None
    protected = np.ones_like(a)
    for _ in range(n_steps):
        if kern is not None:
            a = np.fft.irfftn(np.fft.rfftn(a, axes=axes) * kern, s=a.shape, axes=axes)
        protected *= np.exp(-k_eff * a * dt)
    return 1.0 - protected
