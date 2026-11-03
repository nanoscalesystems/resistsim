# Step 3: what two clearing doses can identify

This is a conditional sensitivity calculation, not a validated calibration.
No resistsim defaults or website files change. Requires Step 1's evidence dataset
and calibration_consistency.py. Step 2 remains the separate solution-kinetics evidence.

## Evidence and scope

Source: Liu et al., https://doi.org/10.1039/d6sc03643k, main Table 2;
SI1 Section 7.2/Fig. S11 for processing and Section 4/Tables S1–S3 for solution kinetics.
Exact source locators and reviewed PDF hashes remain in the Step 1 and Step 2 JSON files.
We reuse Step 1 observations liu2026-e0-02 and -01: 4a/TPS-PFBuS,
25 mJ/cm² at 100°C and 110 mJ/cm² at 90°C, both with 60 s PEB, 265 nm exposure.
This pair uses a PFAS-containing PAG. It does not calibrate a PFAS-free formulation or EUV response.
No new experimental measurements have been added in Step 3.

## Derivation

Let the generated acid fraction be 1-exp(-C E). After instantaneous neutralization,
a(E)=max(1-exp(-C E)-Q,0). The uniform model gives
D(E,T)=1-exp(-k_ref s(T) t a(E)), with s(T) the Arrhenius rate multiplier.
At a common clearing conversion D_clear and equal bake durations:

    a(25) = r a(110), where r=k(90°C)/k(100°C).

The clearing threshold cancels from this equation. For fixed Q and activation
energy, solve it for C by bisection, then reconstruct k_ref from the hot observation.
Both measured doses are used to fit: neither is a held-out validation point.
The chosen threshold still rescales the fitted k_ref, so its cancellation does not
make the reaction rate independently measured.

For Q>0 the positive solution lies between -ln(1-Q)/25 and
-ln((1-Q)(1-r))/25. For Q=0 a positive finite-rate solution requires r>25/110;
the algebraic C=0 root is excluded because it generates no acid.

## Assumptions versus measurements

The sweep Q=0, 0.05, 0.10, 0.15 is illustrative. These are effective neutralization
fractions, not additional experimental formulations. Q=0.10 maps nominal TOA/PAG
loading to immediate acid subtraction, which remains an assumption.
Ea=33.5 kcal/mol is the solution-derived monomer proxy already used in Step 1;
28 and 39 kcal/mol are illustrative sensitivity values, not measured film energies
or confidence limits. The simulator's gas constant is retained for consistency.
D_clear=0.5 is assumed, not measured. Solution rates in L mol^-1 s^-1 cannot be
copied into rates per normalized acid fraction without concentration and phase mapping.

At Ea=33.5, changing Q from 0.05 to 0.10 to 0.15 yields C approximately
0.010729, 0.014212 and 0.017378 cm²/mJ respectively, all fitting both doses.
This is non-identifiability when Q is unknown, not three independent confirmations.
For Q=0.10 and the assumed threshold, k_ref is about 0.058044 s^-1 per acid fraction.
Do not install this as a physical default.

## Missing evidence and useful next measurements

These are gaps in our current calibration evidence, not claims that no literature exists.

| Missing constraint | Useful data for the same formulation | What it helps separate |
|---|---|---|
| Photoacid generation | Acid yield versus dose, with wavelength and normalization | C from thermal reaction rate |
| Film kinetics | Deprotection versus time at multiple temperatures and documented exposure | Effective rate and film activation energy |
| Development endpoint | Remaining thickness/dissolution versus measured deprotection | Clearing threshold from chemical conversion |
| Quenching and acid loss | Controlled base-loading series or independent acid/base measurements | Effective Q from generated acid |
| Uncertainty | Replicates, dose spacing, error estimates, thickness and processing variation | Parameter precision and model mismatch |
| Independent validation | Additional temperatures/times not used in fitting | Predictive performance |

Raw numeric curves from the authors would be preferable. Digitized plots should
retain figure/panel identifiers and extraction uncertainty. Do not assign zero
uncertainty to missing error bars. A third clearing dose can test a fixed-assumption
fit, but does not by itself identify every kinetic and development parameter.
Full-model failure probabilities and EUV dose claims remain outside this patch.

## Checks

Seven tests cover synthetic parameter recovery, reconstruction of both doses,
threshold/rate degeneracy, multiple Q solutions, the Q=0 feasibility boundary,
duration scaling and invalid inputs. Passing confirms implementation consistency,
not empirical validity of the underlying film model.
