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

`registry.py` holds published monomer activation energies and dose-to-clear observations for a PFAS-containing PAG and two reported PFAS-free PAGs. `calibration.py` fits conditional effective rates. These rates depend on assumed acid generation, quenching and clearing conversion; their ratios are not independently measured PAG reaction-rate ratios or validated performance rankings.

### Experimental evidence and consistency checks

The source-traceable [265 nm dataset](data/experiments/liu2026_265nm_e0.json) records Table 2 observations and supplementary experimental conditions from Liu et al. (DOI 10.1039/d6sc03643k). Numerical E0 observations, non-clearing observations, solution-phase kinetics, fitted values and assumptions are kept distinct. No independent uncertainty is invented for observations without reported error bars.

Run the [calibration consistency diagnostic](docs/calibration-evidence.md):

```bash
python scripts/calibration_consistency.py
python -m unittest discover -s tests -p test_calibration_evidence.py -v
```

Under the existing C=0.05, Q=0.10 and monomer-Ea proxy assumptions, fitting the 4a / TPS-PFBuS observation at 100°C does not reproduce clearing at 90°C. Varying C changes that result. This is a sensitivity diagnostic, not a newly validated parameter set. Simulator defaults remain unchanged. No sourced PFAS-free acid diffusion value or EUV calibration is established by this dataset.

## Browser interface

A Pyodide interface has been implemented in the separate Nanoscale Systems Astro website project at `/research/resistsim/simulator/`. It provides automatic optical previews and button-driven deterministic exposure/bake calculations, with worker execution, loading status, mobile layout and exports. This describes the implementation; deployment status is managed in the website project.

The interface uses the Python package through a browser adapter. It currently uses illustrative chemistry constants rather than selecting calibrated formulations from the literature registry. Desktop/browser agreement checks verify numerical execution for tested cases, not experimental accuracy. Finite-rate quenching, 2D stochastics and failure counting are available in the Python package but are not exposed in that interface.

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
dimension; evidence-backed browser presets; comparison with published process-window data; 2D imaging.

## Data provenance

Literature sources are listed in `REFERENCES.md`; some parameters are explicitly assumed or fitted rather than measured. The experimental dataset and diagnostic document those distinctions and source locations. No proprietary or confidential data are used. Future values digitized from figures must be labeled as digitized, with uncertainty and extraction method.

## Related open-source work

TorchLitho, TorchResist, OpenILT and LithographySimulator target differentiable imaging, analytical resist
models and inverse lithography. resistsim focuses on resist chemistry and stochastic effects. Links are in
`REFERENCES.md`.

## Citing

See `CITATION.cff`.

## Licence

Apache-2.0.
