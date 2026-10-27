"""Stochastic (shot-noise) resist model, 2D top-down view (x across the lines, y along them).

Imaging stays 1D (infinite lines, so the image is constant along y). Photon absorption and
acid generation are Poisson processes on a pixel grid; the acid field is blurred, baked with
the 2D PEB model and developed by a threshold. Edge positions along y give LER/LWR.

ALL parameters in `Stochastic` are UNSOURCED placeholders, as are diffusion lengths and the
development threshold. Use for trends (e.g. roughness vs dose), not absolute predictions.
"""
from dataclasses import dataclass
import numpy as np
from .bake import diffuse_periodic, peb_1d
from .pipeline import space_edges

HC_EV_NM = 1239.84198      # h*c in eV nm
EV_J = 1.602176634e-19


@dataclass(frozen=True)
class Stochastic:
    absorbed_fraction: float = 0.30   # fraction of incident photons absorbed in the film
    acids_per_photon: float = 1.0     # mean acids generated per absorbed photon
    pag_per_nm2: float = 10.0         # PAG molecules per nm^2 (areal, thin film)
    blur_nm: float = 2.0              # rms blur of acid deposition before the PEB


def photons_per_nm2(dose_mj_cm2, wavelength_nm):
    """Incident photons per nm^2 for a clear-field dose."""
    photon_j = HC_EV_NM / wavelength_nm * EV_J
    return dose_mj_cm2 * 1e-3 / photon_j / 1e14


def mean_acid(img, dx, wavelength, dose, sto):
    """Mean-field acid fraction (1D): the expectation of `generate_acids` before pixel noise."""
    h = (sto.acids_per_photon * sto.absorbed_fraction
         * photons_per_nm2(dose, wavelength) * np.asarray(img) / sto.pag_per_nm2)
    return diffuse_periodic(np.clip(h, 0.0, 1.0), dx, sto.blur_nm)


def generate_acids(img, dx, wavelength, dose, sto, n_y, rng):
    """Noisy acid fraction field, shape (len(img), n_y): Poisson photons -> Poisson acids -> blur."""
    mu = photons_per_nm2(dose, wavelength) * sto.absorbed_fraction * dx * dx * np.asarray(img)
    photons = rng.poisson(np.repeat(mu[:, None], n_y, axis=1))
    acids = rng.poisson(photons * sto.acids_per_photon)
    h = np.clip(acids / (sto.pag_per_nm2 * dx * dx), 0.0, 1.0)
    return diffuse_periodic(h, dx, sto.blur_nm)


def _bake(acid, dx, chem):
    return peb_1d(acid, dx, chem.peb_time_s, chem.peb_temp_c, chem.ea_kcal, chem.k_ref,
                  diff_len_nm=chem.diff_len_nm, quencher=chem.quencher)


def mean_deprotection(img, dx, wavelength, dose, sto, chem):
    return _bake(mean_acid(img, dx, wavelength, dose, sto), dx, chem)


def stochastic_deprotection(img, dx, wavelength, dose, sto, chem, n_y, rng):
    return _bake(generate_acids(img, dx, wavelength, dose, sto, n_y, rng), dx, chem)


def threshold_for_cd(x, d_mean, target_cd):
    """Development threshold that makes the mean-field space equal `target_cd`.

    Equivalent to choosing a resist of a given sensitivity (dose-to-size) for this image.
    """
    return float(np.interp(target_cd / 2.0, x, d_mean))


def edge_arrays(x, d2d, d_th):
    """Left/right edge position (nm) for each row along y; NaN where the space is closed or merged."""
    left = np.full(d2d.shape[1], np.nan)
    right = np.full(d2d.shape[1], np.nan)
    for j in range(d2d.shape[1]):
        e = space_edges(x, d2d[:, j], d_th)
        if e is not None:
            left[j], right[j] = e
    return left, right


def roughness(left, right):
    """Mean CD, LER (3 sigma, each edge), LWR/SWR (3 sigma of width) and fraction of failed rows."""
    ok = ~np.isnan(left)
    out = {"fail_frac": float(1.0 - ok.mean())}
    if ok.sum() < 2:
        return {**out, "mean_cd": np.nan, "ler_left_3s": np.nan, "ler_right_3s": np.nan, "swr_3s": np.nan}
    l, r = left[ok], right[ok]
    return {**out, "mean_cd": float((r - l).mean()),
            "ler_left_3s": float(3 * np.std(l)), "ler_right_3s": float(3 * np.std(r)),
            "swr_3s": float(3 * np.std(r - l))}
