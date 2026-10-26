"""End-to-end 1D flow: aerial image -> acid -> PEB -> space CD, plus focus-exposure matrices.

Development is a constant-threshold model on the deprotected fraction (thin resist,
no depth dimension yet). Threshold `d_th` is a placeholder, not a calibrated value.
"""
from dataclasses import dataclass
import numpy as np
from .imaging import aerial_image_1d
from .exposure import acid_fraction
from .bake import peb_1d


@dataclass(frozen=True)
class Optics:
    wavelength: float
    na: float
    sigma_out: float
    pitch: float
    space: float
    sigma_in: float = 0.0


@dataclass(frozen=True)
class Chemistry:
    c: float                 # Dill C, cm^2/mJ
    ea_kcal: float
    k_ref: float             # 1/s per unit acid fraction at 100 C
    quencher: float = 0.10
    diff_len_nm: float = 0.0  # UNSOURCED sweep parameter
    peb_temp_c: float = 100.0
    peb_time_s: float = 60.0
    d_th: float = 0.5        # placeholder development threshold


def space_cd(x, d, d_th):
    """Width of the opened space around x=0 where deprotection >= d_th (linear interpolation).

    Returns 0 if nothing opens, and the full period if the space merges with its neighbours.
    """
    i0 = int(np.argmin(np.abs(x)))
    if d[i0] < d_th:
        return 0.0

    def edge(step):
        i = i0
        while 0 <= i + step < len(x):
            j = i + step
            if d[j] < d_th:
                return x[i] + (d[i] - d_th) / (d[i] - d[j]) * (x[j] - x[i])
            i = j
        return None

    right, left = edge(+1), edge(-1)
    if right is None or left is None:
        return float(x[-1] - x[0] + (x[1] - x[0]))
    return float(right - left)


def fem(optics, chem, doses, defoci, dx=0.25):
    """Space CD (nm) on a dose x defocus grid; shape (len(doses), len(defoci))."""
    x = np.arange(-optics.pitch / 2, optics.pitch / 2, dx)
    out = np.zeros((len(doses), len(defoci)))
    for j, z in enumerate(defoci):
        img = aerial_image_1d(optics.pitch, optics.space, optics.wavelength, optics.na,
                              optics.sigma_out, x, sigma_in=optics.sigma_in, defocus=z)
        for i, e in enumerate(doses):
            acid = acid_fraction(img, e, chem.c)
            d = peb_1d(acid, dx, chem.peb_time_s, chem.peb_temp_c, chem.ea_kcal, chem.k_ref,
                       diff_len_nm=chem.diff_len_nm, quencher=chem.quencher)
            out[i, j] = space_cd(x, d, chem.d_th)
    return out
