"""Read-only, source-traceable diagnostic. Does not update simulation defaults."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

from resistsim.bake import arrhenius_scale
from resistsim.calibration import fit_k_ref
from resistsim.registry import E0_TABLE

DATASET = Path(__file__).resolve().parents[1] / 'data/experiments/liu2026_265nm_e0.json'


def load_evidence(path=DATASET):
    data = json.loads(Path(path).read_text())
    rows = data['observations']
    ids = [r['id'] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate observation IDs')
    extracted = [(r['resist_registry_key'], r['pag'], r['peb_temperature_c'], r['e0_mj_cm2']) for r in rows]
    if sorted(extracted) != sorted(E0_TABLE):
        raise ValueError('Evidence and installed resistsim.registry disagree. Check your editable installation before fitting.')
    return data


def predict_e0(k_ref, temp_c, ea_kcal, c, quencher, d_clear, time_s):
    """Invert the uniform-exposure model. None means no finite clearing dose."""
    values = (k_ref, temp_c, ea_kcal, c, quencher, d_clear, time_s)
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Inputs must be finite')
    if k_ref <= 0 or c <= 0 or time_s <= 0 or temp_c <= -273.15:
        raise ValueError('Rate, C and duration must be positive; temperature above absolute zero')
    if not 0 <= quencher < 1 or not 0 < d_clear < 1:
        raise ValueError('Invalid quencher or clearing fraction')
    k = k_ref * float(arrhenius_scale(ea_kcal, temp_c, 100.0))
    required = quencher - math.log1p(-d_clear) / (k * time_s)
    return {'required_generated_acid_fraction': required,
            'predicted_e0_mj_cm2': -math.log1p(-required) / c if required < 1 else None,
            'status': 'finite' if required < 1 else 'no_finite_clearing_dose'}


def diagnostic(data):
    by_id = {r['id']: r for r in data['observations']}
    reference, comparison = by_id['liu2026-e0-02'], by_id['liu2026-e0-01']
    a = data['model_assumptions']
    ea = a['activation_energy_kcal_mol']['value']
    q = a['quencher_fraction']['value']
    threshold = a['clearing_deprotected_fraction']['value']
    duration = data['experimental_conditions']['peb']['time_s']
    e_ref = reference['e0_mj_cm2']
    ratio = float(arrhenius_scale(ea, comparison['peb_temperature_c'], reference['peb_temperature_c']))
    rows = []
    for c in a['c_cm2_mj']['values']:
        k = float(fit_k_ref(e_ref, reference['peb_temperature_c'], ea, c=c,
                           quencher=q, d_clear=threshold, time_s=duration))
        fit = predict_e0(k, reference['peb_temperature_c'], ea, c, q, threshold, duration)
        predicted = predict_e0(k, comparison['peb_temperature_c'], ea, c, q, threshold, duration)
        pred = predicted['predicted_e0_mj_cm2']
        rows.append({'assumed_c_cm2_mj': c, 'fitted_k_ref_per_s_per_acid_fraction': k,
                     'reference_reconstructed_e0_mj_cm2': fit['predicted_e0_mj_cm2'],
                     **predicted, 'comparison_error_mj_cm2': None if pred is None else pred-comparison['e0_mj_cm2']})
    return {'dataset_id': data['dataset_id'], 'status': 'conditional sensitivity diagnostic; not validated calibration',
            'reference_observation': reference, 'comparison_observation': comparison,
            'assumptions': a, 'peb_time_s': duration, 'rate_ratio_90_to_100': ratio,
            'necessary_c_interval_cm2_mj': {'lower_exclusive': -math.log1p(-q)/e_ref,
                'upper_exclusive': -math.log((1-q)*(1-ratio))/e_ref,
                'meaning': 'Feasibility only for these equal-duration, equal-threshold assumptions; not a confidence interval.'},
            'sensitivity': rows, 'sources': data['sources'],
            'interpretation': 'All rows fit the reference observation. The comparison point has already informed model exploration and is not a pristine validation set. No C value is selected.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional JSON report path; refuses to overwrite an existing file.')
    args = parser.parse_args()
    data = load_evidence()
    report = diagnostic(data)
    report['dataset_sha256'] = hashlib.sha256(DATASET.read_bytes()).hexdigest()
    report['python_version'] = sys.version.split()[0]
    report['resistsim_source_sha256'] = {
        name: hashlib.sha256((Path(__import__('resistsim').__file__).parent / name).read_bytes()).hexdigest()
        for name in ('bake.py', 'calibration.py', 'registry.py')}
    print('265 nm open-frame data; NOT an EUV calibration. No defaults changed.')
    print('Reference: 4a / TPS-PFBuS, 100 C, E0=25. Comparison: 90 C, E0=110 mJ/cm2.')
    print(' C (cm2/mJ)    fitted k_ref     predicted E0 at 90 C')
    for r in report['sensitivity']:
        p = r['predicted_e0_mj_cm2']
        label = f'{p:.2f} mJ/cm2' if p is not None else 'No finite clearing dose'
        print(f" {r['assumed_c_cm2_mj']:10.3f}    {r['fitted_k_ref_per_s_per_acid_fraction']:12.6f}    {label}")
    bounds = report['necessary_c_interval_cm2_mj']
    print(f"Necessary interval: {bounds['lower_exclusive']:.6f} < C < {bounds['upper_exclusive']:.6f}")
    print('No best-fit C selected. See docs/calibration-evidence.md for scope and assumptions.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            json.dump(report, stream, indent=2, allow_nan=False)
            stream.write('\n')
        print('Report saved:', args.output)


if __name__ == '__main__':
    main()
