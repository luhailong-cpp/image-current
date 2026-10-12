import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
Z=Path(__file__).resolve().parents[1];prefix=sys.argv[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
m=rd(Z/'qa'/(prefix+'.manifest.json'));trace=Z/'qa'/(prefix+'-trace.json');t=rd(trace);context=Image.open(t['context']['path']).convert('RGB');core=Image.open(t['candidate']['path']).convert('RGB');out=[]
for r in m['repairs']:
 b=[v+115 for v in r['tileContextBox']];p=Z/'qa'/(prefix+'-'+r['id']+'-finalcrop-100pct.png');assert not p.exists();context.crop(b).save(p);out.append({'id':r['id'],'path':p.as_posix(),'sha256':sha(p),'contextBox':b})
asm=rd(Z/'qa/full-tile-r08_c06-assembly.json');q=[]
for old in asm['qa']:
 b=old['sourceBox'];after=core.crop(b);before=Image.open(old['file']).convert('RGB');equal=np.array_equal(np.asarray(after),np.asarray(before));record={'original':old,'unchangedPixels':equal}
 if not equal:
  p=Z/'qa'/(prefix+'-'+Path(old['file']).name.replace('full-tile-r08_c06-',''));assert not p.exists();after.save(p);record['updated']={'path':p.as_posix(),'sha256':sha(p)}
 q.append(record)
p=Z/'qa'/(prefix+'-qa-index.json');assert not p.exists();p.write_text(json.dumps({'trace':{'path':trace.as_posix(),'sha256':sha(trace)},'finalcrops':out,'original39':q},indent=2)+'\n',encoding='utf-8');print(json.dumps({'finalcrops':len(out),'inherited39':sum(x['unchangedPixels'] for x in q),'updated39':sum(not x['unchangedPixels'] for x in q)}))

