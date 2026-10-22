"""Read local credentials without printing or persisting them; probe real providers."""
import concurrent.futures
import datetime as dt
import json
import os
from pathlib import Path
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
CREDENTIALS = ROOT.parent / 'API及接口'

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def save(path, data):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def request(url, body=None, headers=None, timeout=55):
    payload = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=payload, headers=headers or {})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode('utf-8', errors='replace')
            meta = {'http_status': r.status, 'elapsed_seconds': round(time.perf_counter()-started, 3)}
            if raw.lstrip().startswith('event:') or raw.lstrip().startswith('data:'):
                candidates = [json.loads(line[5:].strip()) for line in raw.splitlines() if line.startswith('data:') and line[5:].strip() != '[DONE]']
                data = candidates[-1] if candidates else {}
            else:
                data = json.loads(raw) if raw else {}
            return data, dict(r.headers), meta
    except urllib.error.HTTPError as e:
        # Do not print response bodies: providers may echo sensitive request details.
        return {}, {}, {'http_status': e.code, 'error': 'HTTPError', 'elapsed_seconds': round(time.perf_counter()-started, 3)}
    except Exception as e:
        return {}, {}, {'http_status': None, 'error': type(e).__name__, 'elapsed_seconds': round(time.perf_counter()-started, 3)}

def ifind(server):
    config = json.loads((CREDENTIALS/'iFinD MCP.txt').read_text(encoding='utf-8-sig'))['mcpServers'][server]
    key = os.getenv('IFIND_API_KEY') or config['headers']['Authorization']
    headers = {'Authorization': key, 'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
    init, rh, meta = request(config['url'], {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'chainscope-research','version':'0.1.0'}}}, headers)
    result = {'provider':server, 'checked_at':now(), 'initialize':meta, 'server_info':init.get('result',{}).get('serverInfo'), 'tools':[]}
    if 'result' in init:
        sid = next((v for k,v in rh.items() if k.lower()=='mcp-session-id'), None)
        if sid:
            headers['Mcp-Session-Id'] = sid
        headers['MCP-Protocol-Version'] = init['result'].get('protocolVersion','2024-11-05')
        request(config['url'], {'jsonrpc':'2.0','method':'notifications/initialized'}, headers)
        listing, _, lm = request(config['url'], {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}}, headers)
        result['list_tools'] = lm
        result['tools'] = listing.get('result',{}).get('tools',[])
        result['rpc_error'] = listing.get('error')
    save(f'artifacts/connectivity/{server}.json',result)
    return {'provider':server,'status':meta,'tools_count':len(result['tools'])}

def deepseek():
    from model_adapter import get_profile, resolve_api_key, require_chat_endpoint
    profile = require_chat_endpoint(get_profile('deepseek'))
    key = resolve_api_key(profile)
    headers = {'Authorization':'Bearer '+key,'Content-Type':'application/json'}
    models, _, meta = request(profile['base_url'].rstrip('/') + '/models', headers=headers)
    result = {'provider':'deepseek','checked_at':now(),'models_request':meta,'models':[v['id'] for v in models.get('data',[])]}
    if meta.get('http_status') == 200:
        body = {'model':profile['model'],'thinking':{'type':'disabled'},'max_tokens':120,'response_format':{'type':'json_object'},'messages':[{'role':'user','content':'Return JSON only: {"status":"ok","rule":"Missing financial values stay null; never invent evidence."}'}]}
        chat,_,cm = request(profile['base_url'].rstrip('/') + '/chat/completions',body,headers)
        result.update(chat_request=cm, usage=chat.get('usage'), model=chat.get('model'), response=chat.get('choices',[{}])[0].get('message',{}).get('content'))
    save('artifacts/connectivity/deepseek.json',result)
    return result

if __name__ == '__main__':
    servers = ['hexin-ifind-ds-mcp','hexin-ifind-ds-stock-mcp','hexin-ifind-ds-global-stock-mcp','hexin-ifind-ds-news-mcp']
    # Low concurrency across independent provider endpoints.
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(ifind,servers))
    results.append(deepseek())
    fy = (CREDENTIALS/'扶摇APIkey.txt').read_text(encoding='utf-8-sig').strip()
    results.append({'provider':'fuyao','status':'not_tested_missing_key' if not fy and not os.getenv('FUYAO_API_KEY') else 'key_present'})
    save('artifacts/connectivity/summary.json',results)
    print(json.dumps(results,ensure_ascii=True,indent=2))
