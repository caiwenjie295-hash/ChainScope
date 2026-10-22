"""Protect user-facing financial, evidence, candidate and release boundaries."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from probe import ROOT
from validate_frontend import validate

class FrontendBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'frontend/public/data/snapshot.json').read_text(encoding='utf-8'))
    def test_export_is_consistent(self):
        self.assertGreater(validate(self.data),100)
    def test_missing_evidence_rejected(self):
        self.data['sources'].pop(next(iter(self.data['sources'])))
        with self.assertRaisesRegex(ValueError,'missing source'):validate(self.data)
    def test_unverified_candidate_cannot_show_financials(self):
        candidate=next(c for c in self.data['companies'] if c['research_status']=='candidate')
        candidate['metrics']=copy.deepcopy(self.data['companies'][0]['metrics'])
        with self.assertRaisesRegex(ValueError,'candidate'):validate(self.data)
    def test_group_revenue_cannot_become_ai_revenue(self):
        m=next(m for c in self.data['companies'] for m in c['metrics'] if m['name']=='ai_specific_revenue')
        m['value']=10
        with self.assertRaisesRegex(ValueError,'invented AI'):validate(self.data)
    def test_parent_profit_denominator_rejected(self):
        c=next(c for c in self.data['companies'] if c['id']=='envicool')
        ms={m['name']:m for m in c['metrics']}
        ms['cash_conversion']['value']=ms['ocf']['value']/ms['parent_net_profit']['value']
        with self.assertRaisesRegex(ValueError,'denominator'):validate(self.data)
    def test_data_tampering_rejected(self):
        self.data['companies'][0]['headline']='tampered'
        with self.assertRaisesRegex(ValueError,'fingerprint'):validate(self.data)
    def test_quarterly_margin_not_used_as_full_year(self):
        c=next(c for c in self.data['companies'] if c['id']=='smci')
        self.assertEqual(c['gross_margin']['period'],'FY2025')
        self.assertAlmostEqual(c['gross_margin']['value'],2429922/21972042*100)
        self.assertNotAlmostEqual(c['gross_margin']['value'],9.5)
    def test_parent_category_not_ai_exposure(self):
        c=next(c for c in self.data['companies'] if c['id']=='envicool')
        self.assertIsNone(c['relevant_revenue_share']['value'])
        self.assertAlmostEqual(c['business_composition'][0]['share'],1700144828.46/3016714649.18*100)
        self.assertEqual(c['gross_margin_change_pp']['value'],-1.22)
    def test_new_investor_metric_mixed_period_rejected(self):
        c=next(c for c in self.data['companies'] if c['id']=='envicool')
        c['gross_margin']['period']='FY2025'
        with self.assertRaisesRegex(ValueError,'period mismatch'):validate(self.data)
    def test_income_coverage_excludes_parent_categories_and_paths_exclude_scenarios(self):
        cv=self.data['overview']['coverage']
        self.assertEqual(cv['scoped_revenue_evidence_count'],0)
        # P1 EDITED set was 8; P2 deep.b1c snapshot coverage.researched/denominator is 9.
        # Assertion tracks the exported coverage field (not a hard-coded company roster).
        self.assertEqual(cv['revenue_evidence_denominator'],9)
        self.assertEqual(cv['revenue_evidence_denominator'],cv['researched'])
        self.assertEqual(cv['validated_impact_paths'],0)
        self.assertEqual(cv['conditional_impact_cases'],1)

if __name__=='__main__':unittest.main()
