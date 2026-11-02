"""Stochastic (shot-noise) resist model, 2D top-down view (x across the lines, y along them).

Imaging stays 1D (infinite lines, so the image is constant along y). Photons, acid yield, PAG
count and quencher count can each be Poisson-random (see the `random_*` flags); the acid field is
blurred, baked with the 2D PEB model and developed by a threshold. Edge positions along y give
LER/LWR. Quenching is either instant (pixelwise, before the bake) or a finite-rate second-order
reaction during the bake (`quencher_rate_nm3_s`).

`Stochastic()` defaults are UNSOURCED placeholders. `NAULLEAU_CAR` uses published modeling
assumptions (see below). Diffusion lengths and the development threshold are placeholders either
way. Use for trends and term rankings, not absolute predictions.
"""
from dataclasses import dataclass, replace
from typing import Optional
import numpy as np
from .bake import diffuse_periodic, peb_1d, peb_quench
from .pipeline import space_edges

HC_EV_NM = 1239.84198      # h*c in eV nm
EV_J = 1.602176634e-19


@dataclass(frozen=True)
class Stochastic:
    absorbed_fraction: float = 0.30   # fraction of incident photons absorbed in the film
    acids_per_photon: float = 1.0     # mean radiation-chemistry events (acids) per absorbed photon
    pag_per_nm2: float = 10.0         # PAG molecules per nm^2 (areal, thin film)
    blur_nm: float = 2.0              # rms blur of acid deposition before the PEB
    quencher_per_nm2: float = 0.0     # quencher molecules per nm^2 (0 = none)
    # which quantities are random (Poisson) rather than fixed at their mean:
    random_photons: bool = True
    random_yield: bool = True
    random_pag: bool = False
    random_quencher: bool = False
    # finite-rate quenching (None = instant pixelwise neutralization before the bake):
    thickness_nm: float = 35.0                    # film thickness, converts areal to volume density
    quencher_rate_nm3_s: Optional[float] = None   # neutralization rate constant k_n (nm^3/s)
    quencher_diff_nm: float = 0.0                 # quencher rms diffusion over the bake (0 = immobile)
    quencher_ea_kcal: float = 0.0                 # activation energy of neutralization
    pool: str = "hard"

    @classmethod
    def from_volumetric(cls, absorptivity_per_nm, thickness_nm, acids_per_photon,
                        pag_per_nm3, quencher_per_nm3=0.0, blur_nm=2.0,
                        random_pag=True, random_quencher=True, quencher_rate_nm3_s=None):
        """Build from bulk quantities: absorptivity (1/nm), densities (1/nm^3), film thickness (nm)."""
        return cls(absorbed_fraction=float(1.0 - np.exp(-absorptivity_per_nm * thickness_nm)),
                   acids_per_photon=acids_per_photon,
                   pag_per_nm2=pag_per_nm3 * thickness_nm,
                   quencher_per_nm2=quencher_per_nm3 * thickness_nm,
                   blur_nm=blur_nm, random_pag=random_pag, random_quencher=random_quencher,
                   thickness_nm=thickness_nm, quencher_rate_nm3_s=quencher_rate_nm3_s)


# Inputs from Naulleau et al., Chem. Mater. 2026, 38, 6141 (DOI 10.1021/acs.chemmater.5c02771),
# Table 1 (35 nm chemically amplified resist). These are the authors' MODELING ASSUMPTIONS for an
# illustrative case, not measurements. blur_nm = 3 nm follows the electron thermalization distance
# quoted there (about 3 nm in a typical resist); it is not a Table 1 value.
NAULLEAU_CAR = Stochastic.from_volumetric(
    absorptivity_per_nm=0.0042, thickness_nm=35.0, acids_per_photon=2.8,
    pag_per_nm3=0.2, quencher_per_nm3=0.09, blur_nm=3.0)


def photons_per_nm2(dose_mj_cm2, wavelength_nm):
    """Incident photons per nm^2 for a clear-field dose."""
    photon_j = HC_EV_NM / wavelength_nm * EV_J
    return dose_mj_cm2 * 1e-3 / photon_j / 1e14


def mean_acid(img, dx, wavelength, dose, sto):
    """Mean-field acid fraction (1D), ignoring quencher and PAG-pool statistics."""
    h = (sto.acids_per_photon * sto.absorbed_fraction
         * photons_per_nm2(dose, wavelength) * np.asarray(img) / sto.pag_per_nm2)
    return diffuse_periodic(np.clip(h, 0.0, 1.0), dx, sto.blur_nm)


def _draw(img, dx, wavelength, dose, sto, n_y, rng):
    """Random counts per pixel: acids (limited by the PAG pool) and quencher (None if absent)."""
    shape = (len(img), n_y)
    mu = photons_per_nm2(dose, wavelength) * sto.absorbed_fraction * dx * dx * np.asarray(img)
    mu = np.repeat(mu[:, None], n_y, axis=1)
    photons = rng.poisson(mu) if sto.random_photons else mu
    events = rng.poisson(photons * sto.acids_per_photon) if sto.random_yield else photons * sto.acids_per_photon
    pag_mean = sto.pag_per_nm2 * dx * dx
    pag = rng.poisson(pag_mean, size=shape) if sto.random_pag else pag_mean
    
    if sto.pool == "smooth":
        pag_arr = np.broadcast_to(np.asarray(pag, dtype=float), shape)
        n_int = np.rint(pag_arr).astype(np.int64)
        n_safe = np.maximum(n_int, 1)
        scale = np.where(n_int > 0, pag_arr / n_safe, 0.0)          # keeps the mean for non-integer pools
        p_hit = 1.0 - np.exp(-events / n_safe)                      # chance a given PAG is activated
        acids = (rng.binomial(n_int, p_hit) if sto.random_yield else n_int * p_hit) * scale
    else:
        acids = np.minimum(events, pag)

    
    q = None
    if sto.quencher_per_nm2 > 0:
        q_mean = sto.quencher_per_nm2 * dx * dx
        q = rng.poisson(q_mean, size=shape) if sto.random_quencher else q_mean
    return acids, q, pag_mean


def generate_acids(img, dx, wavelength, dose, sto, n_y, rng):
    """Noisy net acid fraction field, shape (len(img), n_y), with INSTANT pixelwise quenching.

    Photons -> events (acids) -> limited by available PAG -> minus quencher -> blur.
    Each stage is Poisson or fixed at its mean according to the `random_*` flags.
    """
    acids, q, pag_mean = _draw(img, dx, wavelength, dose, sto, n_y, rng)
    if q is not None:
        acids = np.maximum(acids - q, 0.0)
    return diffuse_periodic(np.clip(acids / pag_mean, 0.0, 1.0), dx, sto.blur_nm)


def generate_fields(img, dx, wavelength, dose, sto, n_y, rng):
    """(acid, quencher) fraction fields before the bake, for finite-rate quenching.

    The acid is blurred by `blur_nm` (electron blur); the quencher is not.
    """
    acids, q, pag_mean = _draw(img, dx, wavelength, dose, sto, n_y, rng)
    h = diffuse_periodic(np.clip(acids / pag_mean, 0.0, 1.0), dx, sto.blur_nm)
    hq = np.zeros_like(h) if q is None else np.broadcast_to(q / pag_mean, h.shape).copy()
    return h, hq


def _bake(acid, dx, chem):
    return peb_1d(acid, dx, chem.peb_time_s, chem.peb_temp_c, chem.ea_kcal, chem.k_ref,
                  diff_len_nm=chem.diff_len_nm, quencher=chem.quencher)


def mean_deprotection(img, dx, wavelength, dose, sto, chem):
    return _bake(mean_acid(img, dx, wavelength, dose, sto), dx, chem)


def stochastic_deprotection(img, dx, wavelength, dose, sto, chem, n_y, rng):
    """Deprotected-fraction field. Any quencher in `sto` replaces chem.quencher (which is ignored).

    quencher_rate_nm3_s None : instant pixelwise neutralization before the bake.
    quencher_rate_nm3_s set  : finite-rate second-order neutralization during the bake.
    """
    if sto.quencher_rate_nm3_s is None:
        if sto.quencher_per_nm2 > 0:
            chem = replace(chem, quencher=0.0)
        return _bake(generate_acids(img, dx, wavelength, dose, sto, n_y, rng), dx, chem)
    h, hq = generate_fields(img, dx, wavelength, dose, sto, n_y, rng)
    kappa = sto.quencher_rate_nm3_s * sto.pag_per_nm2 / sto.thickness_nm   # 1/s per unit fraction
    return peb_quench(h, hq, dx, chem.peb_time_s, chem.peb_temp_c, chem.ea_kcal, chem.k_ref,
                      kappa_ref=kappa, diff_len_nm=chem.diff_len_nm,
                      quencher_diff_len_nm=sto.quencher_diff_nm, ea_n_kcal=sto.quencher_ea_kcal)


def threshold_for_cd(x, d_mean, target_cd):
    """Development threshold that makes the MEAN deprotection profile open a space of `target_cd`.

    d_mean can be the mean-field profile or the row-average of a noisy pilot field.
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
