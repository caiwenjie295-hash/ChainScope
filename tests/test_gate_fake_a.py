"""P0 negative gates: fake A grades and uncited numbers must be rejected."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from probe import ROOT
from validate import check_bundle
from validate_frontend import validate as validate_frontend


class FakeAGradeGates(unittest.TestCase):
    def setUp(self):
        self.r = json.loads((ROOT / 'data/company_research.json').read_text(encoding='utf-8'))
        self.s = json.loads((ROOT / 'data/sources.json').read_text(encoding='utf-8'))
        self.g = json.loads((ROOT / 'data/industry_graph.json').read_text(encoding='utf-8'))

    def test_consolidated_total_cannot_be_A(self):
        c = self.r['companies'][0]
        # metrics[0] is consolidated_total revenue for 浪潮信息
        c['assessments'][0]['grade'] = 'A'
        c['assessments'][0]['revenue_metric_id'] = c['metrics'][0]['id']
        with self.assertRaisesRegex(ValueError, 'scoped revenue'):
            check_bundle(self.r, self.s, self.g, False)

    def test_null_metric_cannot_be_A(self):
        c = self.r['companies'][0]
        null_m = next(m for m in c['metrics'] if m['value'] is None)
        c['assessments'][0]['grade'] = 'A'
        c['assessments'][0]['concept'] = '服务器'
        c['assessments'][0]['revenue_metric_id'] = null_m['id']
        with self.assertRaisesRegex(ValueError, 'scoped revenue'):
            check_bundle(self.r, self.s, self.g, False)

    def test_ai_concept_cannot_use_related_revenue_for_A(self):
        c = self.r['companies'][0]
        related = next(m for m in c['metrics'] if m['name'] == 'related_revenue')
        # Force narrow AI concept to A using parent-category revenue
        ai = next(a for a in c['assessments'] if 'AI' in a['concept'])
        ai['grade'] = 'A'
        ai['revenue_metric_id'] = related['id']
        with self.assertRaisesRegex(ValueError, 'AI concept A'):
            check_bundle(self.r, self.s, self.g, False)

    def test_snapshot_rejects_uncited_claim_digits(self):
        from export_frontend import assert_claim_citations
        snap = json.loads((ROOT / 'frontend/public/data/snapshot.json').read_text(encoding='utf-8'))
        reviewed = next(c for c in snap['companies'] if c['research_status'] == 'reviewed')
        reviewed['claims'].append({'text': '收入增长 12.3%', 'kind': 'fact', 'source_ids': []})
        with self.assertRaisesRegex(ValueError, 'source_ids'):
            assert_claim_citations(snap['companies'])
        with self.assertRaisesRegex(ValueError, 'source_ids'):
            validate_frontend(snap)


if __name__ == '__main__':
    unittest.main()
