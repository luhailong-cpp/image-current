import sys
sys.dont_write_bytecode=True
import json,hashlib,shutil,importlib.util
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
z=Path(__file__).resolve().parent.parent;q=z/'qa';t=z/'tiles'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
tracep=q/'block2x2-r09r10c04c05-v1-trace.json'
assert sha(tracep)=='3a26aa0f7321414cd519e737e43107bf020e779604049da65db83e52ce3d9aff'
tr=json.loads(tracep.read_text(encoding='utf-8'))
audit=q/'block2x2-r09r10c04c05-v1-root-art-audit.json'
write(audit,{'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','status':'art_passed','trace':ref(tracep),'nativeSharedSegmentsViewed':20,'centralJunctionViewed':True,'compositionPreviewViewed':True,'staircaseCount':6,'layout':'continuous six-step staircase, posts, roads, sand shoulder, wall, foliage and parasol retain intended placements','observations':['Minor stone bevel and texture variation remains in west-shared3 and south-shared3; no open cracks or object disconnections found.'],'nativeQa':tr['qa'],'scope':'art and source-pixel integrity only; no runtime acceptance gate'})
export=[]
im=Image.open(tr['context']['path'])
assert im.size==(8422,8422)
for item in tr['tiles']:
 p=Path(item['path']);assert sha(p)==item['sha256']
 target=t/(item['tile']+'.png');old=None
 if target.exists() and sha(target)!=item['sha256']:
  history=t/'history';history.mkdir(exist_ok=True)
  old=history/(item['tile']+'-'+sha(target)[:12]+'.png')
  if not old.exists():shutil.copy2(target,old)
  meta=Path(str(target)+'.provenance.json')
  if meta.exists() and not Path(str(old)+'.provenance.json').exists():shutil.copy2(meta,Path(str(old)+'.provenance.json'))
 shutil.copy2(p,target);assert sha(target)==item['sha256']
 x,y,r,b=item['contextBox'];ctx=q/('block2x2-r09r10c04c05-v1-'+item['tile']+'-context-native.png')
 if not ctx.exists():im.crop((x-115,y-115,r+115,b+115)).save(ctx)
 rr,cc=map(int,[item['tile'][1:3],item['tile'][5:7]])
 provenance={'tile':item['tile'],'status':'art_accepted','dimensions':[4096,4096],'file':ref(target),'globalCoreBox':[(cc-1)*4096,(rr-1)*4096,cc*4096,rr*4096],'source':ref(p),'sourceTrace':ref(tracep),'artAudit':ref(audit),'nativeContext':ref(ctx),'noResize':True,'noBlend':True,'sourcePixelIdentity':True,'priorVersion':ref(old) if old else None,'runtimeGateActive':False}
 write(Path(str(target)+'.provenance.json'),provenance);export.append(provenance)
out=z/'art-delivery-index.json'
write(out,{'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'production_in_progress','assignedTiles':49,'artAcceptedTiles':4,'artAccepted':export,'preview':ref(q/'block2x2-r09r10c04c05-v1-composition-preview-only.png'),'finalPixelPolicy':'native hard-source choice; no enlargement','next':'continue remaining southwest tiles and joining edges'})
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
progress=json.loads((z/'progress.json').read_text(encoding='utf-8-sig'));progress.update({'complete4kCount':4,'artAccepted4kCount':4,'artDeliveryIndex':str(out),'runtimeGateActive':False,'status':'continuing_adjacent_native_art','updatedAtUtc':datetime.now(timezone.utc).isoformat()});prod.write(z/'progress.json',progress)
print(json.dumps({'exportCount':len(export),'index':ref(out),'audit':ref(audit),'tiles':[x['file'] for x in export]}))
