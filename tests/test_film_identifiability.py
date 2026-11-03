import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from film_identifiability import fit_pair, solve_c, diagnostic, load_evidence
from calibration_consistency import predict_e0


class FilmIdentifiabilityTests(unittest.TestCase):
    def test_synthetic_parameter_recovery(self):
        c, k, ea, q = .012, .12, 30., .08
        doses = [predict_e0(k,t,ea,c,q,.5,60)['predicted_e0_mj_cm2'] for t in (100,90)]
        fit = fit_pair(*doses,100,90,ea,q)
        self.assertAlmostEqual(fit['c_cm2_mj'],c,places=12)
        self.assertAlmostEqual(fit['k_ref_per_s_per_acid_fraction'],k,places=12)

    def test_all_feasible_scenarios_reproduce_both_observations(self):
        for row in diagnostic(load_evidence())['scenarios']:
            if row['fit']:
                for actual,expected in zip(row['fit']['reconstructed_e0_mj_cm2'],(25,110)):
                    self.assertAlmostEqual(actual,expected,places=8)

    def test_threshold_changes_rate_not_c(self):
        a = fit_pair(25,110,100,90,33.5,.1,.2)
        b = fit_pair(25,110,100,90,33.5,.1,.8)
        self.assertEqual(a['c_cm2_mj'],b['c_cm2_mj'])
        self.assertAlmostEqual(b['k_ref_per_s_per_acid_fraction']/a['k_ref_per_s_per_acid_fraction'],math.log(.2)/math.log(.8))

    def test_quencher_nonidentifiability(self):
        fits = [fit_pair(25,110,100,90,33.5,q) for q in (.05,.1,.15)]
        self.assertEqual(len({f['c_cm2_mj'] for f in fits}),3)
        for f in fits:
            self.assertAlmostEqual(f['reconstructed_e0_mj_cm2'][1],110,places=8)

    def test_zero_quencher_feasibility_boundary(self):
        self.assertIsNone(solve_c(25,110,25/110,0))
        self.assertIsNone(solve_c(25,110,.2,0))
        self.assertGreater(solve_c(25,110,.3,0),0)
        self.assertGreater(solve_c(25,110,.2,.1),0)

    def test_duration_scales_rate(self):
        a = fit_pair(25,110,100,90,33.5,.1,time_s=60)
        b = fit_pair(25,110,100,90,33.5,.1,time_s=120)
        self.assertEqual(a['c_cm2_mj'],b['c_cm2_mj'])
        self.assertAlmostEqual(a['k_ref_per_s_per_acid_fraction'],2*b['k_ref_per_s_per_acid_fraction'])

    def test_invalid_inputs(self):
        for args in [(0,110,.3,.1),(110,25,.3,.1),(25,110,1,.1),(25,110,.3,-.1),(25,110,math.nan,.1)]:
            with self.assertRaises(ValueError):
                solve_c(*args)
        with self.assertRaises(ValueError):
            fit_pair(25,110,90,100,33.5,.1)


if __name__ == '__main__':
    unittest.main()
