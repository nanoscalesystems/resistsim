"""Post-exposure bake (PEB): acid diffusion, quenching and acid-catalysed deprotection.

1D, periodic domain (a grating period), thin-resist approximation.
Acid is a fraction of the PAG loading (0..1), as returned by exposure.acid_fraction.

NOTE: `diff_len_nm` is an UNSOURCED sweep parameter, not a measured value.
"""
import numpy as np

R_KCAL = 1.987204e-3  # gas constant, kcal/(mol K)


def arrhenius_scale(ea_kcal, temp_c, ref_c):
    """Rate multiplier k(T)/k(T_ref) for activation energy ea_kcal (kcal/mol)."""
    t, tr = temp_c + 273.15, ref_c + 273.15
    return np.exp(-ea_kcal / R_KCAL * (1.0 / t - 1.0 / tr))


def diffuse_periodic(field, dx, length_nm):
    """Gaussian blur with rms length `length_nm` (= sqrt(2 D t)) on a periodic grid."""
    if length_nm <= 0:
        return np.asarray(field, dtype=float)
    k = 2 * np.pi * np.fft.rfftfreq(len(field), d=dx)
    return np.fft.irfft(np.fft.rfft(field) * np.exp(-0.5 * (k * length_nm) ** 2), n=len(field))


def peb_1d(acid, dx, time_s, temp_c, ea_kcal, k_ref, ref_temp_c=100.0,
           diff_len_nm=0.0, quencher=0.0, n_steps=200):
    """Return the deprotected fraction (0..1) after a bake.

    k_ref       : deprotection rate per unit acid fraction at ref_temp_c (1/s)
    diff_len_nm : acid rms diffusion length over the whole bake (sweep parameter)
    quencher    : base loading, same units as acid; fast stoichiometric neutralization
    """
    a = np.clip(np.asarray(acid, dtype=float) - quencher, 0.0, None)
    k_eff = k_ref * arrhenius_scale(ea_kcal, temp_c, ref_temp_c)
    dt = time_s / n_steps
    step_len = diff_len_nm / np.sqrt(n_steps)       # variances add: L^2 = n * step^2
    protected = np.ones_like(a)
    for _ in range(n_steps):
        a = diffuse_periodic(a, dx, step_len)
        protected *= np.exp(-k_eff * a * dt)
    return 1.0 - protected
