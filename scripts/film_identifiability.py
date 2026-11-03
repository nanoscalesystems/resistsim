"""Conditional two-dose fits; no defaults changed and no EUV calibration."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from calibration_consistency import DATASET, load_evidence, predict_e0
from resistsim.bake import arrhenius_scale


def solve_c(hot_dose, cold_dose, ratio, q):
    """Solve a(hot_dose)=ratio*a(cold_dose), where a=1-exp(-C*E)-q.

    Assumes equal clearing conversion and equal bake duration.
    None means no positive finite-rate solution, not infinite measured E0.
    """
    if not all(math.isfinite(x) for x in (hot_dose, cold_dose, ratio, q)):
        raise ValueError('Inputs must be finite')
    if not 0 < hot_dose < cold_dose or not 0 < ratio < 1 or not 0 <= q < 1:
        raise ValueError('Require 0<E_hot<E_cold, 0<ratio<1, 0<=q<1')
    if q == 0 and ratio <= hot_dose/cold_dose:
        return None
    lo = -math.log1p(-q)/hot_dose
    hi = -math.log((1-q)*(1-ratio))/hot_dose
    for _ in range(120):
        mid = (lo+hi)/2
        residual = -math.expm1(-mid*hot_dose)-q-ratio*(-math.expm1(-mid*cold_dose)-q)
        if residual > 0:
            hi = mid
        else:
            lo = mid
    return (lo+hi)/2


def fit_pair(hot_dose, cold_dose, hot_c, cold_c, ea, q, threshold=.5, time_s=60):
    if not all(math.isfinite(x) for x in (hot_c, cold_c, ea, threshold, time_s)):
        raise ValueError('Inputs must be finite')
    if not -273.15 < cold_c < hot_c or ea <= 0 or time_s <= 0 or not 0 < threshold < 1:
        raise ValueError('Invalid temperature, energy, duration or threshold')
    ratio = float(arrhenius_scale(ea, cold_c, hot_c))
    c = solve_c(hot_dose, cold_dose, ratio, q)
    if c is None:
        return None
    acid = -math.expm1(-c*hot_dose)-q
    k = -math.log1p(-threshold)/(time_s*acid)/float(arrhenius_scale(ea, hot_c, 100))
    doses = [predict_e0(k, t, ea, c, q, threshold, time_s)['predicted_e0_mj_cm2'] for t in (hot_c, cold_c)]
    return {'c_cm2_mj': c, 'k_ref_per_s_per_acid_fraction': k,
            'rate_ratio_cold_to_hot': ratio, 'reconstructed_e0_mj_cm2': doses}


def diagnostic(data):
    rows = {r['id']: r for r in data['observations']}
    hot, cold = rows['liu2026-e0-02'], rows['liu2026-e0-01']
    if (hot['resist_registry_key'], hot['pag']) != (cold['resist_registry_key'], cold['pag']):
        raise ValueError('Paired observations must have the same formulation')
    scenarios = []
    for ea in (28., 33.5, 39.):
        for q in (0., .05, .10, .15):
            fit = fit_pair(hot['e0_mj_cm2'], cold['e0_mj_cm2'], hot['peb_temperature_c'],
                           cold['peb_temperature_c'], ea, q,
                           time_s=data['experimental_conditions']['peb']['time_s'])
            scenarios.append({'assumed_ea_kcal_mol': ea, 'assumed_q': q,
                              'status': 'conditional_fit' if fit else 'no_positive_finite_solution', 'fit': fit})
    return {'status': 'assumption sensitivity, not validated calibration',
            'dataset_id': data['dataset_id'], 'sources': data['sources'],
            'observations': [hot, cold], 'scenarios': scenarios,
            'assumptions': {'threshold': .5, 'equal_threshold_and_bake_duration': True,
                            'instantaneous_quenching': True,
                            'sweep_values': 'Illustrative scenarios, not confidence intervals. Only 33.5 is the solution-derived proxy.'},
            'interpretation': 'Both doses fitted; no independent validation point. No EUV or PFAS-free formulation calibration established.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional JSON report; refuses overwrite')
    args = parser.parse_args()
    report = diagnostic(load_evidence())
    report['dataset_sha256'] = hashlib.sha256(DATASET.read_bytes()).hexdigest()
    print('Conditional 265 nm two-point fits. Both doses fitted. No defaults changed.')
    print(' Ea(kcal/mol)    Q       C(cm2/mJ)       k_ref(1/s per acid fraction)')
    for row in report['scenarios']:
        fit = row['fit']
        label = f"{fit['c_cm2_mj']:12.6f}       {fit['k_ref_per_s_per_acid_fraction']:.6f}" if fit else 'No positive finite solution'
        print(f" {row['assumed_ea_kcal_mol']:10.1f}   {row['assumed_q']:.2f}   {label}")
    print('Sweep ranges are illustrative, not uncertainty bounds. See docs/film-identifiability.md.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            json.dump(report, stream, indent=2, allow_nan=False)
            stream.write('\n')


if __name__ == '__main__':
    main()
