import sys
sys.dont_write_bytecode=True
import json,hashlib,shutil,importlib.util
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
z=Path(__file__).resolve().parent.parent
q=z/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
tp=q/'pair-r09c06-c07-final-v5-trace.json'
assert sha(tp)=='6d813ed4c72bdcd4c560df8d1d4f0796c8ed80c8168a7ab4a63f68eea4a1fe83'
tr=json.loads(tp.read_text(encoding='utf-8'))
ap=q/'pair-r09c06-c07-final-v5-root-art-audit.json'
write(ap,{'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','status':'art_passed','trace':ref(tp),'nativeSharedSegmentsViewed':5,'additionalNativeCropsViewed':['upper-finalcrop','lower-finalcrop','north-halo-finalcrop','south-halo-finalcrop'],'observations':['Wood rail, rear post, red fish and lower frame contours are continuous.','Small rear wood shadow triangle at upper joint is non-blocking; existing painterly stone texture retained.'],'scope':'Art, internal and c06/c07 shared-edge acceptance. Other outer neighbors remain pending; no runtime gate.'})
ip=z/'art-delivery-index.json'
idx=json.loads(ip.read_text(encoding='utf-8-sig'))
entries={e['tile']:e for e in idx['artAccepted']}
for item in tr['tiles']:
 p=Path(item['candidate']['path'])
 assert sha(p)==item['candidate']['sha256']
 assert Image.open(p).size==(4096,4096)
 target=z/'tiles'/(item['tile']+'.png')
 assert not target.exists() or sha(target)==sha(p)
 shutil.copy2(p,target)
 rr,cc=int(item['tile'][1:3]),int(item['tile'][5:7])
 e={'tile':item['tile'],'status':'art_accepted','dimensions':[4096,4096],'file':ref(target),'globalCoreBox':[(cc-1)*4096,(rr-1)*4096,cc*4096,rr*4096],'source':ref(p),'sourceTrace':ref(tp),'artAudit':ref(ap),'nativeContext':item['context'],'noResize':True,'noBlend':True,'sourcePixelIdentity':True,'runtimeGateActive':False}
 write(Path(str(target)+'.provenance.json'),e)
 entries[item['tile']]=e
idx.update({'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'artAcceptedTiles':len(entries),'artAccepted':list(entries.values()),'status':'production_in_progress'})
write(ip,idx)
spec=importlib.util.spec_from_file_location('prod',z/'production.py')
prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
p=json.loads((z/'progress.json').read_text(encoding='utf-8-sig'))
p.update({'complete4kCount':len(entries),'artAccepted4kCount':len(entries),'artDeliveryIndex':str(ip),'runtimeGateActive':False,'status':'continuing_adjacent_native_art','updatedAtUtc':datetime.now(timezone.utc).isoformat()})
prod.write(z/'progress.json',p)
print(json.dumps({'exported':['r09_c06','r09_c07'],'artAcceptedTiles':len(entries),'index':ref(ip),'audit':ref(ap)}))
