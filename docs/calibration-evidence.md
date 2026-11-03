# Calibration evidence: first consistency diagnostic

## Scope

This diagnostic uses Liu et al., Chemical Science 2026, 17, 15458–15466,
DOI [10.1039/d6sc03643k](https://doi.org/10.1039/d6sc03643k).
It does not change the simulator defaults or establish an EUV calibration.

The machine-readable record is `data/experiments/liu2026_265nm_e0.json`.
It transcribes all 12 Table 2 entries (10 numerical clearing doses and two non-clearing observations), with source locations and reviewed PDF hashes. It is repository research data, not an automatically installed runtime preset.

## Experimental evidence versus model assumptions

| Item | Evidence | Use in diagnostic |
|---|---|---|
| E0 for 4a / TPS-PFBuS | Main Table 2: 25 mJ/cm² at 100°C; 110 at 90°C | Fit first point, compare against second |
| Exposure | SI1 Fig. S11(a): 265 nm LED, open frame | Explicitly not EUV |
| PEB | SI1 Fig. S11(a): variable temperature, 60 s | 60 s at both temperatures |
| Soft bake | SI1 Section 7.2 / Fig. S11: 110°C, 60 s | Recorded separately; not PEB |
| Development | SI1 Fig. S11(a): 2.4 wt% TMAH, 60 s, water | Conditions attached to observations |
| Film thickness | Main text before Table 2: nominal 80 nm | Not an independent thickness for each sample |
| TOA | SI1 Section 7.2 / Fig. S11: 10 mol%; relative-to-PAG wording in Fig. S14 caption | Q=0.10 is a nominal-loading mapping; instantaneous 1:1 neutralization remains assumed |
| Ea=33.5 kcal/mol | Main Table 2; SI1 Section 4: monomer kinetics in MsOH/DMSO solution | Film activation energy is a proxy, not a film measurement |
| C | No independent measurement established by this evidence record | Assumed sensitivity sweep |
| Clearing conversion=0.5 | Not measured in this dataset | Explicit assumption |
| k_ref | Calculated separately for each assumed C | Fitted effective parameter, not measurement |

Missing uncertainty is stored as null, not zero. Non-clearing entries retain the authors' statement that films did not fully dissolve after exposure to over 500 mJ/cm². The exact maximum tested dose is unknown from that statement. These observations do not become E0=500 or E0=infinity, and are excluded from numerical fitting here.

PFAS classification here describes the reported PAG, not a certification of the entire formulation, process equipment or environmental impact. No PFAS-free versus fluorinated comparison is claimed to be controlled for temperature, PAG photochemistry, or all formulation variables.

## Equations and interpretation

For uniform exposure, generated acid fraction is h=1-exp(-C E).
After assumed instantaneous quenching, a=max(h-Q,0).
Deprotection is d=1-exp(-k(T) a t). The rate follows the package's Arrhenius temperature scaling.

For each assumed C, `fit_k_ref` matches E0=25 at 100°C. The script then predicts E0 at 90°C using the same fitted parameters. A generated fraction >=1 means no finite dose can clear in this mathematical model. It is serialized as null with a descriptive status, never as a zero dose.

With Ea=33.5 and equal bake durations/thresholds, the 90°C/100°C rate ratio is about 0.2882. The necessary C interval is 0.004214<C<0.017814 cm²/mJ. This is an algebraic feasibility interval under the stated assumptions, not an experimentally measured interval or uncertainty estimate. It only requires finite clearing; it does not require agreement with 110 mJ/cm².

The assumed C=0.05 fits the reference but cannot clear at 90°C. C=0.015 predicts about 121.35 mJ/cm². Neither result selects a physically correct C. Changing the common clearing threshold and refitting k_ref leaves the dose prediction unchanged under this particular model.

The comparison observation has already informed our model exploration, so it should not be described as a pristine independent validation set. Matching both points later would be calibration, not validation. The existing `examples/02_e0_calibration.py` fits rates row-by-row; those fits do not demonstrate one parameter set working across temperatures.

## Run

From the repository root with the project installed in your active environment:

```bash
python scripts/calibration_consistency.py
python -m unittest discover -s tests -p test_calibration_evidence.py -v
python scripts/calibration_consistency.py --output /tmp/resistsim-calibration-report.json
```

The output option is optional and refuses to overwrite an existing report. It includes observed inputs, assumed parameters, fitted rates, predictions, source locations and hashes. The script checks all Table 2 entries against the installed registry; a mismatch stops the calculation.

## Next scientific work

1. Audit the remaining SI kinetics and film-response evidence before adopting additional constraints.
2. Obtain independent acid-generation or film-reaction data, or state which parameter combinations alone can be identified.
3. Fit one consistent formulation across conditions; reserve additional conditions for validation.
4. Quantify uncertainty; do not fabricate error bars from absent data.
5. Keep EUV calibration separate from 265 nm and electron-beam observations.
6. Keep failure-rate predictions and rare-event work separate until the underlying chemistry and defect definition are justified.

A successful code test verifies implementation, not agreement with experiment.
