from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(r'D:/work/image/designs/creature-combat-20261005/pets/02-jiangling')
rows=[];seen={}
for a,n in [('hit',6),('attack',12)]:
 for i in range(1,n+1):
  p=R/'runtime'/a/'W'/f'{i:02}.png'
  im=Image.open(p); digest=hashlib.sha256(p.read_bytes()).hexdigest()
  rec=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
  alpha=im.getchannel('A')
  rows.append({'file':p.relative_to(R).as_posix(),'sha256':digest,'size':list(im.size),'mode':im.mode,'alphaExtrema':list(alpha.getextrema()),'bbox':list(alpha.getbbox()),'recordShaMatches':digest==rec['sha256'],'recordPath':str(Path(str(p)+'.generation.json').relative_to(R)),'actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality'),'duplicateOf':seen.get(digest)})
  seen[digest]=str(p)
res={'scope':'W hit6 + attack12 only','count':len(rows),'passed':len(rows)==18 and all(x['size']==[1024,1024] and x['mode']=='RGBA' and x['alphaExtrema']==[0,255] and x['recordShaMatches'] and x['duplicateOf'] is None for x in rows),'files':rows,'nativeUniformResize':'1254 square to1024 square Lanczos full canvas; no per-frame alignment','clientVerified':False}
(R/'qa'/'W-hit-attack-technical.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'count':res['count'],'passed':res['passed'],'bbox_extrema':{'minLeft':min(x['bbox'][0] for x in rows),'minTop':min(x['bbox'][1] for x in rows),'maxRight':max(x['bbox'][2] for x in rows),'maxBottom':max(x['bbox'][3] for x in rows)}}))

