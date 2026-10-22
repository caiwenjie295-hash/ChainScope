"""Financial-caliber regressions and real tool handoff without network access."""
import asyncio
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_round2 import ratio
from probe import ROOT

class FinancialCaliberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics=json.loads((ROOT/'data/round2/financial_metrics.json').read_text(encoding='utf-8'))['metrics']

    def test_consolidated_revenue_not_product_sales(self):
        self.assertEqual(self.metrics['m.vrt.H12026.revenue']['value'],5923800000)
        self.assertNotEqual(self.metrics['m.vrt.H12026.revenue']['value'],4782500000)
        self.assertEqual(self.metrics['m.vrt.FY2025.revenue']['value'],10229900000)

    def test_cash_conversion_uses_consolidated_profit(self):
        m=self.metrics
        self.assertAlmostEqual(m['m.envicool.H12026.cash_conversion']['value'],61871999.03/196695259.71)
        self.assertNotAlmostEqual(m['m.envicool.H12026.cash_conversion']['value'],61871999.03/184767516.83)

    def test_cashflow_capex_proxy(self):
        self.assertAlmostEqual(self.metrics['m.envicool.H12026.ocf_less_cash_capex']['value'],-156537615.43)
        self.assertIn('非公司披露',self.metrics['m.envicool.H12026.ocf_less_cash_capex']['scope'])

    def test_negative_prior_cashflow_no_ordinary_growth_rate(self):
        self.assertIsNone(self.metrics['m.envicool.H12026.ocf_yoy_pct']['value'])

    def test_mixed_currency_ratio_rejected(self):
        a={'currency':'CNY','period_start':'2025-01-01','period_end':'2025-12-31','value':10}
        b={**a,'currency':'USD','value':2}
        with self.assertRaisesRegex(ValueError,'mismatch'):ratio(a,b)

    def test_mixed_period_ratio_rejected(self):
        a={'currency':'CNY','period_start':'2025-01-01','period_end':'2025-12-31','value':10}
        b={**a,'period_end':'2025-06-30','value':2}
        with self.assertRaisesRegex(ValueError,'mismatch'):ratio(a,b)

    def test_missing_or_zero_denominator_is_unknown(self):
        a={'currency':'CNY','period_start':'2025-01-01','period_end':'2025-12-31','value':10}
        self.assertIsNone(ratio(a,{**a,'value':0}))
        self.assertIsNone(ratio(a,{**a,'value':None}))

    def test_framework_executes_tool_before_output(self):
        from pydantic_ai.models.function import FunctionModel
        from pydantic_ai.messages import ModelResponse,ToolCallPart
        from round2_agents import Bank,Context,make_agent
        bank=Bank();context=Context('financial_quality','envicool',['envicool'],bank)
        source=bank.metrics['m.envicool.H12026.ocf']['source_ids'][0]
        output={'subject':'display-name-normalized-by-scheduler','summary':'现金流与利润需结合看待。','findings':[{'text':'经营现金流已取数，现金转化由代码计算。','kind':'inference','source_ids':[source],'metric_ids':['m.envicool.H12026.ocf'],'quote':None}],'missing':[],'followup_queries':[],'concept':None,'grade':None,'grade_metric_id':None}
        def respond(messages,info):
            if not context.tool_events:return ModelResponse(parts=[ToolCallPart('financial_snapshot',{'company_id':'envicool','period':'H12026'},tool_call_id='test-tool')])
            return ModelResponse(parts=[ToolCallPart('final_result',output,tool_call_id='test-output')])
        agent=make_agent('financial_quality',FunctionModel(respond))
        result=asyncio.run(agent.run('test',deps=context))
        self.assertEqual(result.output.subject,'envicool')
        self.assertEqual(context.tool_events[0]['tool'],'financial_snapshot')
        self.assertEqual(result.usage.requests,2)

if __name__=='__main__':unittest.main()
