from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
import numpy as np
from PIL import Image

BASE=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
REVIEW=BASE/'parallel-review-20261013/island-game-20261009'
OUT=REVIEW/'resume-v03/west-late'
NW=BASE/'island-game-20261009/northwest'
OUT.mkdir(parents=True, exist_ok=True)
(OUT/'snapshots').mkdir(exist_ok=True)
(OUT/'crops').mkdir(exist_ok=True)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj): Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def freeze(p):
 p=Path(p); data=p.read_bytes(); dest=OUT/'snapshots'/p.name; dest.write_bytes(data)
 return {'path':str(p),'sha256':hashlib.sha256(data).hexdigest(),'snapshot':str(dest)}
snapshot=freeze(NW/'current-adopted-20261012.json')
current=read(snapshot['snapshot'])
prior=read(REVIEW/'resume-v03/west/summary.json')
old={t['tileId']:t for t in prior['tiles']}
adopted={t['tileId']:t for t in current['tiles']}
report={'frozenAtUtc':datetime.now(timezone.utc).isoformat(),'metadata':snapshot,'tiles':[],'crops':[],'sourceImages':[]}
cache={}
def img(p):
 p=str(p)
 if p not in cache:
  cache[p]=Image.open(p).convert('RGB'); report['sourceImages'].append({'path':p,'sha256':sha(p),'dimensions':list(cache[p].size)})
 return cache[p]
def savecrop(tile, name, im, box, kind, changed=None):
 path=OUT/'crops'/f'{tile}-{name}.png'; crop=im.crop(box);crop.save(path)
 o={'tileId':tile,'name':name,'kind':kind,'path':str(path),'tileBox':list(box),'dimensions':list(crop.size),'sha256':sha(path),'pixelSha256':hashlib.sha256(crop.tobytes()).hexdigest(),'visualStatus':'pending'}
 if changed is not None:o['changedPixels']=int(changed)
 report['crops'].append(o)
 return o
for tid in ['r05_c02','r06_c04','r07_c03']:
 entry=adopted[tid]; before=img(old[tid]['file']); after=img(entry['image']['path'])
 if sha(entry['image']['path'])!=entry['image']['sha256']:raise RuntimeError('hash mismatch')
 a=np.asarray(before); b=np.asarray(after); delta=np.any(a!=b,axis=2);ys,xs=np.nonzero(delta)
 bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
 tile={'zone':'northwest','tileId':tid,'coreCount':16,'oldCoreCount':16,'coreCountDelta':0,'fullCoverage':True,'adopted':True,'file':entry['image']['path'],'sha256':entry['image']['sha256'],'formalAccepted':False,'productionInternalClosurePassed':entry['internalClosurePassed'],'baselineFile':old[tid]['file'],'baselineSha256':sha(old[tid]['file']),'changedPixelCount':int(delta.sum()),'diffBbox':bbox,'priorEvidenceReusable':False,'internalSeams':[],'outerStrips':[],'repairChain':[]}
 freeze(entry['record']['path'])
 # Only walk finite current repair ancestry to record affected mask/crop boundaries.
 record=read(entry['record']['path'])
 seen=set()
 while 'repairSource' in record:
  recpath=record['base']['record']['path']
  box=record['cropBox']; patch=record['repairSource']['path']
  tile['repairChain'].append({'source':patch,'sourceSha256':record['repairSource']['sha256'],'cropBox':box,'mask':record['mask'],'baseFile':record['base']['image']['path']})
  if record['base']['image']['path'].replace('\\','/')==old[tid]['file'].replace('\\','/'):break
  if recpath in seen:break
  seen.add(recpath);record=read(recpath)
 # Native core edges: reuse exact pixels, save only changed segments.
 for orientation in ['h','v']:
  for line in [1024,2048,3072]:
   for seg in range(4):
    box=(seg*1024,line-256,(seg+1)*1024,line+256) if orientation=='h' else (line-256,seg*1024,line+256,(seg+1)*1024)
    n=int(delta[box[1]:box[3],box[0]:box[2]].sum()); name=f'internal-{orientation}{line}-seg{seg+1}'
    e={'name':name,'box':list(box),'changedPixels':n,'priorPixelsIdentical':n==0}
    if n:e['crop']=savecrop(tid,name,after,box,'internal-seam',n)['path']
    tile['internalSeams'].append(e)
 for side,box in {'north':(0,0,4096,256),'south':(0,3840,4096,4096),'west':(0,0,256,4096),'east':(3840,0,4096,4096)}.items():
  n=int(delta[box[1]:box[3],box[0]:box[2]].sum())
  tile['outerStrips'].append({'side':side,'box':list(box),'changedPixels':n,'priorPixelsIdentical':n==0,'currentPixelSha256':hashlib.sha256(after.crop(box).tobytes()).hexdigest(),'priorPixelSha256':hashlib.sha256(before.crop(box).tobytes()).hexdigest()})
 # Save current repair crop views only if those windows contain changed pixels.
 unique=[]
 for item in tile['repairChain']:
  box=item['cropBox']
  if box in unique:continue
  unique.append(box)
  if delta[box[1]:box[3],box[0]:box[2]].any():savecrop(tid,f'repair-context-{len(unique):02d}',after,box,'repair-context')
 report['tiles'].append(tile)
# Validate south-neighbor input and full shared-edge pixel reuse against frozen v03 pair.
neighbor=old['r08_c03']; ni=img(neighbor['file']); north=report['tiles'][2]
report['crossZone']={'pair':['r07_c03','r08_c03'],'neighborFile':neighbor['file'],'neighborSha256':sha(neighbor['file']),'neighborHashMatchesV03':sha(neighbor['file'])==neighbor['sha256'],'northLast256RowsUnchanged':next(x for x in north['outerStrips'] if x['side']=='south')['priorPixelsIdentical'],'priorEvidence':str(REVIEW/'resume-v03/west/summary.json'),'native100PercentReinspectionRequired':False}
report['crossZone']['priorPassReusable']=report['crossZone']['neighborHashMatchesV03'] and report['crossZone']['northLast256RowsUnchanged']
report['crossZone']['native100PercentReinspectionRequired']=not report['crossZone']['priorPassReusable']
write(OUT/'prepared.json',report)
print(json.dumps({'tiles':[{k:t[k] for k in ['tileId','changedPixelCount','diffBbox','outerStrips']}|{'changedInternalSegments':sum(e['changedPixels']>0 for e in t['internalSeams']),'repairCropCount':len(t['repairChain'])} for t in report['tiles']],'crossZone':report['crossZone'],'cropCount':len(report['crops'])},indent=2))
