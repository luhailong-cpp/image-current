from pathlib import Path
import json,sys,re
S=Path('C:/Users/luyua/.codex/sessions/2026/10/12')
ROOT='01a12076-0b9d-76b2-949d-c4cf520a83be'
for p in sorted(S.glob('*.jsonl')):
 with p.open('rb') as f:
  head=f.readline()
 if ROOT.encode() not in head: continue
 try: meta=json.loads(head)
 except: continue
 print(json.dumps({'log':str(p),'metadata':meta.get('payload',{}),'size':p.stat().st_size},ensure_ascii=False)[:4000])
 with p.open('rb') as f:
  f.seek(max(0,p.stat().st_size-12000000));raw=f.read()
 lines=raw.splitlines()
 if p.stat().st_size>12000000:lines=lines[1:]
 for line in lines[-160:]:
  if not any(x in line for x in [b'image_gen',b'Generated images are saved',b'network permission',b'code-mode host',b'RESUME_HANDOFF']):continue
  try:d=json.loads(line)
  except:continue
  v=d.get('payload',{});out={'timestamp':d.get('timestamp'),'type':d.get('type'),'payloadType':v.get('type'),'name':v.get('name'),'call_id':v.get('call_id')}
  for k in ['output','arguments','message']:
   value=v.get(k)
   if isinstance(value,str):out[k]=value[:1500]
  out['imagePaths']=list(set(re.findall(r'exec-[a-z0-9-]+\.png',line.decode('utf-8',errors='replace'))))
  print(json.dumps(out,ensure_ascii=False))
