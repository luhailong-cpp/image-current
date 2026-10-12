"""Mechanical existing-only capacity gate audit; no generation or repainting."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import numpy as np
Z=Path(__file__).resolve().parent;T=Z/'r11_c10';Q=T/'qa'/'existing-2x2'
Q.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
tiles=['r10_c09','r10_c10','r11_c09','r11_c10'];states={};sources={}
for t in tiles:
 sel=Z/t/'selected-patches.json';s=read(sel);states[t]={'path':str(sel),'sha256':sha(sel),'selection':s}
 for pid,rel in s['patches'].items():
  f=Z/t/rel;im=Image.open(f).convert('RGB');assert im.size==(1254,1254)
  row,col=int(t[1:3]),int(t[5:7]);r,c=int(pid[1]),int(pid[2]);x=(col-1)*4096+(c-1)*1024;y=(row-1)*4096+(r-1)*1024
  sources[(t,pid)]={'file':str(f),'sha256':sha(f),'tile':t,'patch':pid,'nativeGlobalBox':[x-115,y-115,x+1139,y+1139],'coreGlobalBox':[x,y,x+1024,y+1024],'core':im.crop((115,115,1139,1139))}
def public(s):return {k:v for k,v in s.items() if k!='core'}
seams=[]
for ta,tb,axis in [('r10_c09','r10_c10','vertical'),('r11_c09','r11_c10','vertical'),('r10_c09','r11_c09','horizontal'),('r10_c10','r11_c10','horizontal')]:
 for n in range(1,5):
  pa,pb=(f'p{n}4',f'p{n}1') if axis=='vertical' else (f'p4{n}',f'p1{n}')
  if (ta,pa) not in sources or (tb,pb) not in sources:continue
  a,b=sources[(ta,pa)],sources[(tb,pb)];aa,bb=a['core'],b['core'];box=b['coreGlobalBox']
  if axis=='vertical':
   out=Image.new('RGB',(512,1024));out.paste(aa.crop((768,0,1024,1024)),(0,0));out.paste(bb.crop((0,0,256,1024)),(256,0));wb=[box[0]-256,box[1],box[0]+256,box[3]]
  else:
   out=Image.new('RGB',(1024,512));out.paste(aa.crop((0,768,1024,1024)),(0,0));out.paste(bb.crop((0,0,1024,256)),(0,256));wb=[box[0],box[1]-256,box[2],box[1]+256]
  name=f'{ta}-{pa}--{tb}-{pb}';f=Q/(name+'.png');out.save(f)
  rec={'id':name,'file':str(f),'sha256':sha(f),'axis':axis,'globalBox':wb,'seamCoordinate':256,'dimensions':list(out.size),'sources':[public(a),public(b)],'resamplingApplied':False,'visualStatus':'pending'}
  write(f.with_suffix('.png.derivation.json'),rec);seams.append(rec)
out=Image.new('RGB',(512,512));keys=[('r10_c09','p44'),('r10_c10','p41'),('r11_c09','p14'),('r11_c10','p11')]
for i,key in enumerate(keys):
 c=sources[key]['core'];crop=[(768,768,1024,1024),(0,768,256,1024),(768,0,1024,256),(0,0,256,256)][i];out.paste(c.crop(crop),((i%2)*256,(i//2)*256))
cf=Q/'cross-tile-r10-r11-c09-c10.png';out.save(cf);cross={'file':str(cf),'sha256':sha(cf),'globalBox':[36608,40704,37120,41216],'sources':[public(sources[k]) for k in keys],'resamplingApplied':False,'visualStatus':'pending'}
write(cf.with_suffix('.png.derivation.json'),cross)
partial=Image.new('RGBA',(4096,4096),(0,0,0,0));owned=[]
for key,s in sources.items():
 if key[0]!='r11_c10':continue
 b=s['coreGlobalBox'];partial.paste(s['core'],(b[0]-36864,b[1]-40960));owned.append(public(s))
pf=Q/'r11_c10-partial-native-core-4096.png';partial.save(pf)
write(pf.with_suffix('.png.derivation.json'),{'file':str(pf),'sha256':sha(pf),'dimensions':[4096,4096],'operation':'Unscaled exact native cores; absent positions transparent','sources':owned,'complete':False,'notGameReady':True,'resamplingApplied':False})
refchecks=[];nativechecks=[]
for f in sorted((T/'native').glob('*.png')):
 rec=read(f.with_suffix('.png.generation.json'));assert sha(f)==rec['sha256'];assert Image.open(f).size==(1254,1254)
 nativechecks.append({'file':str(f),'sha256':sha(f),'nativeDimensions':[1254,1254]})
 for ref in rec['references']:
  p=Path(ref['path']);actual=sha(p) if p.exists() else None;ok=actual==ref['sha256']
  if not ok:
   p=T/'input-snapshots'/(ref['sha256']+'.png');ok=p.exists() and sha(p)==ref['sha256']
  refchecks.append({'native':str(f),'reference':ref,'verifiedPath':str(p),'match':ok})
audit={'tile':'r11_c10','auditedAt':now(),'nativeCount':len(nativechecks),'nativeChecks':nativechecks,'referenceCount':len(refchecks),'referenceChecks':refchecks,'allMatch':all(r['match'] for r in refchecks)}
write(T/'qa'/'gate-provenance-audit.json',audit)
for t,st in states.items():assert sha(st['path'])==st['sha256'],'Neighbor selection changed; rerun'
write(Q/'manifest.json',{'createdAt':now(),'purpose':'existing-only shared-edge inspection during capacity gate','selectionSnapshots':states,'seams':seams,'crossing':cross,'partialNativeComposite':str(pf),'formalAccepted':False})
ack={'agent':'next_tile_setup','createdAt':now(),'gate':str(Z.parents[1]/'capacity-layout-gate-20261010.json'),'inFlightImageGeneration':False,'newGenerationHeld':True,'noArtworkDeleted':True,'successfulNewTileCoordinates':owned,'r10c10SelectedCount':len(states['r10_c10']['selection']['patches']),'newTileNativeCount':len(owned),'newTileComplete4kCount':0,'r12c10r13c10r14c10':'not started; no coordinate-plan or art created','failedAttempt':{'patch':'p23','receipt':str(T/'p23-v1.receipt.json'),'output':None,'retrySubmitted':False},'qaManifest':str(Q/'manifest.json'),'provenanceAudit':str(T/'qa'/'gate-provenance-audit.json'),'capacityRiskObservations':['Existing six r11_c10 cores depict open wooden dock floor; rail at west consumes part of p11/p21/p22. Artwork alone is not a collision or capacity validation.','One authoritative overview pixel corresponds to roughly45.73 world pixels under current57344 extent mapping; exact functional widths cannot be inferred from the enlarged layout guide.','Northern workshop roof in r10_c10 and western rail/support footprints must be excluded from any conservative walking mask.','Southern ungenerated r11_c10 layout contains dock edge, mooring post, water and adjacent stone pavement; do not treat the whole tile as walkable.','Coordinate/world scale remains provisional under root capacity gate; no5000-player capacity claim.']}
write(T/'capacity-gate-ack.json',ack)
print(json.dumps({'nativeCount':len(nativechecks),'referenceCount':len(refchecks),'allMatch':audit['allMatch'],'existingSharedSeams':len(seams),'crossings':1,'ack':str(T/'capacity-gate-ack.json')}))

