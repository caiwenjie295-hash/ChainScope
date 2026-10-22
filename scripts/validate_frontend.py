"""Check the user-visible data boundary, references, scope and release fingerprint."""
import hashlib
import json
from probe import ROOT,save,now

def validate(data):
    checks=0
    def require(condition,message):
        nonlocal checks
        checks+=1
        if not condition:raise ValueError(message)
    companies={c['id']:c for c in data['companies']};sources=data['sources']
    require(len(companies)==len(data['companies']),'duplicate company id')
    require(data['meta']['mode']=='offline_snapshot','misleading live mode')
    require(data['meta']['deep_companies']==sum(c['research_status']=='reviewed' for c in companies.values()),'research count mismatch')
    coverage=data['overview']['coverage']
    require(coverage['total']==len(companies),'coverage total mismatch')
    require(coverage['revenue_evidence_denominator']==coverage['researched'],'evidence denominator mismatch')
    require(coverage['scoped_revenue_evidence_count']==sum(c['assessment']['grade']=='A' for c in companies.values() if c['research_status']=='reviewed'),'A scope count mismatch')
    require(coverage['validated_impact_paths']==0,'scenario presented as verified path')
    def refs(items):
        for sid in items:require(sid in sources,'missing source: '+sid)
    for c in companies.values():
        refs(c['source_ids']);refs(c['assessment']['source_ids'])
        require(c['assessment']['grade'] in 'ABCDE','invalid grade')
        if c['research_status']=='candidate':
            require(c['assessment']['grade']=='E' and not c['metrics'] and not c['claims'],'candidate presented as researched')
        for m in c['metrics']:
            refs(m['source_ids'])
            require(m['value'] is not None or bool(m['missing_reason']),'unexplained missing financial value')
            require(m['value'] is None or bool(m['source_ids']),'ungrounded financial value')
            if m['name']=='ai_specific_revenue':require(m['value'] is None,'invented AI revenue')
        for claim in c['claims']:
            require(bool(claim.get('source_ids')), c['id']+': claim missing source_ids')
            refs(claim['source_ids'])
        for name in ('relevant_revenue_share','revenue_yoy','gross_margin','net_profit_yoy','gross_margin_change_pp'):
            m=c[name]
            if m is not None:
                require(m['period']==c['report_period'],'investor metric period mismatch')
                require(m['currency'] is None,'percentage mislabeled as currency')
                if name=='relevant_revenue_share':require(m['value'] is None,'parent category share used as AI share')
        for part in c['business_composition']:
            require(part['period']==c['report_period'],'composition period mismatch')
            require(part['share'] is None or 0<=part['share']<=100,'composition share outside percent scale')
            refs(part['source_ids'])
    nodes={n['id']:n for n in data['graph']['nodes']}
    for n in nodes.values():
        require(n['size']==1,'noncomparable revenue used as node size')
        require(not n['parent_id'] or n['parent_id'] in nodes,'missing graph parent')
        if n['type']=='company':require(n['company_id'] in companies,'unknown graph company')
        require(n.get('impact') in ('positive','negative','unclear'), n['id']+': bad impact')
        if n.get('impact') in ('positive','negative'):
            require(bool(n.get('impact_source_ids')), n['id']+': impact missing source_ids')
            refs(n['impact_source_ids'])
    if data.get('events'):
        require(any(e.get('id')==data['event']['id'] for e in data['events']),'primary event not in events[]')
        for ev in data['events']:
            for step in ev['steps']:
                require(step['kind'] in ('fact','inference','scenario'),'unknown statement kind')
                if step['kind']=='fact':require(bool(step['source_ids']),'unsupported event fact')
                refs(step['source_ids'])
    for edge in data['graph']['edges']:
        require(edge['source'] in nodes and edge['target'] in nodes,'dangling graph edge')
        refs(edge['source_ids'])
        require(edge['type']!='supply','unsupported supply relation')
    for pair in data['pairs']:
        require(all(cid in companies for cid in pair['company_ids']),'unknown peer')
        refs(pair['source_ids'])
        require('amount_compare_allowed' in pair, pair['id']+': missing amount_compare_allowed')
        require(pair['amount_compare_allowed'] is False, pair['id']+': bare amount compare must stay disallowed')
        if pair['id']=='envicool_vrt':
            require(pair.get('aligned_period')=='H12026', 'envicool_vrt must declare aligned H12026')
            require(pair.get('ratio_compare_allowed') is True, 'envicool_vrt ratio compare expected')
        else:
            require(pair.get('aligned_period') in (None, ''), pair['id']+': unexpected aligned_period')
    for step in data['event']['steps']:
        require(step['kind'] in ('fact','inference','scenario'),'unknown statement kind')
        if step['kind']=='fact':require(bool(step['source_ids']),'unsupported event fact')
        refs(step['source_ids'])
        # No invented elasticity percentages in event narrative.
        import re as _re
        if _re.search(r'\d+(?:\.\d+)?\s*%', step.get('text') or ''):
            require(bool(step.get('source_ids')), step['id']+': uncited percent in event step')
    for change in data['overview']['changes']:refs(change['source_ids'])
    for s in sources.values():
        require(not s['url'] or s['url'].startswith('https://'),'unsafe source URL')
        if not s['access'].startswith('public'):
            require(s['url'] is None and not s['excerpt'],'provider raw excerpt escaped local boundary')
    # This comparison specifically promises matched H1 periods and consolidated denominators.
    for cid in ('envicool','vrt'):
        cm={m['name']:m for m in companies[cid]['metrics']}
        a,b=cm['ocf'],cm['consolidated_net_profit']
        require((a['currency'],a['period_start'],a['period_end'])==(b['currency'],b['period_start'],b['period_end']),'mixed financial caliber')
        require(a['period_start']=='2026-01-01' and a['period_end']=='2026-06-30','not matched H1 period')
        require(abs(cm['cash_conversion']['value']-a['value']/b['value'])<1e-10,'wrong cash conversion denominator')
    content={**data,'meta':{k:v for k,v in data['meta'].items() if k not in ('generated_at','data_hash')}}
    digest=hashlib.sha256(json.dumps(content,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    require(data['meta']['data_hash']==digest,'snapshot fingerprint mismatch')
    return checks

if __name__=='__main__':
    path=ROOT/'frontend/public/data/snapshot.json'
    result={'checked_at':now(),'checks':validate(json.loads(path.read_text(encoding='utf-8'))),'status':'passed'}
    save('artifacts/frontend/data_validation.json',result)
    print(json.dumps(result))
