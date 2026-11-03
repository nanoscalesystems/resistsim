# Evidence review: PFAS-free and EUV archive

## What changed

We now have a named-formulation EUV performance benchmark: Liu et al., SPIE 2025,
DOI 10.1117/12.3050881, Tables 7–8. It is suitable for a measurement view and future
forward-model comparison under matched conditions. It does not uniquely identify
acid generation, quenching, reaction kinetics or diffusion. No simulator defaults change.

## Source inventory and use decisions

1. **Technology readiness of PFAS-free lithography materials: an anonymized survey
   of resist and ancillary material maturity**, Danilo De Simone, JM3 25(4), 040901
   (2026). Ten supplier partners; aggregated self-reported maturity. EUV range 4–6,
   excluding the isolated TRL-1 entry as described by the author. Use for contextual
   maturity labels, not numerical resist calibration or independent manufacturing
   qualification. Reported range is not a probability distribution.
2. **Commercialization of Non-PFAS KrF and Development of Non-PFAS EUV Photoresists**,
   Cong Liu et al., SPIE 13428, 1342822 (2025), DOI 10.1117/12.3050881.
   Priority source: four Gen-2 EUV rows transcribed from Table 8 and visually verified.
   Table 7 identifies Poly-7, PAG-D/reference PAG, Q-3 and solvents; absolute loadings
   and chemical structures are not disclosed. Processing: 30 nm film, SiARC,
   13.5 nm NXE3400B exposure, PAB 110°C/60 s, PEB 100°C/60 s, 0.26 N TMAH/30 s.
   Do not inherit the 60 nm film / 90°C PEB of the separate Gen-1 experiment.
   Gen-1 contact-hole and line/space process-window images are qualitative here;
   no defect probabilities are inferred from their red/purple cells.
   Gen-2 uLER conflict: Table 8 says 1.75 nm for non-PFAS P28; prose says 1.85 nm.
   Display Table 8 provisionally, visibly preserving the conflict. The prose also
   calls the reference Ref. C once, whereas Tables 7–8 use Ref. D.
   The Gen-1 discussion says PAG-D where its formulation table says PAG-C;
   that inconsistency is not carried into a quantitative Gen-1 dataset.
3. **2024 SPIE_DCarja_vfinal_FK**, Merck/EMD presentation. Slides 11–15 contain
   fluorine-free M-PAG i-line and KrF comparisons. Slide 12 shows an optimized
   negative-tone i-line comparison at 450 mJ/cm² for both versions, 10 µm film.
   Slide 11's earlier substitution example instead uses 350 versus 650 mJ/cm²:
   these are different examples, not contradictory replicate measurements.
   Slide 13 shows 17.9/17.7 mJ/cm² labels alongside a dose-axis graph spanning
   roughly 120–220 mJ/cm². Without clarification, do not combine those into a
   single numeric dose-response curve. Slide 14 lists 180/160/250 nm half-pitch
   examples in 650/310/410 nm films for different polymer systems. Useful future
   benchmarks; incomplete processing conditions and graphical data need follow-up.
4. **2024 EUVL Workshop and Supplier Showcase Abstract Book**, P55, printed p.43:
   *Multi-Trigger Resist Patterning towards High-NA EUV Lithography*. Reports
   PFAS-free negative-tone MTR: P28 L/S at 56 mJ/cm², 21.5 nm film, unbiased
   LER 2.2 nm; P32 hexagonal pillars at 76 mJ/cm², 20 nm film, unbiased LCDU 2.6 nm.
   These are abstract-reported measurements with incomplete recipe/metrology.
   The title is not evidence that these exposures used a High-NA scanner.
   MTR ring-opening/crosslinking chemistry requires a different model from positive
   deprotection. Request the full presentation/paper before fitting.
5. **Resolving In Situ Exposure Dynamics in a Chemically Amplified EUV Photoresist
   Using Table-Top EUV Photoemission Spectroscopy**, Singh et al., ACS Applied
   Materials & Interfaces 17, 52567–52579 (2025), DOI 10.1021/acsami.5c09589.
   This is a PFAS-containing ESCAP model resist, not a PFAS-free benchmark.
   EUV photoemission, XPS, outgassing and FTIR probe exposure-induced chemistry.
   Ex-situ doses include 0, 10, 20, 40, 60, 100, 200, 400 mJ/cm² without PEB.
   It supports evaluating additional reaction channels, but spectral peak loss
   must not be treated as acid yield or clearing conversion. Request Supporting
   Information and raw normalized dose-response data before extracting parameters.
6. **US 12,242,190 B2**, Meijer et al., *Photoacid generator for chemically amplified
   photoresists*, IBM, dated 4 March 2025. Scanned patent: relevant specification
   pages reviewed using OCR, with cover checked visually. It describes polycyclic
   aromatic PAG anions, including fluorine-free examples and optional fluorinated
   variants. A patent-wide PFAS-free label would be wrong. No usable measured
   dose-to-clear / CD-versus-dose calibration series was identified in this review.
   Use as a chemistry/design lead. This review makes no legal scope or freedom-to-
   operate assessment and does not equate patent claims with experimental validation.

## Evidence classification

Keep author-reported PFAS-free formulation status distinct from a fluorine-free
PAG component and from a fluorine-free manufacturing process. Both resist papers
mention PTFE filtration; their formulation claims do not imply a PFAS-free process.
Do not infer hazard, lifecycle benefit, or emissions reduction from patterning metrics.

The earlier i-line packaging paper (Lu et al., DOI 10.1117/12.3050807) contributes
17 tabulated patterning observations. These include poor-profile cases, retained
without cherry-picking. Its Table 2 header is mislabeled Contact Hole; the title
and discussion identify line/space. Its profile delta-CD definition is separate
from nominal-to-printed CD bias. No patterning dose is relabeled E0.

## Next data requests, in priority order

- Gen-2 EUV raw CD versus dose/focus grids, the target CD and process-window
  acceptance rules, dose calibration, roughness definitions/sampling/uncertainty,
  illumination/mask details and the Table 8 uLER clarification. Summary DtS/EL/DOF
  values alone cannot reproduce a full process window.
- Same-formulation contrast curves, acid generation and deprotection versus time
  and temperature, plus composition/loading information if available. These would
  support kinetic inference rather than only performance benchmarking.
- Singh et al. Supporting Information and numeric chemical-response curves.
- P55 full presentation and chemistry/process details for a separate MTR model.

Reported small differences (e.g. 48.7 versus 48.8 mJ/cm²) are not established
statistically significant improvements without uncertainties and replicates.
A rare-event estimator still needs a suitable failure model and experimental
constraints; these summary benchmarks do not supply failure probabilities.
