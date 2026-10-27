# resistsim

Open-source photoresist process simulator (1D), from mask to process window.
Maintained by [Nanoscale Systems](https://github.com/nanoscalesystems). Lead author: Fazil (@phazyl).

**Status: v0.1, research and education tool. Not calibrated to any production process.**

## What it does

Mask pattern -> aerial image -> photoacid generation -> post-exposure bake
(acid diffusion, quenching, Arrhenius deprotection) -> space CD -> focus-exposure
matrix, exposure latitude and depth of focus.

| Stage | Model | Module |
|---|---|---|
| Imaging | Abbe partially coherent, thin mask, circular/annular source, defocus | `imaging.py` |
| Exposure | Photoacid generation, `h = 1 - exp(-C * dose * I)` | `exposure.py` |
| PEB | Periodic Gaussian acid diffusion, stoichiometric quencher, Arrhenius deprotection | `bake.py` |
| Development | Constant threshold on deprotected fraction | `pipeline.py` |
| Metrics | Contrast, NILS, process window | `metrics.py`, `process_window.py` |
| Data | Sourced resist/PAG parameters with status and citation | `registry.py`, `calibration.py` |
| Stochastics | Poisson photon absorption and acid generation, 2D top-down (x across, y along lines), LER/LWR from edge extraction | `stochastic.py` |

## Quick start

    pip install -e ".[dev]"
    pytest -q
    python examples/01_aerial_image.py
    python examples/03_process_window.py

## PFAS-free resists

`registry.py` holds published deprotection activation energies and dose-to-clear data
for PFAS and PFAS-free photoacid generators (see `REFERENCES.md`), and `calibration.py`
fits effective rates to them. This supports *relative* comparisons between PAGs. It does
not predict absolute behaviour, and it cannot separate acid strength from quantum yield,
diffusion or quenching.

## Limitations (please read)

- **Acid diffusion length is an unsourced sweep parameter.** No published value is built in.
- Dill C, quencher loading and the development threshold are placeholders.
- Activation energies were measured on monomers in solution and used as a proxy for the film.
- The chemistry data come from 265 nm and electron-beam experiments; they are not applied to EUV optics.
- Thin mask, thin resist, no aberrations, no stochastics (shot noise, LER), no depth dimension.
- Absolute DOF and EL values from the examples are not predictions.
- Stochastic parameters (absorbed fraction, acids per photon, PAG density, blur) are unsourced placeholders. Results show trends such as roughness versus dose, not absolute LER.
- The example's LER-versus-dose slope is about -0.6 (pure shot noise gives about -0.5). Do not quote the absolute roughness values.
- No quencher or PAG-site randomness, no secondary-electron transport, and no metrology-noise removal.

## Data provenance

Every equation and parameter comes from public literature listed in `REFERENCES.md`.
No proprietary or confidential data are used.

## Related open-source work

TorchLitho, TorchResist, OpenILT and LithographySimulator target differentiable imaging,
analytical resist models and inverse lithography. See `REFERENCES.md` for links.

## Citing

See `CITATION.cff`.

## Licence

Apache-2.0.
