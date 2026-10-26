"""Aerial image and acid map for 22 nm half-pitch lines/spaces (generic EUV settings)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from resistsim import aerial_image_1d, acid_fraction, contrast, nils

EUV = dict(wavelength=13.5, na=0.33)
P = dict(pitch=44, space=22, sigma_out=0.6)
x = np.linspace(-44, 44, 881)

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for z in (0, 50, 100):
    I = aerial_image_1d(x=x, defocus=z, **P, **EUV)
    ax[0].plot(x, I, label=f"defocus {z} nm")
    print(f"defocus {z:>3} nm: contrast {contrast(I):.3f}, NILS {nils(**P, **EUV, defocus=z):.2f}")
ax[0].set(xlabel="x (nm)", ylabel="relative intensity", title="Aerial image"); ax[0].legend()

I0 = aerial_image_1d(x=x, **P, **EUV)
ax[1].plot(x, acid_fraction(I0, dose=30, c=0.05))
ax[1].set(xlabel="x (nm)", ylabel="acid fraction", title="Photoacid generation (generic parameters)")
fig.tight_layout(); fig.savefig("examples/aerial_image.png", dpi=150)
