"""Compare the Table 2 dose-to-clear data with the model's temperature scaling,
and tabulate fitted effective rates per (resist, PAG).

Dill C, quencher and clearing threshold are PLACEHOLDERS (see calibration.py).
"""
from resistsim.calibration import apparent_ea, fit_k_ref
from resistsim.registry import RESISTS, PAGS, E0_TABLE

print("Apparent vs literature Ea (two-temperature E0 pairs, TPS-PFBuS):")
for name in ("4a (adamantyl, reference)", "29a (tricyclo[6.3.1.0^3,9])"):
    rows = sorted((t, e) for r, p, t, e in E0_TABLE if r == name and p == "TPS-PFBuS" and e)
    (t1, e1), (t2, e2) = rows
    print(f"  {name}: apparent {apparent_ea(e1, t1, e2, t2):.1f} kcal/mol, literature {RESISTS[name].ea_kcal}")

print("\nFitted effective rate k_ref at 100 C (1/s per unit acid fraction):")
base = {}
for r, p, t, e in E0_TABLE:
    if e is None:
        print(f"  {r:30s} {p:12s} PEB {t}: no clearing up to >500 mJ/cm2"); continue
    k = fit_k_ref(e, t, RESISTS[r].ea_kcal)
    base.setdefault(r, {}).setdefault(p, []).append(k)
    print(f"  {r:30s} {p:12s} PEB {t}: E0 {e:>4} -> k_ref {k:.2e}")

print("\nk_ref relative to the PFAS PAG, same resist (mean over available PEBs):")
for r, d in base.items():
    if "TPS-PFBuS" in d:
        ref = sum(d["TPS-PFBuS"]) / len(d["TPS-PFBuS"])
        for p, ks in d.items():
            if p != "TPS-PFBuS":
                print(f"  {r}: {p} is {sum(ks) / len(ks) / ref:.3f} x TPS-PFBuS")
