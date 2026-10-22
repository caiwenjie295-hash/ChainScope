"""Schema, cross-file, provenance, scope and missing-value checks."""
import copy
import hashlib
import json
from pathlib import Path
import re
from probe import ROOT,save,now
from models import CONTRACTS,Research,Sources,Graph

def load(name):return json.loads((ROOT/'data'/f'{name}.json').read_text(encoding='utf-8'))

def check_bundle(research,sources,graph,verify_files=True):
    Research.model_validate(research);Sources.model_validate(sources);Graph.model_validate(graph)
    failures=[];checks=0
    def check(condition,message):
        nonlocal checks
        checks+=1
        if not condition:failures.append(message)
    companies={c['id']:c for c in research['companies']};sids={s['id'] for s in sources['sources']};nodes={n['id']:n for n in graph['nodes']}
    check(len(companies)==len(research['companies']),'duplicate company id')
    check(len(sids)==len(sources['sources']),'duplicate evidence id')
    check(len(nodes)==len(graph['nodes']),'duplicate graph node id')
    check(len({e['id'] for e in graph['edges']})==len(graph['edges']),'duplicate edge id')
    for c in companies.values():
        check(c['market']!='CN' or bool(re.fullmatch(r'\d{6}\.(SZ|SH|BJ)',c['ticker'])),c['id']+': ticker format')
        check(c['ticker']!='VRT-1.N','obsolete Vertiv instrument')
        if c['research_depth']=='deep':check(c['ai_analysis'] is not None,c['id']+': missing AI result')
        for cl in c['claims']:
            check(set(cl['source_ids'])<=sids,cl['id']+': missing claim citation')
            check(cl['kind']!='inference' or cl['verification']!='primary_checked',cl['id']+': inference presented as fact')
        metrics={m['id']:m for m in c['metrics']}
        for m in c['metrics']:
            check(set(m['source_ids'])<=sids,m['id']+': missing metric citation')
            check(m['period_end']<='2026-10-21',m['id']+': future metric')
            check(m['currency']==('CNY' if c['market']=='CN' else 'USD'),m['id']+': currency mismatch')
        for a in c['assessments']:
            check(set(a['source_ids'])<=sids,c['id']+': assessment evidence missing')
            check(a['grade'] in 'ABCDE',c['id']+': invalid grade')
            if a['grade']=='A':
                check(a.get('revenue_metric_id') in metrics,c['id']+': missing A-grade metric')
                if a.get('revenue_metric_id') in metrics:
                    metric=metrics[a['revenue_metric_id']]
                    check(metric['value'] is not None and metric['scope']!='consolidated_total',c['id']+': A-grade scoped revenue not available')
                    # Narrow AI concepts cannot use parent/group revenue to claim A (CONCEPT_GRADES P0).
                    concept=a.get('concept') or ''
                    if 'AI' in concept or 'ai' in concept.lower():
                        check(metric.get('name')=='ai_specific_revenue' and metric['value'] is not None,
                              c['id']+': AI concept A requires ai_specific_revenue, not group/parent revenue')
        for peer in c['comparisons']:
            check(peer['peer_id'] in companies,c['id']+': unknown peer')
            check(set(peer['source_ids'])<=sids,c['id']+': peer evidence missing')
        if c['ai_analysis']:
            check(c['ai_analysis']['company_id']==c['id'],c['id']+': AI identity mismatch')
            for obs in c['ai_analysis']['observations']:check(set(obs['source_ids'])<=sids,c['id']+': AI evidence missing')
    for n in nodes.values():
        check(n['parent_id'] is None or n['parent_id'] in nodes,n['id']+': missing parent')
        check(n['company_id'] is None or n['company_id'] in companies,n['id']+': missing company')
        if n['type']=='company':
            check(n['market']==companies[n['company_id']]['market'],n['id']+': inconsistent market')
    for e in graph['edges']:
        check(e['source'] in nodes and e['target'] in nodes,e['id']+': dangling edge')
        check(set(e['source_ids'])<=sids,e['id']+': unknown edge source')
        check(e['type']=='taxonomy' or len(e['source_ids'])>0,e['id']+': relation without evidence')
    if verify_files:
        for s in sources['sources']:
            p=ROOT/s['local_path'];check(p.exists(),s['id']+': local provenance missing')
            if p.exists():check(hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'],s['id']+': provenance hash mismatch')
    if failures:raise ValueError('\n'.join(failures))
    return {'status':'passed','deterministic_checks':checks,'semantic_note':'Schema和引用存在性不等于事实蕴含证明。八家公司关键业务与财务由研究者抽核，广度层AI关联待核验。'}

def validate():
    files={name:load(name) for name in CONTRACTS}
    for name,model in CONTRACTS.items():model.model_validate(files[name])
    result=check_bundle(files['company_research'],files['sources'],files['industry_graph'])
    for filename,digest in files['research_manifest']['files'].items():
        actual=hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()
        if actual!=digest:raise ValueError('manifest mismatch: '+filename)
    result['checked_at']=now();save('artifacts/validation_report.json',result)
    print(json.dumps(result,ensure_ascii=True))

if __name__=='__main__':validate()
