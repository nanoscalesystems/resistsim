# resistsim
[![tests](https://github.com/nanoscalesystems/resistsim/actions/workflows/ci.yml/badge.svg)](https://github.com/nanoscalesystems/resistsim/actions/workflows/ci.yml)

Open-source photoresist process simulator: from mask image to printed edge, including the effect of
molecular-scale randomness. Maintained by [Nanoscale Systems](https://github.com/nanoscalesystems).
Lead author: Fazil (@phazyl).

**Status: v0.3, early research release. Illustrative and uncalibrated. Not a predictive tool for any
production process.**

## What it does

Mask pattern -> aerial image -> photoacid generation -> post-exposure bake (acid diffusion, quenching,
Arrhenius deprotection) -> threshold development -> space CD, focus-exposure matrix, exposure latitude and
depth of focus. A separate stochastic branch adds photon, acid-yield, PAG and quencher randomness to give
line-edge roughness and local bridge/break failure counts.

**Dimensionality.** Imaging is 1D: dense lines and spaces are treated as infinite, so the image is constant
along the lines. The stochastic resist model is 2D top-down (x across the lines, y along them), which is what
allows roughness and local failures. Not included: 2D imaging (contacts, line ends, tip-to-tip), depth in the
resist, and 3D mask effects.

| Stage | Model | Module |
|---|---|---|
| Imaging | Abbe partially coherent imaging, thin mask, circular or annular source, defocus | `imaging.py` |
| Exposure | Photoacid generation, `h = 1 - exp(-C * dose * I)` (deterministic path) | `exposure.py` |
| Bake | Periodic Gaussian acid diffusion (1D or 2D), Arrhenius deprotection, instant or finite-rate second-order acid-quencher reaction | `bake.py` |
| Development | Constant threshold on the deprotected fraction | `pipeline.py` |
| Metrics | Contrast, NILS, focus-exposure matrix, exposure latitude, depth of focus | `metrics.py`, `process_window.py` |
| Stochastics | Poisson photons, acid yield, PAG count and quencher count; hard or smooth PAG-pool limit; edge extraction for LER/LWR | `stochastic.py` |
| Failures | Voxel-scale counting of bridge and break events with Wilson intervals | `failure.py` |
| Data | Sourced deprotection activation energies, dose-to-clear data, pKa values; calibration helpers | `registry.py`, `calibration.py` |

## Quick start

    pip install -e ".[dev]"
    pytest -q
    python examples/01_aerial_image.py

## Examples

| File | Shows |
|---|---|
| `01_aerial_image.py` | Aerial image, contrast and NILS through focus |
| `02_e0_calibration.py` | Effective deprotection rates fitted to published dose-to-clear data |
| `03_process_window.py` | Exposure latitude versus acid diffusion length |
| `04_stochastic_roughness.py` | Roughness versus dose from photon shot noise |
| `05_noise_decomposition.py` | Roughness from each source of randomness (published modeling inputs) |
| `06_quencher_rate.py` | Finite-rate versus instant quenching |
| `07_quencher_diffusion.py` | Effect of quencher mobility |
| `08_superadditivity.py` | Whether the noise terms add in quadrature (hard versus smooth PAG pool) |
| `09_failure_vs_dose.py` | Bridge and break rates versus dose |

`scripts/make_figures.py` regenerates the figures used on the Nanoscale Systems website into `docs/figures/`.

## Sourced values and placeholders

- **From the literature** (see `REFERENCES.md`): deprotection activation energies for four cage monomers,
  dose-to-clear data and pKa values for PFAS and PFAS-free PAGs, the `NAULLEAU_CAR` stochastic preset
  (the authors' modeling assumptions for an illustrative case, not measurements), and the range of
  acid-quencher neutralization rates (a measured value and a diffusion-limit estimate).
- **Placeholders or sweep parameters:** acid diffusion length, quencher mobility, Dill C, the development
  threshold, deprotection rate prefactors, and the defaults of `Stochastic()`.
- Each registry entry carries a status (`literature`, `estimated` or `measured`) and a citation.

## PFAS-free resists

`registry.py` holds published deprotection activation energies and dose-to-clear data for a PFAS PAG and
two PFAS-free PAGs, and `calibration.py` fits effective rates to them. This supports *relative* comparisons
between PAGs. It does not predict absolute behavior, cannot separate acid strength from quantum yield,
diffusion or quenching, and is not validated for EUV. No sourced acid diffusion value for PFAS-free PAGs is
built in yet.

## Limitations (please read)

**Scope of the physics**
- 1D imaging only, thin-mask approximation, no aberrations, no 3D mask effects.
- Thin-resist model: no depth dimension, no standing waves, and no dissolution kinetics
  (development is a constant threshold).

**Parameters**
- Acid diffusion length and quencher mobility are unsourced sweep parameters.
- Dill C, quencher loading, the development threshold and the deprotection rate prefactors are placeholders,
  so absolute doses and rates are not meaningful.
- Activation energies were measured on monomers in solution and are used as a proxy for the film.
- The chemistry data come from 265 nm and electron-beam experiments and are not applied to EUV optics.

**Stochastics**
- Defaults of `Stochastic()` are placeholders. `NAULLEAU_CAR` uses published assumptions, not measurements.
- No protecting-group randomness, no secondary-electron transport, and no metrology-noise removal.
- Quenching is instant by default; the finite-rate option assumes an immobile quencher unless a diffusion
  length is set.
- The noise terms interact more strongly in this model than the published additive picture suggests
  (see example 08). The simulated roughness-versus-dose slope is about -0.6, against about -0.5 for pure
  shot noise.

**Failure model**
- Counting only: rates much below 1/(number of voxels) cannot be resolved, and a rare-event estimator is
  not yet implemented.
- The z-margins are trend indicators, not rates.

**Validation**
- Not validated against experiment. Comparisons with published numbers are qualitative rankings, and
  absolute values from the examples are not predictions.

## Roadmap (planned, not promised)

Calibration of the deprotection chain; a rare-event failure estimator; a dissolution model with a depth
dimension; an interactive in-browser demo; comparison with published process-window data; 2D imaging.

## Data provenance

Every equation and parameter comes from public literature listed in `REFERENCES.md`. No proprietary or
confidential data are used. Values read off published figures, if any are added, will be labeled as such.

## Related open-source work

TorchLitho, TorchResist, OpenILT and LithographySimulator target differentiable imaging, analytical resist
models and inverse lithography. resistsim focuses on resist chemistry and stochastic effects. Links are in
`REFERENCES.md`.

## Citing

See `CITATION.cff`.

## Licence

Apache-2.0.
