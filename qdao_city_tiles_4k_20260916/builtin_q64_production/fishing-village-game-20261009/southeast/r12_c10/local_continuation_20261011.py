from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from PIL import Image
T=Path(__file__).resolve().parent; Z=T.parent
sys.path.insert(0,str(Z))
import review_external_seams as ex
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
S=T/'selected-continuation-20261011.json'; sel=read(S); plan=read(T/'coordinate-plan.json'); records=[]
canvas=Image.new('RGBA',(4096,4096),(0,0,0,0));mask=Image.new('L',(4096,4096),0)
for pid,rel in sel['patches'].items():
 p=T/rel;im=Image.open(p).convert('RGB');assert im.size==(1254,1254)
 at=((int(pid[2])-1)*1024,(int(pid[1])-1)*1024);canvas.paste(im.crop((115,115,1139,1139)),at);mask.paste(255,(at[0],at[1],at[0]+1024,at[1]+1024))
 records.append(dict(patch=pid,file=str(p),sha256=sha(p),coreCrop=[115,115,1139,1139],destination=at))
O=T/'candidate';O.mkdir(exist_ok=True)
p=O/'r12_c10-partial-14cores-4096.png';canvas.save(p); m=O/'r12_c10-partial-coverage-mask-4096.png';mask.save(m)
write(p.with_suffix('.png.derivation.json'),dict(operation='unscaled exact native cores; transparent missing pixels',sources=records,dimensions=[4096,4096],sha256=sha(p),coverageMask=str(m),coverageMaskSha256=sha(m),coveredPixels=14*1024*1024,coverageFraction=14/16,complete=False,internalReady=False,formalAccepted=False,layoutPixelsUsed=False,resamplingApplied=False,missing=['p43','p44']))
src=ex.Sources(); cached=src.tile('r12_c10');cached.update(selection=sel,selectedPath=S,selectedSha256=sha(S))
Q=T/'qa'/'external-continuation-20261011';Q.mkdir(parents=True,exist_ok=True)
evidence=[]
for edge in ['north','west']:
 for i in range(4):
  box=[36864+i*1024,45056-256,36864+(i+1)*1024,45056+256] if edge=='north' else [36864-256,45056+i*1024,36864+256,45056+(i+1)*1024]
  evidence.append(ex.write_evidence(src,Q,f'{edge}-segment-{i+1}',box,dict(edge=edge)))
points=set([(36864+i*1024,45056) for i in range(5)]+[(36864,45056+i*1024) for i in range(5)])
for x,y in sorted(points):evidence.append(ex.write_evidence(src,Q,f'intersection-x{x}-y{y}',[x-384,y-384,x+384,y+384],dict(intersectionGlobal=[x,y])))
write(Q/'manifest.json',dict(selection=str(S),selectionSha256=sha(S),evidence=evidence,formalAccepted=False))
# Audit this continuation's actual successful returned artifacts against receipts.
new=[];raw_dir=Path('C:/Users/luyua/.codex/generated_images/01a12a35-7066-7da1-a5c9-9fb15070a385')
for pid in ['p23','p24','p31','p32','p33','p34','p41','p42']:
 p=T/'native'/f'{pid}-v1.png'; r=read(T/f'{pid}-v1.receipt.json');g=read(p.with_suffix('.png.generation.json'))
 assert p.exists() and sha(p)==sha(r['sourcePath'])==g['sha256']
 assert Image.open(p).size==(1254,1254)
 new.append(dict(patch=pid,native=str(p),sha256=sha(p),original=r['sourcePath'],provenance=str(p.with_suffix('.png.generation.json'))))
known={str(Path(r['original']).resolve()).lower() for r in new}; orphans=[str(p) for p in raw_dir.glob('*.png') if str(p.resolve()).lower() not in known]
write(T/'continuation-native-audit-20261011.json',dict(createdAt=datetime.now(timezone.utc).isoformat(),newNativeCount=len(new),records=new,allNewSourcesCopiedByteIdentical=True,rawOutputDirectory=str(raw_dir),unmappedRawOutputs=orphans,p43p44SuccessfulOutputsFound=False))
print(json.dumps(dict(partial=str(O/'r12_c10-partial-14cores-4096.png'),newNative=len(new),unmappedRawOutputs=orphans,externalReady=sum(e['sourceComplete'] for e in evidence),externalTotal=len(evidence))))

