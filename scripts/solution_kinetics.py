"""Reconstruct solution-phase kinetics from rounded SI tables; not film calibration."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np

DATA = Path(__file__).resolve().parents[1]/'data/experiments/liu2026_solution_kinetics.json'
R_J = 8.314  # As specified in SI Equation S3.


def load_data():
    return json.loads(DATA.read_text())


def fit_arrhenius(temperatures_c, rates):
    t = np.asarray(temperatures_c, dtype=float) + 273.15
    k = np.asarray(rates, dtype=float)
    if t.ndim != 1 or k.shape != t.shape or len(t) < 3:
        raise ValueError('Need matching one-dimensional arrays with at least three points')
    if not np.isfinite(t).all() or not np.isfinite(k).all() or (t <= 0).any() or (k <= 0).any():
        raise ValueError('Temperatures and rates must be finite and physically positive')
    if np.unique(t).size < 3:
        raise ValueError('Need at least three distinct temperatures')
    x, y = 1/t, np.log(k)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope*x + intercept
    residual_sum = float(np.sum((y-fitted)**2))
    total = float(np.sum((y-y.mean())**2))
    k90 = float(np.exp(slope/363.15 + intercept))
    return {'slope_K':float(slope),'ln_preexponential_in_L_mol_s':float(intercept),
            'ea_kcal_mol':float(-slope*R_J/4184),
            'r_squared':1-residual_sum/total if total > 0 else None,
            'k90_L_mol_s':k90,'half_life_90c_1M_s':math.log(2)/k90}


def reconstruct(data):
    rows=[]
    for m in data['monomers']:
        rates=m['rates']
        fit=fit_arrhenius([r['temperature_c'] for r in rates],[r['k_L_mol_s'] for r in rates])
        checks=[{'temperature_c':r['temperature_c'],
                 'k_from_rounded_kprime_and_acid':r['k_prime_s_inv']/r['acid_mol_L'],
                 'relative_difference_from_tabulated_k':(r['k_prime_s_inv']/r['acid_mol_L'])/r['k_L_mol_s']-1}
                for r in rates]
        rows.append({'monomer':m['id'],'reconstruction':fit,
            'published_ea_kcal_mol':m['published_ea_kcal_mol'],
            'published_ea_standard_error':m['published_ea_standard_error'],
            'adopted_half_life_s':m['adopted_half_life_s'],
            'normalization_checks':checks})
    return {'dataset_id':data['dataset_id'],'source':data['source'],'results':rows,
            'discrepancy_decision':data['discrepancy'],
            'method':'Unweighted OLS on ln(tabulated k) versus 1/T; rounded published rates, not raw replicate refitting.',
            'limitations':['No exposure coefficient C used.','No film-model parameter is updated.',
            'Reconstruction agreement is not independent experimental validation.',
            'Published fit standard errors are retained as reported, not assigned to individual rate points.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Optional JSON report; refuses overwrite')
    args=parser.parse_args()
    report=reconstruct(load_data())
    report['dataset_sha256']=hashlib.sha256(DATA.read_bytes()).hexdigest()
    print('Solution-phase reconstruction. No C, no film calibration, no defaults changed.')
    print('Monomer   Ea published / reconstructed (kcal/mol)   half-life adopted / reconstructed (s)')
    for row in report['results']:
        f=row['reconstruction']
        print(f"{row['monomer']:>7}   {row['published_ea_kcal_mol']:6.2f} / {f['ea_kcal_mol']:6.2f}                         {row['adopted_half_life_s']:7.1f} / {f['half_life_90c_1M_s']:7.1f}")
    print('Monomer 13: supplementary 1222.2 s adopted; conflicting main-table 1122 s retained in provenance.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:json.dump(report,stream,indent=2,allow_nan=False);stream.write('\n')
        print('Saved:',args.output)


if __name__=='__main__':main()
