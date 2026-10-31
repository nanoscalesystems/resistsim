# References

## Methods
- C. A. Mack, *Fundamental Principles of Optical Lithography*, Wiley (2007), DOI 10.1002/9780470723876.
  Imaging, exposure and development models.
- F. H. Dill et al., "Characterization of positive photoresist," IEEE Trans. Electron Devices 22, 445 (1975).
  Exposure kinetics.
- M. Born and E. Wolf, *Principles of Optics*. Diffraction and partially coherent imaging.

## Data and parameters used in the code
- Y. Liu, M. D. Summersgill et al., "PFAS free chemically amplified resists enabled by low activation
  energy hydrocarbon cage monomers," Chem. Sci. 17, 15458 (2026), DOI 10.1039/d6sc03643k.
  Activation energies (SI Table S2), dose-to-clear data (Table 2) and pKa values as quoted there.
  Licensed CC BY-NC 4.0: numbers are recorded with citation, and no tables or figures are reproduced.
- P. Naulleau et al., "Illuminating the Challenges in Extreme Ultraviolet Patterning Materials,"
  Chem. Mater. 38, 6141 (2026), DOI 10.1021/acs.chemmater.5c02771.
  Source of the `NAULLEAU_CAR` inputs (Table 1: the authors' modeling assumptions) and of the electron
  thermalization length used to set the 3 nm acid-deposition blur.
- P. Naulleau and G. Gallatin, "Relative importance of various stochastic terms and EUV patterning,"
  J. Micro/Nanolithogr. MEMS MOEMS 17(4), 041015 (2018), DOI 10.1117/1.JMM.17.4.041015
  Noise-term decomposition (comparison target), quenching rate anchor (10 nm^3/s), model structure.
- F. A. Houle, W. D. Hinsberg, M. I. Sanchez, "Acid-base reactions in a positive tone chemically amplified
  photoresist and their effect on imaging," J. Vac. Sci. Technol. B 22, 747 (2004), DOI 10.1116/1.1688351.
  Measured acid-base neutralization rate constants (anchors for the quencher-rate sweep).
- F. A. Houle, W. D. Hinsberg, M. I. Sanchez, J. A. Hoffnagle, "Influence of resist components on image blur
  in a patterned positive-tone chemically amplified photoresist," J. Vac. Sci. Technol. B 20, 924 (2002),
  DOI 10.1116/1.1475985. Background for the bake model: chemical versus diffusive blur, anion-size effects.
- W. D. Hinsberg, F. A. Houle, M. I. Sanchez, G. M. Wallraff, "Chemical and physical aspects of the
  post-exposure baking process used for positive-tone chemically amplified resists,"
  IBM J. Res. Dev. 45, 667 (2001). Acid diffusion behavior and the proportional-neutralization picture;
  guides the ranges of the diffusion sweeps (no values are built in).
- W. D. Hinsberg, G. M. Wallraff, M. I. Sanchez, N. Megiddo, O. Kostko, "Contribution of EUV resist counting
  statistics to stochastic printing failures," J. Micro/Nanopattern. Mater. Metrol. 20(1), 014603 (2021).
  Framework for `failure.py` (voxel statistics, bridge and break events, solubility threshold).

## Comparison and validation targets
- C. N. Anderson and P. P. Naulleau, "Do not always blame the photons: Relationships between deprotection
  blur, line-edge roughness, and shot noise in extreme ultraviolet photoresists,"
  J. Vac. Sci. Technol. B 27, 665 (2009), DOI 10.1116/1.3100270. Measured LER, blur and E-size trends;
  not yet compared quantitatively.
- B. A. Reddy et al., "PFAS-Free 193 immersion Resist for 28 nm node Metal-1 Layer Electrical Performance
  Meets POR Quality," Proc. SPIE 13983, 139831I (2026), DOI 10.1117/12.3091736. Process-window and
  roughness targets for a PFAS-free resist; not yet implemented.
- "Y. Kaneko, T. Masubuchi et al., "PFAS free materials and resist for ArF immersion photolithography," Proc. SPIE 134  28, 134280W (2025), DOI 10.1117/12.3047953. Acid diffusion reach of PFAS and PFAS-free PAGs (read from a figure); not yet used in the code.

## Which reference informs which module
| Module | References |
|---|---|
| `imaging.py`, `exposure.py`, `pipeline.py` | Mack; Dill et al.; Born and Wolf |
| `registry.py`, `calibration.py` | Liu et al. |
| `bake.py` (quenching) | Houle 2004; Houle 2002; Hinsberg 2001; Naulleau and Gallatin |
| `stochastic.py` | Naulleau et al. 2026; Naulleau and Gallatin; Anderson and Naulleau |
| `failure.py` | Hinsberg 2021 |

## Related open-source projects
- TorchLitho: https://github.com/torchopc/torchlitho
- TorchResist: https://arxiv.org/abs/2502.06838
- OpenILT: https://github.com/OpenOPC/OpenILT
- LithographySimulator: https://github.com/quarterwave0/LithographySimulator

## Notes on use of published data
Numerical values are recorded with citation. Tables and figures are not reproduced. Values read from a
figure are labeled as such and carry reading uncertainty. Where a source licence is restrictive, only facts
and numbers are used.
