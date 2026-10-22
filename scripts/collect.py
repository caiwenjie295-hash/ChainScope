"""Cached source collection. Credentials are read only at request time."""
import concurrent.futures
import hashlib
import json
import os
import sys
from pathlib import Path
from probe import ROOT, CREDENTIALS, now, save, request

class MCP:
    def __init__(self, server):
        cfg = json.loads((CREDENTIALS/'iFinD MCP.txt').read_text(encoding='utf-8-sig'))['mcpServers'][server]
        self.url = cfg['url']
        self.headers = {'Authorization':os.getenv('IFIND_API_KEY') or cfg['headers']['Authorization'],'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
        data, rh, meta = request(self.url, {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'chainscope','version':'0.1.0'}}}, self.headers)
        if 'result' not in data:
            raise RuntimeError('MCP initialize failed: '+str(meta))
        sid = next((v for k,v in rh.items() if k.lower()=='mcp-session-id'),None)
        if sid: self.headers['Mcp-Session-Id'] = sid
        self.headers['MCP-Protocol-Version'] = data['result']['protocolVersion']
        request(self.url,{'jsonrpc':'2.0','method':'notifications/initialized'},self.headers)

    def call(self, name, args):
        return request(self.url,{'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':name,'arguments':args}},self.headers,timeout=100)

def job(item):
    out = ROOT/'artifacts/raw'/f"{item['id']}.json"
    if out.exists() and not item.get('refresh'):
        return {'id':item['id'],'status':'cached'}
    if item['provider']=='fuyao':
        key = os.getenv('FUYAO_API_KEY') or (CREDENTIALS/'扶摇APIkey.txt').read_text(encoding='utf-8-sig').strip()
        data,_,meta = request('https://fuyao.aicubes.cn'+item['path'],headers={'X-api-key':key})
    else:
        client = MCP(item['provider'])
        data,_,meta = client.call(item['tool'],item['arguments'])
    record = {'id':item['id'],'retrieved_at':now(),'request':item,'transport':meta,'response':data}
    record['payload_sha256'] = hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    save(f"artifacts/raw/{item['id']}.json",record)
    return {'id':item['id'],'status':meta,'bytes':len(json.dumps(data)),'is_error':data.get('result',{}).get('isError',False)}

if __name__=='__main__':
    jobs = json.loads(Path(sys.argv[1] if len(sys.argv)>1 else ROOT/'config/collection_jobs.json').read_text(encoding='utf-8'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(job,jobs):
            print(json.dumps(result,ensure_ascii=True),flush=True)
