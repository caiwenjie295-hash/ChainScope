"""Version 0.1 data contract. Pydantic is used for validation, not financial inference."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Model(BaseModel):
    model_config=ConfigDict(extra='forbid', allow_inf_nan=False)

class Evidence(Model):
    id:str
    title:str
    provider:str
    source_type:Literal['annual_report','earnings_release','api_financial','api_profile','notice_excerpt','product_release','concept_catalog','concept_constituents']
    url:str|None
    published_at:str|None
    retrieved_at:str
    local_path:str
    sha256:str
    locator:str
    excerpt:str
    excerpt_kind:Literal['original','analyst_transcription']='original'
    access:Literal['public_verified','authenticated_api','excerpt_only']
    limitations:list[str]

class Sources(Model):
    schema_version:Literal['0.1.0']='0.1.0'
    sources:list[Evidence]

class Claim(Model):
    id:str
    text:str
    kind:Literal['fact','inference','scenario']
    source_ids:list[str]=Field(min_length=1)
    verification:Literal['primary_checked','provider_only','analyst_inference','pending']
    limitations:list[str]

class Metric(Model):
    id:str
    name:str
    value:float|None
    unit:Literal['currency_units','percent','per_share']
    currency:Literal['CNY','USD']|None
    period:str
    period_start:str
    period_end:str
    scope:str
    accounting_basis:Literal['CAS','US_GAAP','not_applicable']
    disclosure_status:str
    source_ids:list[str]=Field(min_length=1)
    missing_reason:str|None
    @model_validator(mode='after')
    def missing(self):
        if self.value is None and not self.missing_reason: raise ValueError('null metric needs missing_reason')
        if self.value is not None and self.missing_reason is not None: raise ValueError('non-null metric cannot have missing_reason')
        if self.period_end < self.period_start: raise ValueError('invalid period')
        if self.unit in ('currency_units','per_share') and not self.currency: raise ValueError('currency required')
        return self

class Assessment(Model):
    concept:str
    grade:Literal['A','B','C','D','E']
    rationale:str
    revenue_metric_id:str|None
    source_ids:list[str]=Field(min_length=1)
    limitations:list[str]

class Comparison(Model):
    peer_id:str
    comparable:list[str]=Field(min_length=1)
    non_comparable:list[str]=Field(min_length=1)
    source_ids:list[str]=Field(min_length=1)

class Observation(Model):
    text:str
    kind:Literal['fact','inference']
    source_ids:list[str]=Field(min_length=1)

class AIAnalysis(Model):
    company_id:str
    summary:str
    observations:list[Observation]=Field(min_length=1,max_length=4)
    uncertainties:list[str]=Field(min_length=1)

class Company(Model):
    id:str
    name:str
    ticker:str
    exchange:str
    market:Literal['CN','US']
    domicile:str
    research_depth:Literal['deep','breadth']
    business_summary:str
    claims:list[Claim]=Field(min_length=1)
    assessments:list[Assessment]
    metrics:list[Metric]
    comparisons:list[Comparison]
    uncertainties:list[str]
    ai_analysis:AIAnalysis|None
    @model_validator(mode='after')
    def grade_a(self):
        metrics={m.id:m for m in self.metrics}
        for a in self.assessments:
            if a.grade=='A' and (a.revenue_metric_id not in metrics or metrics[a.revenue_metric_id].value is None):
                raise ValueError('A grade requires non-null scoped revenue metric')
        return self

class Research(Model):
    schema_version:Literal['0.1.0']='0.1.0'
    companies:list[Company]

class Node(Model):
    id:str
    label:str
    type:Literal['theme','branch','segment','company']
    parent_id:str|None
    company_id:str|None
    market:Literal['CN','US']|None
    layer:int=Field(ge=0,le=3)
    distance_basis:str
    size:float=Field(gt=0)
    size_basis:str
    impact:Literal['positive','negative','unclear']

class Edge(Model):
    id:str
    source:str
    target:str
    type:Literal['taxonomy','industry_membership','supply','demand','technology','financial_transmission']
    kind:Literal['fact','inference','scenario']
    direction:Literal['positive','negative','unclear']
    confidence:Literal['high','medium','low']
    source_ids:list[str]
    mechanism:str
    conditions:list[str]

class Graph(Model):
    schema_version:Literal['0.1.0']='0.1.0'
    taxonomy_basis:str
    nodes:list[Node]
    edges:list[Edge]

class Evaluation(Model):
    schema_version:Literal['0.1.0']='0.1.0'
    generated_at:str
    model:str  # from config/model_registry.json active profile
    calls:list[dict]
    usage:dict
    estimated_cost_cny:dict
    failure_cases:list[dict]
    validation:dict
    comparison_experiment:Literal['not_run']='not_run'

class Manifest(Model):
    schema_version:Literal['0.1.0']='0.1.0'
    research_version:str
    topic:str
    research_as_of:str
    generated_at:str
    financial_baseline:str
    freshness_note:str
    is_mock:Literal[False]=False
    validation_status:Literal['passed_with_limitations','failed']
    company_count:int
    deep_company_count:int
    files:dict[str,str]
    limitations:list[str]

CONTRACTS={'industry_graph':Graph,'company_research':Research,'sources':Sources,'agent_evaluation':Evaluation,'research_manifest':Manifest}

if __name__=='__main__':
    from probe import save
    for name,model in CONTRACTS.items():save('schemas/'+name+'.schema.json',model.model_json_schema())
    print('Exported 5 JSON Schemas')
