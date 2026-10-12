import sys
sys.dont_write_bytecode=True
import json,hashlib,shutil,importlib.util
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
z=Path(__file__).resolve().parent.parent;q=z/'qa';t=z/'tiles'
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
write=prod.write
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
prefix='block2x2-r09r10c05c06-v1'
tracep=q/(prefix+'-trace.json');tr=json.loads(tracep.read_text(encoding='utf-8'))
assert tr['sourcePixelIdentity'] and not tr['nativePixelsResampled']
audit=q/(prefix+'-root-art-audit.json')
write(audit,{'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','status':'art_passed','trace':ref(tracep),'nativeSharedSegmentsViewed':20,'centralJunctionViewed':True,'nativeQa':tr['qa'],'observations':['Road slabs, wood frame, lantern and parasol contours remain continuous across all four shared edges.','Minor bevel variation on the east shared edge remains consistent with the existing painterly stone material.'],'scope':'Art and source-pixel integrity; other outer edges pending. No runtime acceptance gate.'})
idxp=z/'art-delivery-index.json';idx=json.loads(idxp.read_text(encoding='utf-8-sig'));entries={e['tile']:e for e in idx['artAccepted']}
with Image.open(tr['context']['path']) as im:
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
  if not target.exists() or sha(target)!=item['sha256']:
   pending=target.with_name(target.stem+'.new-block-c05c06.png');shutil.copy2(p,pending);pending.replace(target)
  assert sha(target)==item['sha256']
  x,y,r,b=item['contextBox'];ctx=q/(prefix+'-'+item['tile']+'-context-native.png')
  if not ctx.exists():im.crop((x-115,y-115,r+115,b+115)).save(ctx)
  rr,cc=int(item['tile'][1:3]),int(item['tile'][5:7])
  e={'tile':item['tile'],'status':'art_accepted','dimensions':[4096,4096],'file':ref(target),'globalCoreBox':[(cc-1)*4096,(rr-1)*4096,cc*4096,rr*4096],'source':ref(p),'sourceTrace':ref(tracep),'artAudit':ref(audit),'nativeContext':ref(ctx),'noResize':True,'noBlend':True,'sourcePixelIdentity':True,'priorVersion':ref(old) if old else None,'runtimeGateActive':False}
  write(Path(str(target)+'.provenance.json'),e);entries[item['tile']]=e
idx.update({'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'artAcceptedTiles':len(entries),'artAccepted':list(entries.values()),'status':'production_in_progress'});write(idxp,idx)
p=json.loads((z/'progress.json').read_text(encoding='utf-8-sig'));p.update({'complete4kCount':len(entries),'artAccepted4kCount':len(entries),'artDeliveryIndex':str(idxp),'runtimeGateActive':False,'updatedAtUtc':datetime.now(timezone.utc).isoformat()});write(z/'progress.json',p)
print(json.dumps({'artAcceptedTiles':len(entries),'index':ref(idxp),'audit':ref(audit),'currentContexts':{e['tile']:e['nativeContext'] for e in entries.values() if e['tile'] in [x['tile'] for x in tr['tiles']]}}))
