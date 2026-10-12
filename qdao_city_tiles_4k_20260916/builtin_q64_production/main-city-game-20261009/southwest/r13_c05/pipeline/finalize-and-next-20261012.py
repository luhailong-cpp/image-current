from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest')
P=B/'r13_c05/pipeline'; A=P/'output/58c1da5acdb9a915/assembly.json'; a=json.loads(A.read_text()); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
final=json.loads((A.parent/'native-qa/manifest.json').read_text()); reviewed={}
for sig in ['e25add5da318eb09','0944961c5f4b56fd','a61993cba112315b']:
 m=P/'output'/sig/'native-qa/manifest.json'
 if m.exists():
  for r in json.loads(m.read_text())['records']: reviewed[r['name']]=r
same=[];changed=[]
for r in final['records']:
 if r['name'] in reviewed and r['sha256']==reviewed[r['name']]['sha256']: same.append(r['name'])
 elif r['name'] in reviewed: changed.append(r['name'])
ext=P/'qa/external-top-native';ext.mkdir(exist_ok=True)
up=B/'r12_c05/repairs-resume-20261012/integrated-local-v14/r12_c05.candidate.png';u=Image.open(up).convert('RGB');im=Image.open(a['output']['file']).convert('RGB');records=[]
for c in range(4):
 q=Image.new('RGB',(1024,238));q.paste(u.crop((c*1024,3977,(c+1)*1024,4096)),(0,0));q.paste(im.crop((c*1024,0,(c+1)*1024,119)),(0,119));f=ext/f'TOP-{c+1}.png';q.save(f);records.append({'file':str(f),'sha256':sha(f),'pixels':list(q.size),'upperCoreBox':[c*1024,3977,(c+1)*1024,4096],'lowerCoreBox':[c*1024,0,(c+1)*1024,119]})
write(ext/'manifest.json',{'upperSource':{'file':str(up),'sha256':sha(up)},'lowerSource':a['output'],'records':records,'nativeCropOnly':True,'resampled':False,'visualQa':'pending','formalAccepted':False})
base=P/'receipts/p01_01.resumed-full64-v01.receipt.json';b=json.loads(base.read_text());write(P/'receipts/p01_01.resumed-full64-v01.disposition.json',{'createdAtUtc':now,'native':b['native'],'explicitlyRejected':True,'reason':'Wrong full-width horizontal paving topology: guide left/central groove rows must be staggered from right strip. Base original preserved; not current selected native. Superseded by stagger-layout-v02. No local art extracted from rejected base into final.'})
T=B/'r14_c05';p=T/'pipeline';p.mkdir(exist_ok=True);anc=p/'anchors/r13_c05-bottom230.native.png';anc.parent.mkdir(exist_ok=True);ctx=Image.open(a['contextOutput']['file']).convert('RGB');ctx.crop((0,4096,4326,4326)).save(anc)
write(str(anc)+'.derivation.json',{'file':str(anc),'sha256':sha(anc),'source':a['contextOutput'],'sourceAssembly':{'file':str(A),'sha256':sha(A)},'sourceContextBox':[0,4096,4326,4326],'operation':'exact native crop only','sourceResampling':False,'gameArtNative':True,'sourceStatus':'provisional coverage; open geometry/material issues remain; formal/internal false','formalAccepted':False})
(p/'qa').mkdir(exist_ok=True);sheet=Image.new('RGB',(1024,1088),(35,35,35));d=ImageDraw.Draw(sheet)
for r in range(1,5):
 for c in range(1,5):
  g=Image.open(T/'guides'/f'p{r:02d}_{c:02d}.layout-only.png').convert('RGB');sheet.paste(g.resize((256,256),Image.Resampling.NEAREST),((c-1)*256,(r-1)*272));d.text(((c-1)*256+8,(r-1)*272+257),f'p{r:02d}_{c:02d} GUIDE only',fill='white')
sheet.save(p/'qa/layout-contact-resized.png')
write(p/'lane-state-20261012.json',{'tile':'r14_c05','owner':'/root/sol_r12_repair_20261012','status':'native_production_active','startedAtUtc':now,'selectedNativeSlots':0,'plannedNativeSlots':16,'activePatch':'p01_01','topAnchor':{'file':str(anc),'sha256':sha(anc)},'mandatoryReferenceCount':3,'actualModel':None,'actualQuality':None,'internalAccepted':False,'formalAccepted':False})
print(json.dumps({'unchangedPreviouslyReviewed':same,'changedFromPreviouslyReviewed':changed,'externalTopCrops':records,'nextAnchor':str(anc),'nextLayoutContact':str(p/'qa/layout-contact-resized.png'),'core':a['output'],'context':a['contextOutput']},indent=2))
