"""Download primary disclosures, preserve bytes/hash and extract text with page markers."""
import concurrent.futures
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import urllib.request
from probe import ROOT, now, save

class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','div','tr','td','li','h1','h2','h3'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def fetch(item):
    folder=ROOT/'artifacts/public'; folder.mkdir(parents=True,exist_ok=True)
    target=folder/(item['id']+('.pdf' if item['url'].lower().endswith('.pdf') else '.html'))
    meta_path=folder/(item['id']+'.meta.json')
    if meta_path.exists(): return {'id':item['id'],'status':'cached'}
    try:
        req=urllib.request.Request(item['url'],headers={'User-Agent':'Mozilla/5.0 ChainScope research contact local-user'})
        with urllib.request.urlopen(req,timeout=60) as r:
            raw=r.read(); final=r.url; status=r.status
        target.write_bytes(raw)
        if raw.startswith(b'%PDF'):
            from pypdf import PdfReader
            pages=PdfReader(target).pages
            text='\n\n'.join(f'\n[PDF PAGE {i+1}]\n'+(p.extract_text() or '') for i,p in enumerate(pages))
            count=len(pages)
        else:
            parser=Text();parser.feed(raw.decode('utf-8',errors='replace'))
            text=re.sub(r'[ \t]+',' ',''.join(parser.parts));text=re.sub(r'\n\s*\n','\n',text);count=None
        (folder/(item['id']+'.txt')).write_text(text,encoding='utf-8')
        meta={**item,'retrieved_at':now(),'final_url':final,'http_status':status,'sha256':hashlib.sha256(raw).hexdigest(),'pages':count,'text_chars':len(text)}
        save('artifacts/public/'+item['id']+'.meta.json',meta)
        return {'id':item['id'],'status':status,'text_chars':len(text),'pages':count}
    except Exception as e:
        save('artifacts/public/'+item['id']+'.failure.json',{'id':item['id'],'url':item['url'],'error':type(e).__name__,'checked_at':now()})
        return {'id':item['id'],'error':type(e).__name__}

if __name__=='__main__':
    jobs=json.loads(Path(sys.argv[1] if len(sys.argv)>1 else ROOT/'config/public_sources.json').read_text(encoding='utf-8'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(fetch,jobs):print(json.dumps(result),flush=True)
