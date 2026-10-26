"""Image-quality metrics for a 1D line/space aerial image."""
import numpy as np
from .imaging import aerial_image_1d


def contrast(intensity):
    """Michelson contrast (Imax - Imin) / (Imax + Imin)."""
    hi, lo = np.max(intensity), np.min(intensity)
    return (hi - lo) / (hi + lo)


def nils(pitch, space, wavelength, na, sigma_out, dx=0.05, **kw):
    """Normalized image log-slope at the nominal space edge (x = space/2)."""
    xe = space / 2
    x = np.array([xe - dx, xe, xe + dx])
    I = aerial_image_1d(pitch, space, wavelength, na, sigma_out, x, **kw)
    return space * abs(I[2] - I[0]) / (2 * dx) / I[1]
