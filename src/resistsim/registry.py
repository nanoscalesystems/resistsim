"""Sourced resist and PAG data. Every entry carries a status and a citation.

status: "literature" (published measurement), "estimated" (placeholder) or "measured" (own data).
"""
from dataclasses import dataclass

LIU2026 = "Liu et al., Chem. Sci. 2026, 17, 15458 (DOI 10.1039/d6sc03643k), SI Table S2"


@dataclass(frozen=True)
class Resist:
    name: str
    ea_kcal: float      # acid-catalysed deprotection activation energy
    ea_err: float
    status: str
    source: str
    note: str = "Ea measured on the monomer in solution (MsOH, DMSO-d6); used as a proxy for the film."


@dataclass(frozen=True)
class PAG:
    name: str
    pka: tuple          # (low, high) of the photoacid, as reported by the source
    pfas: bool
    status: str
    source: str


RESISTS = {r.name: r for r in [
    Resist("4a (adamantyl, reference)", 33.5, 0.2, "literature", LIU2026),
    Resist("27a (bicyclo[3.3.1])", 35.0, 0.4, "literature", LIU2026),
    Resist("28a (bicyclo[3.3.3])", 28.3, 0.9, "literature", LIU2026),
    Resist("29a (tricyclo[6.3.1.0^3,9])", 27.5, 0.2, "literature", LIU2026),
]}

_P = "Liu et al., Chem. Sci. 2026, 17, 15458, pKa values as quoted there (refs 48-50)"
PAGS = {p.name: p for p in [
    PAG("TPS-PFBuS", (-5.5, 0.14), True, "literature", _P + "; wide estimated range"),
    PAG("TPS-Ms", (-1.9, -1.9), False, "literature", _P),
    PAG("DTBPI-CampS", (1.2, 1.2), False, "literature", _P),
]}

# Dose-to-clear E0 (mJ/cm^2), 265 nm open-frame, 60 s PEB, 80 nm film, 10 wt% PAG, 10 mol% TOA.
# (resist, PAG, PEB degC, E0). None = film did not fully clear (tested up to >500 mJ/cm^2).
# Source: Liu et al., Chem. Sci. 2026, 17, 15458, Table 2.
E0_TABLE = [
    ("4a (adamantyl, reference)", "TPS-PFBuS", 90, 110), ("4a (adamantyl, reference)", "TPS-PFBuS", 100, 25),
    ("27a (bicyclo[3.3.1])", "TPS-PFBuS", 100, 19),
    ("28a (bicyclo[3.3.3])", "TPS-PFBuS", 80, 8),
    ("29a (tricyclo[6.3.1.0^3,9])", "TPS-PFBuS", 80, 12), ("29a (tricyclo[6.3.1.0^3,9])", "TPS-PFBuS", 90, 6),
    ("4a (adamantyl, reference)", "TPS-Ms", 120, None), ("27a (bicyclo[3.3.1])", "TPS-Ms", 120, None),
    ("28a (bicyclo[3.3.3])", "TPS-Ms", 100, 57), ("29a (tricyclo[6.3.1.0^3,9])", "TPS-Ms", 110, 59),
    ("28a (bicyclo[3.3.3])", "DTBPI-CampS", 100, 138), ("29a (tricyclo[6.3.1.0^3,9])", "DTBPI-CampS", 120, 147),
]
