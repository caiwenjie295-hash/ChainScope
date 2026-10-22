import json
import urllib.request
from probe import ROOT,save,now

SELECTION={
 'FinRobot':['LICENSE','NOTICE','finrobot_desktop/finrobot/engine/pipelines/equity_research.py','finrobot_desktop/finrobot/engine/pipelines/validators.py','finrobot_desktop/finrobot/engine/compute/operators/audit/currency_caliber.py','finrobot_desktop/finrobot/engine/compute/operators/audit/ttm_period.py','finrobot_desktop/finrobot/engine/compute/operators/earnings.py'],
 'TradingAgents':['LICENSE','tradingagents/agents/analysts/fundamentals_analyst.py','tradingagents/agents/researchers/bear_researcher.py'],
 'edgartools':['LICENSE.txt','edgar/financials.py']}

if __name__=='__main__':
    for project,paths in SELECTION.items():
        meta=json.loads((ROOT/f'artifacts/references/{project}.inventory.json').read_text(encoding='utf-8'))
        for path in paths:
            url=f'https://raw.githubusercontent.com/{meta["repo"]}/{meta["commit"]}/{path}'
            try:
                with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ChainScope source review'}),timeout=30) as r:text=r.read().decode()
                dest=ROOT/'artifacts/references'/project/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8')
                print(json.dumps({'repo':project,'path':path,'chars':len(text)}),flush=True)
            except Exception as e:print(json.dumps({'repo':project,'path':path,'error':type(e).__name__}),flush=True)
