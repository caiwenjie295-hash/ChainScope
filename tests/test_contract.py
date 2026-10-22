import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from models import Research
from probe import ROOT
from validate import check_bundle
from run_agent import validate_numeric,validate_result

class ResearchSafetyTests(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((ROOT/'data/company_research.json').read_text(encoding='utf-8'))
        self.s=json.loads((ROOT/'data/sources.json').read_text(encoding='utf-8'))
        self.g=json.loads((ROOT/'data/industry_graph.json').read_text(encoding='utf-8'))

    def test_real_bundle(self):check_bundle(self.r,self.s,self.g)
    def test_dangling_citation_rejected(self):
        self.r['companies'][0]['claims'][0]['source_ids']=['nonexistent']
        with self.assertRaisesRegex(ValueError,'citation'):check_bundle(self.r,self.s,self.g,False)
    def test_null_without_reason_rejected(self):
        self.r['companies'][0]['metrics'][0]['value']=None
        with self.assertRaises(ValueError):Research.model_validate(self.r)
    def test_total_revenue_cannot_prove_concept_A(self):
        c=self.r['companies'][0];c['assessments'][0]['revenue_metric_id']=c['metrics'][0]['id']
        with self.assertRaisesRegex(ValueError,'scoped revenue'):check_bundle(self.r,self.s,self.g,False)
    def test_missing_company_edge_rejected(self):
        self.g['edges'][0]['target']='unknown'
        with self.assertRaisesRegex(ValueError,'dangling edge'):check_bundle(self.r,self.s,self.g,False)
    def test_obsolete_instrument_rejected(self):
        self.r['companies'][0]['ticker']='VRT-1.N'
        with self.assertRaisesRegex(ValueError,'obsolete'):check_bundle(self.r,self.s,self.g,False)
    def test_new_numeric_estimate_rejected(self):
        with self.assertRaisesRegex(ValueError,'numeric'):validate_numeric('AI收入增长50%','证据未披露AI收入')
    def test_grounded_technical_identifier_allowed(self):validate_numeric('已有1.6T产品收入发货','Commenced revenue shipments of 1.6T transceiver products')
    def test_unsupported_technical_identifier_rejected(self):
        with self.assertRaisesRegex(ValueError,'technical'):validate_numeric('已有9.6T产品','1.6T products')
    def test_tampered_source_rejected(self):
        self.s['sources'][0]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'hash mismatch'):check_bundle(self.r,self.s,self.g)

if __name__=='__main__':unittest.main()
