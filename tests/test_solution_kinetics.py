import importlib.util
from pathlib import Path
import unittest
import math
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('solution_kinetics',ROOT/'scripts/solution_kinetics.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class SolutionKineticsTests(unittest.TestCase):
    def test_synthetic_arrhenius_recovers_known_energy(self):
        temps=np.array([60.,80.,100.,120.]);ea=30000.
        rates=2e3*np.exp(-ea/(m.R_J*(temps+273.15)))
        fit=m.fit_arrhenius(temps,rates)
        self.assertAlmostEqual(fit['ea_kcal_mol'],ea/4184,places=9)
        self.assertAlmostEqual(fit['ln_preexponential_in_L_mol_s'],math.log(2e3),places=9)

    def test_normalization_agrees_with_rounded_table(self):
        # 1% is a transcription/rounding check, not experimental uncertainty.
        for monomer in m.load_data()['monomers']:
            for r in monomer['rates']:
                self.assertLess(abs(r['k_prime_s_inv']/r['acid_mol_L']/r['k_L_mol_s']-1),.01)

    def test_reproduces_published_summaries(self):
        for r in m.reconstruct(m.load_data())['results']:
            self.assertLess(abs(r['reconstruction']['ea_kcal_mol']-r['published_ea_kcal_mol']),.15)
            self.assertLess(abs(r['reconstruction']['half_life_90c_1M_s']/r['adopted_half_life_s']-1),.01)

    def test_actual_temperatures_and_single_trial_preserved(self):
        data={x['id']:x for x in m.load_data()['monomers']}
        self.assertEqual(data['1']['rates'][1]['temperature_c'],89)
        self.assertEqual(data['13']['rates'][1]['temperature_c'],90.5)
        single=[(x['id'],r['temperature_c']) for x in data.values() for r in x['rates'] if r['replicate_count']==1]
        self.assertEqual(single,[('15a',83)])

    def test_adopted_value_and_conflict_retained(self):
        d=m.load_data();monomer=next(x for x in d['monomers'] if x['id']=='13')
        self.assertEqual(monomer['adopted_half_life_s'],1222.2)
        self.assertEqual(d['discrepancy']['alternative_main_table2'],1122)

    def test_invalid_inputs(self):
        for t,k in [([83,90,100],[1,0,2]),([83,83,100],[1,2,3]),([83,90,100],[1,float('nan'),2])]:
            with self.assertRaises(ValueError):m.fit_arrhenius(t,k)


if __name__=='__main__':unittest.main()
