"""Export reviewed native art without replacing any existing image."""
import sys
sys.dont_write_bytecode=True
import json,shutil,importlib.util,re
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
def verify(r):
 p=Path(r['path']);assert p.is_file() and prod.sha(p)==r['sha256'];return p
tracep=Path(sys.argv[1]).resolve();auditp=Path(sys.argv[2]).resolve();tr=read(tracep);audit=read(auditp)
assert audit['status'] in ['passed','art_passed']
filtertiles=set(sys.argv[3:])
ip=z/'art-delivery-index.json';idx=read(ip);entries={e['tile']:e for e in idx['artAccepted']};exported=[]
hist=z/'tiles/history';hist.mkdir(exist_ok=True)
priorindex=hist/('art-delivery-index-'+prod.sha(ip)[:16]+'.json')
if not priorindex.exists():shutil.copy2(ip,priorindex)
for item in tr['tiles']:
 tile=item['tile']
 if filtertiles and tile not in filtertiles:continue
 src=verify(item['candidate']);ctx=verify(item['context'])
 with Image.open(src) as im:assert im.size==(4096,4096)
 with Image.open(ctx) as im:assert im.size==(4326,4326)
 prior=entries.get(tile)
 if prior and prior['file']['sha256']==prod.sha(src):
  target=verify(prior['file'])
 else:
  versions=[1 if (z/'tiles'/f'{tile}.png').exists() else 0]
  for p in (z/'tiles').glob(tile+'_v*.png'):
   match=re.fullmatch(re.escape(tile)+r'_v(\d+)\.png',p.name)
   if match:versions.append(int(match[1]))
  target=z/'tiles'/f'{tile}_v{max(versions)+1}.png';assert not target.exists()
  shutil.copy2(src,target);assert prod.sha(target)==prod.sha(src)
 rr,cc=int(tile[1:3]),int(tile[5:7]);e={'tile':tile,'status':'art_accepted','dimensions':[4096,4096],'file':ref(target),'globalCoreBox':[(cc-1)*4096,(rr-1)*4096,cc*4096,rr*4096],'source':ref(src),'sourceTrace':ref(tracep),'artAudit':ref(auditp),'nativeContext':item['context'],'noResize':True,'noBlend':True,'sourcePixelIdentity':True,'priorVersion':prior['file'] if prior else None,'runtimeGateActive':False}
 meta=Path(str(target)+'.provenance.json')
 if meta.exists():
  meta=z/'tiles'/(target.stem+'-adoption-'+prod.sha(auditp)[:12]+'.json');assert not meta.exists()
 prod.write(meta,e);e['provenanceRecord']=ref(meta);entries[tile]=e;exported.append({'tile':tile,'file':ref(target)})
idx.update({'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'artAcceptedTiles':len(entries),'artAccepted':list(entries.values()),'status':'production_in_progress','imageWritePolicy':'Versioned new exports; all prior images retained unchanged','previousIndexSnapshot':ref(priorindex)});prod.write(ip,idx)
print(json.dumps({'artAcceptedTiles':len(entries),'exported':exported,'index':ref(ip)}))
