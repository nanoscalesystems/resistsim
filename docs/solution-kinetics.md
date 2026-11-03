# Solution kinetics: evidence and reconstruction

Source: Liu et al., DOI https://doi.org/10.1039/d6sc03643k, Supporting Information 1, Section 4, pages S1-17–S1-22. Tables S1, S2 and S3 contain rounded rates, Arrhenius summaries and standardized half-lives respectively.

## What is measured and what is reconstructed

NMR tracks monomer disappearance in DMSO-d6 with pre-added methanesulfonic acid. An exponential fit gives k_prime (s^-1). Equation S2 divides this by acid concentration to obtain the acid-normalized second-order rate k. No exposure coefficient C is involved.

The new JSON transcribes all 12 S1 conditions with actual temperatures, acid concentrations, k_prime, k and replicate counts. It retains S2 activation energies and their reported standard errors, and S3 rates/half-lives at 90°C and 1 mol/L acid. These are published fitted summaries, not raw time-series or individual replicate data.

The reconstruction uses unweighted least squares of ln(k) versus 1/T on rounded S1 rates. SI R=8.314 J/(mol K), Celsius conversion T=t+273.15 and 4184 J/kcal are explicit. The slope is -Ea/R. The fitted k at 90°C gives half-life ln(2)/(k*1 mol/L). Published S2 standard errors are preserved, not assigned to individual S1 points or treated as new uncertainty estimates.

## Adopted discrepancy resolution

For monomer 13, use SI Table S3's **1222.2 s**. Main Table 2 prints 1122 s. The project owner agreed to adopt the supplementary value. Reconstructing S1 gives about 1222.4 s, supporting this decision. The alternate value remains in the machine-readable provenance; it is not used in calculations. No claim of an author-issued correction is made.

## Units

The SI labels second-order k as mol L^-1 s^-1. Equation S2, k=k_prime/[MsOH], instead requires **L mol^-1 s^-1**. Both labels are stored, with the dimensional justification. The calculation uses the latter. Numerically taking logarithms uses k expressed in those units; the fitted intercept depends on that unit convention.

## Limits and tests

Actual intermediate temperatures differ (89°C for monomer 1; 90.5°C for the others). Most measurements use two trials; 15a at 83°C uses one. Monitoring resolution of 0.5°C is not converted into a statistical error bar. High R² with three temperatures is not evidence of broad predictive accuracy.

Tests verify known synthetic Arrhenius data, rate normalization, approximate reproduction of published summaries, metadata and discrepancy handling. The 1% rate/half-life and 0.15 kcal/mol energy comparison tolerances are engineering regression tolerances for rounded tables, not experimental confidence intervals.

No simulator source, film-rate defaults, exposure response, wheel or website is changed. The package's film k_ref is per normalized acid fraction, whereas solution k is per molar acid concentration. They cannot be substituted directly. Reproducing solution kinetics is not independent validation or EUV calibration.

## Run from repository root

```bash
python scripts/solution_kinetics.py
python -m unittest discover -s tests -p test_solution_kinetics.py -v
python scripts/solution_kinetics.py --output /tmp/resistsim-solution-kinetics.json
```

JSON export refuses overwrite and records source and dataset hashes, method, predictions, published comparisons and limitations. Fits operate on S1 k values; normalization checks separately compare the rounded k_prime/[acid] ratio.
