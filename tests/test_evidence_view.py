import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_evidence_view import load_datasets, render, table


class EvidenceViewTests(unittest.TestCase):
    def setUp(self):
        self.data=load_datasets()

    def test_euv_roughness_types_and_conflict(self):
        d=self.data['liu2025_nonpfas_euv_gen2.json']
        self.assertEqual(len(d['observations']),4)
        for row in d['observations']:
            if row['pitch_nm']==36:
                self.assertIsNone(row['unbiased_lwr_nm'])
                self.assertIsNotNone(row['biased_lwr_nm'])
            else:
                self.assertIsNone(row['biased_lwr_nm'])
                self.assertIsNotNone(row['unbiased_lwr_nm'])
        self.assertEqual(d['discrepancies'][0]['adopted_table_value_nm'],1.75)
        self.assertEqual(d['discrepancies'][0]['conflicting_prose_value_nm'],1.85)

    def test_patterning_doses_not_clearing_doses(self):
        for name in ['liu2025_nonpfas_euv_gen2.json','lu2025_fluorine_free_iline.json']:
            for row in self.data[name]['observations']:
                self.assertNotIn('e0_mj_cm2',row)
                self.assertIsNone(row['uncertainty'])

    def test_poor_profile_is_retained(self):
        rows=self.data['lu2025_fluorine_free_iline.json']['observations']
        self.assertEqual(len(rows),17)
        poor=[r for r in rows if r['film_thickness_um']==100 and r['nominal_cd_um']==10][0]
        self.assertEqual(poor['profile_delta_cd_pct'],38.46)

    def test_existing_nonclear_and_kinetics_preserved(self):
        rows=self.data['liu2026_265nm_e0.json']['observations']
        self.assertEqual(sum(r['e0_mj_cm2'] is None for r in rows),2)
        self.assertEqual(self.data['liu2026_solution_kinetics.json']['discrepancy']['adopted'],1222.2)

    def test_html_escapes_source_and_has_three_views(self):
        self.assertIn('&lt;script&gt;',table([{'a':'<script>'}],[('a','Value')]))
        text=render(self.data)
        for name in ['patterning','chemistry','euv']:
            self.assertIn(f'id="{name}"',text)
        self.assertIn('Source conflict',text)
        self.assertIn('1222.2',text)


if __name__=='__main__':unittest.main()
