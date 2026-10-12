import json,sys,re
from pathlib import Path
p=Path(sys.argv[1]);rows=p.read_text(encoding='utf-8').splitlines()[-120:]
for line in rows:
 if not any(s in line for s in ['p01_01.resume-20261012-v03','code-mode host closed','image_gen__imagegen','imagegen']):continue
 d=json.loads(line);v=d.get('payload',{});out={'timestamp':d.get('timestamp'),'type':d.get('type'),'payloadType':v.get('type'),'name':v.get('name'),'call_id':v.get('call_id')}
 for k in ['output','arguments','message']:
  value=v.get(k)
  if isinstance(value,str):out[k]=value[:1200]
 out['imagePaths']=re.findall(r'exec-[a-z0-9-]+\.png',line)
 print(json.dumps(out,ensure_ascii=False))
