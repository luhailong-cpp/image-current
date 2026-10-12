import sys
sys.dont_write_bytecode=True
import json,shutil,importlib.util
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
tracep=Path(sys.argv[1]).resolve();auditp=Path(sys.argv[2]).resolve();tr=read(tracep);audit=read(auditp)
assert audit['status'] in ['passed','art_passed']
ip=z/'art-delivery-index.json';idx=read(ip);entries={e['tile']:e for e in idx['artAccepted']};exported=[]
for item in tr['tiles']:
 tile=item['tile'];src=Path(item['candidate']['path']);assert prod.sha(src)==item['candidate']['sha256'];assert Image.open(src).size==(4096,4096)
 target=z/'tiles'/(tile+'.png');old=None
 if target.exists() and prod.sha(target)!=prod.sha(src):
  history=z/'tiles'/'history';history.mkdir(exist_ok=True);old=history/(tile+'-'+prod.sha(target)[:12]+'.png')
  if not old.exists():shutil.copy2(target,old)
  meta=Path(str(target)+'.provenance.json')
  if meta.exists() and not Path(str(old)+'.provenance.json').exists():shutil.copy2(meta,Path(str(old)+'.provenance.json'))
 if not target.exists() or prod.sha(target)!=prod.sha(src):
  pending=target.with_name(target.stem+'.new-reviewed-pair.png');shutil.copy2(src,pending);pending.replace(target)
 rr,cc=int(tile[1:3]),int(tile[5:7]);e={'tile':tile,'status':'art_accepted','dimensions':[4096,4096],'file':ref(target),'globalCoreBox':[(cc-1)*4096,(rr-1)*4096,cc*4096,rr*4096],'source':ref(src),'sourceTrace':ref(tracep),'artAudit':ref(auditp),'nativeContext':item['context'],'noResize':True,'noBlend':True,'sourcePixelIdentity':True,'priorVersion':ref(old) if old else None,'runtimeGateActive':False}
 prod.write(Path(str(target)+'.provenance.json'),e);entries[tile]=e;exported.append(tile)
idx.update({'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'artAcceptedTiles':len(entries),'artAccepted':list(entries.values()),'status':'production_in_progress'});prod.write(ip,idx)
print(json.dumps({'artAcceptedTiles':len(entries),'exported':exported,'index':ref(ip)}))
