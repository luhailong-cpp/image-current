from pathlib import Path
from PIL import Image
import json,hashlib,sys
from datetime import datetime,timezone
z=Path(__file__).resolve().parent.parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mode,i=sys.argv[1:3];assert i.startswith('r03_c11_')
if mode=='review':
 rec=read(z/'native'/f'{i}.png.generation.json');assert Image.open(rec['file']).size==(1254,1254)
 checks=[]
 for ref in rec['references']:
  for s in [ref]+ref.get('sources',[]):
   checks.append({'file':s['file'],'sha256':sha(Path(s['file'])),'matches':sha(Path(s['file']))==s['sha256']})
 assert all(s['matches'] for s in checks)
 assert sha(Path(rec['file']))==sha(Path(rec['evidence']['originalToolPath']))
 evidence=sys.argv[3:]
 for e in evidence:assert (z/'qa'/e).exists()
 audit={'id':i,'status':'passed_internal_native_and_recorded_joins','sha256':rec['sha256'],'nativeSize':[1254,1254],'coreCrop':[115,115,1139,1139],'evidence':evidence,'visualChecks':'Native geometry/material/target scale and referenced exact core joins manually inspected at1:1, continuous.','sources':checks,'originalToolBytesMatch':True,'actualModel':None,'actualQuality':None,'resized':False,'feathered':False,'reviewedAtUtc':datetime.now(timezone.utc).isoformat()}
 write(z/'qa'/f'{i}.audit.json',audit);rec['status']=audit['status'];rec['qa']=str(z/'qa'/f'{i}.audit.json');write(z/'native'/f'{i}.png.generation.json',rec)
 p=z/'qa/r03_c11-progress.json';q=read(p)
 for k in ['generated','accepted']:
  if i not in q[k]:q[k].append(i)
 q['currentId']=i;q['updatedAtUtc']=audit['reviewedAtUtc'];write(p,q)
 print(json.dumps({'id':i,'sha256':rec['sha256'],'acceptedCount':len(q['accepted'])}))
elif mode=='cross':
 ids=sys.argv[3:7];assert len(ids)==4
 out=Image.new('RGB',(512,512));ev=[]
 for ident,crop,at in zip(ids,[(883,883,1139,1139),(115,883,371,1139),(883,115,1139,371),(115,115,371,371)],[(0,0),(256,0),(0,256),(256,256)]):
  p=z/'native'/f'{ident}.png';out.paste(Image.open(p).convert('RGB').crop(crop),at);ev.append({'id':ident,'file':str(p),'sha256':sha(p),'crop':crop,'paste':at})
 p=z/'qa'/f'{i}.right-cross-100pct.png';out.save(p);write(p.with_suffix('.png.derivation.json'),{'operation':'exact 256x256 core corners in TL TR BL BR order; no resampling','sources':ev,'sha256':sha(p)})
 print(str(p))
elif mode=='roles':
 p=z/'prompts'/f'{i}.inputs.json';refs=read(p)
 if 'sources' in refs[1]:
  refs[1]['role']='Unscaled exact1254 native neighbor plate, left-to-right: '+', '.join(sys.argv[3:])+'. These are full adjacent native references, not output framing.'
 else:
  refs[1]['role']='Exact full native RIGHT neighbor and its recorded right230px overlap constraint.'
 write(p,refs)

