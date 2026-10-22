"""Archive pinned upstream references for inspection, not execution."""
import json
import urllib.request
from probe import ROOT,save,now

def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'ChainScope-research','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(req,timeout=45) as response:return json.load(response)

if __name__=='__main__':
    for repo in ['AI4Finance-Foundation/FinRobot','TauricResearch/TradingAgents','dgunning/edgartools']:
        try:
            meta=get('https://api.github.com/repos/'+repo)
            branch=meta['default_branch'];commit=get(f'https://api.github.com/repos/{repo}/commits/{branch}')['sha']
            tree=get(f'https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1')
            paths=[v['path'] for v in tree.get('tree',[]) if v['type']=='blob']
            save('artifacts/references/'+repo.split('/')[1]+'.inventory.json',{'repo':repo,'commit':commit,'retrieved_at':now(),'license':meta.get('license'),'files':paths,'truncated':tree.get('truncated')})
            selected=[p for p in paths if (any(k in p for k in ['compute/','pipelines/','researchers/','fundamentals_analyst','financials.py','financials/','audit/']) and p.endswith('.py'))]
            print(json.dumps({'repo':repo,'commit':commit,'relevant_paths':selected[:65]}),flush=True)
        except Exception as e:print(json.dumps({'repo':repo,'error':type(e).__name__}),flush=True)
