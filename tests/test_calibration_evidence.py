"""Evidence integrity and algebraic checks; no claim of experimental validation."""
import importlib.util
import json
import math
from pathlib import Path
import unittest

from resistsim.bake import arrhenius_scale
from resistsim.calibration import fit_k_ref

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('calibration_consistency', ROOT/'scripts/calibration_consistency.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CalibrationEvidenceTests(unittest.TestCase):
    def test_dataset_matches_registry_and_keeps_nonclear_distinct(self):
        data = module.load_evidence()
        self.assertEqual(len(data['observations']), 12)
        censored = [r for r in data['observations'] if r['observation_type']=='non_clearing_observation']
        self.assertEqual(len(censored), 2)
        for row in censored:
            self.assertIsNone(row['e0_mj_cm2'])
            self.assertIsNone(row['non_clearing']['exact_maximum_tested_dose_mj_cm2'])
        self.assertEqual(data['experimental_conditions']['exposure']['wavelength_nm'], 265)
        self.assertEqual(data['experimental_conditions']['peb']['time_s'], 60)

    def test_reference_reconstruction(self):
        report = module.diagnostic(module.load_evidence())
        for row in report['sensitivity']:
            self.assertAlmostEqual(row['reference_reconstructed_e0_mj_cm2'], 25, places=10)
        json.dumps(report, allow_nan=False)

    def test_prediction_satisfies_forward_equation(self):
        for c in [.005,.01,.015]:
            k = fit_k_ref(25,100,33.5,c=c)
            result = module.predict_e0(k,90,33.5,c,.1,.5,60)
            e = result['predicted_e0_mj_cm2']
            acid = -math.expm1(-c*e)-.1
            deprotected = -math.expm1(-k*arrhenius_scale(33.5,90,100)*acid*60)
            self.assertAlmostEqual(deprotected,.5,places=12)

    def test_unreachable_dose_is_null_not_zero(self):
        k = fit_k_ref(25,100,33.5,c=.05)
        r = module.predict_e0(k,90,33.5,.05,.1,.5,60)
        self.assertIsNone(r['predicted_e0_mj_cm2'])
        self.assertGreater(r['required_generated_acid_fraction'],1)

    def test_common_threshold_cancels_after_refit(self):
        predictions=[]
        for d in [.2,.5,.8]:
            k = fit_k_ref(25,100,33.5,c=.01,d_clear=d)
            predictions.append(module.predict_e0(k,90,33.5,.01,.1,d,60)['predicted_e0_mj_cm2'])
        for e in predictions:self.assertAlmostEqual(e,predictions[0],places=10)

    def test_feasibility_boundary(self):
        ratio=float(arrhenius_scale(33.5,90,100))
        upper=-math.log(.9*(1-ratio))/25
        for c,finite in [(upper-1e-5,True),(upper+1e-5,False)]:
            k=fit_k_ref(25,100,33.5,c=c)
            r=module.predict_e0(k,90,33.5,c,.1,.5,60)
            self.assertEqual(r['predicted_e0_mj_cm2'] is not None,finite)

    def test_invalid_inputs_rejected(self):
        for c in [0,-1,float('nan')]:
            with self.assertRaises(ValueError):module.predict_e0(.05,90,33.5,c,.1,.5,60)

    def test_registry_mismatch_detected(self):
        import tempfile
        data = module.load_evidence()
        data['observations'][0]['e0_mj_cm2']=111
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'bad.json';path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'disagree'):module.load_evidence(path)


if __name__ == '__main__':
    unittest.main()
