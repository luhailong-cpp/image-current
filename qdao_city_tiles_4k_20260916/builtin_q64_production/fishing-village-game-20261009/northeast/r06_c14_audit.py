from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
from datetime import datetime,timezone
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast');qd=z/'qa/r06_c14-v1';sel=json.loads((z/'records/r06_c14.selection-proposed-v1.json').read_text(encoding='utf-8'));can=Image.open(z/'tiles/r06_c14.candidate-v1.png').convert('RGB')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p).replace(chr(92),'/'),'sha256':sha(p)}
checks=[]
for p,e in sel['patches'].items():
 f=Path(e['path']);rec=json.loads(Path(str(f)+'.generation.json').read_text(encoding='utf-8'));r,c=int(p[-2]),int(p[-1]);im=Image.open(f).convert('RGB')
 assert im.size==(1254,1254) and sha(f)==e['sha256']==rec['sha256']
 assert rec['actualModel'] is None and rec['actualQuality'] is None and rec['route']=='builtin'
 assert rec['coordinates']['nativeGlobalBox']==[53248+(c-1)*1024-115,20480+(r-1)*1024-115,53248+c*1024+115,20480+r*1024+115]
 assert len(rec['references'])==4
 for key in ['source','prompt','receipt','configSource']:
  assert sha(rec[key]['path'])==rec[key]['sha256']
 for x in rec['references']:assert sha(x['path'])==x['sha256']
 assert sha(rec['source']['path'])==sha(f)
 assert ImageChops.difference(can.crop(((c-1)*1024,(r-1)*1024,c*1024,r*1024)),im.crop((115,115,1139,1139))).getbbox() is None
 checks.append({'patchId':p,'native':ref(f),'source':rec['source'],'coordinates':rec['coordinates'],'receipt':rec['receipt'],'allReferencesAndEvidenceHashesVerified':True,'native1254':True,'corePixelEquality':True,'actualModel':None,'actualQuality':None})
ext=Image.new('RGB',(256,4096));west=[]
for r in range(1,5):
 f=z/'native'/f'r06_c13_p{r}4-v1.png';im=Image.open(f).convert('RGB');ext.paste(im.crop((1011,115,1139,1139)),(0,(r-1)*1024));ext.paste(can.crop((0,(r-1)*1024,128,r*1024)),(128,(r-1)*1024));west.append(ref(f))
fp=qd/'r06_c14-west-boundary-4096.native-1to1.png';assert not fp.exists();ext.save(fp)
exports=[ref(fp)]
for r in range(1,5):
 p=qd/f'r06_c14-west-segment{r}.native-1to1.png';ext.crop((0,(r-1)*1024,256,r*1024)).save(p);exports.append(ref(p))
for r in range(1,4):
 p=qd/f'r06_c14-west-junction{r}.native-1to1.png';ext.crop((0,r*1024-256,256,r*1024+256)).save(p);exports.append(ref(p))
m=json.loads((qd/'manifest.json').read_text(encoding='utf-8'));qachecks=[]
for e in m['qa']:
 p=Path(e['file']);assert sha(p)==e['sha256'];qachecks.append({'file':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size)})
audit={'tile':'r06_c14','checkedAtUtc':datetime.now(timezone.utc).isoformat(),'selectedSources':checks,'sourceCount':len(checks),'actualNativeFiles':len(list((z/'native').glob('r06_c14_*.png'))),'candidate':ref(z/'tiles/r06_c14.candidate-v1.png'),'qaExports':qachecks,'westSourceNative':west,'westExports':exports,'resamplingPerformed':False,'formalAccepted':False}
(qd/'r06_c14-provenance-validation.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
p=z/'records/r06_c14.local-continuation-20261011.json';d=json.loads(p.read_text(encoding='utf-8'));d.update({'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'actualNewNativeCount':audit['actualNativeFiles'],'selectedCoordinateCount':16,'missingCoordinates':[],'actualNewNativeFiles':[ref(p) for p in sorted((z/'native').glob('r06_c14_*.png'))],'candidate':audit['candidate'],'selection':ref(z/'records/r06_c14.selection-proposed-v1.json'),'provenanceValidation':ref(qd/'r06_c14-provenance-validation.json'),'status':'16_native_cores_assembled_self_review_in_progress'});p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected':len(checks),'nativeCount':audit['actualNativeFiles'],'qaCount':len(qachecks),'westExports':len(exports),'allVerified':True}))

