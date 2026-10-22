import json
import urllib.parse
import urllib.request
from probe import ROOT,save,now

if __name__=='__main__':
    body=urllib.parse.urlencode({'pageNum':1,'pageSize':30,'column':'szse','tabName':'fulltext','stock':'000977','searchkey':'2025年年度报告','secid':'','plate':'','category':'','trade':'','seDate':'2026-04-01~2026-04-30','sortName':'time','sortType':'desc','isHLtitle':'true'}).encode()
    req=urllib.request.Request('https://www.cninfo.com.cn/new/hisAnnouncement/query',data=body,headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/x-www-form-urlencoded','Referer':'https://www.cninfo.com.cn/'})
    with urllib.request.urlopen(req,timeout=30) as r:data=json.load(r)
    save('artifacts/discovery/inspur_reports.json',data)
    print(json.dumps([{'title':a['announcementTitle'],'url':'https://static.cninfo.com.cn/'+a['adjunctUrl']} for a in (data.get('announcements') or [])],ensure_ascii=True))
