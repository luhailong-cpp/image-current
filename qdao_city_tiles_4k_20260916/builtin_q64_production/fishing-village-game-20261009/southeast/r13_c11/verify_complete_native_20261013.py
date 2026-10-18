"""Independent exact raw-core replay and bounded QA evidence; no art editing."""
from pathlib import Path
from PIL import Image,ImageChops
import sys,json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
from review_external_seams import Sources,write_evidence
tile=sys.argv[1];assert tile in ('r14_c11','r13_c11')
T=Z/tile;Q=T/'qa'/'complete-20261013-v1';out=Q/'independent-replay-proof.json'
assert not out.exists()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
snapshot=sha(T/'selected-patches.json');sel=read(T/'selected-patches.json');assert len(sel['patches'])==16
assembled=Image.new('RGB',(4096,4096));records=[];raws={}
for pid,rel in sorted(sel['patches'].items()):
 p=T/rel;gen=read(p.with_suffix('.png.generation.json'));raw=Path(gen['evidence']['sourcePath'])
 raw_im=Image.open(raw).convert('RGB');native=Image.open(p).convert('RGB');assert raw_im.size==native.size==(1254,1254)
 assert sha(raw)==sha(p)==gen['sha256'];assert ImageChops.difference(raw_im,native).getbbox() is None
 x=(int(pid[2])-1)*1024;y=(int(pid[1])-1)*1024
 assembled.paste(raw_im.crop((115,115,1139,1139)),(x,y))
 records.append(dict(patch=pid,native=str(p),raw=str(raw),sha256=sha(p),rawAndNativePixelDifference=0,coreCrop=[115,115,1139,1139],destination=[x,y]))
candidate=Q/'candidate-4096.png';actual=Image.open(candidate).convert('RGB');assert actual.size==(4096,4096)
assert ImageChops.difference(assembled,actual).getbbox() is None
manifest=read(Q/'manifest.json');reused=[]
for ev in manifest['evidence']:
 name=Path(ev['file']).stem
 if '--' not in name:continue
 a,b=name.split('--')
 options=[(b,'west'),(a,'east')] if a[1]==b[1] else [(b,'north'),(a,'south')]
 prior_pid,side=next((pid,sd) for pid,sd in options if (T/'qa'/('quick-'+Path(sel['patches'][pid]).stem)/(sd+'.png')).exists())
 prior=T/'qa'/('quick-'+Path(sel['patches'][prior_pid]).stem)/(side+'.png')
 prior_m=read(prior.parent/'manifest.json')
 assert ImageChops.difference(Image.open(prior).convert('RGB'),Image.open(ev['file']).convert('RGB')).getbbox() is None
 for s in prior_m['evidence']:
  if s['side']==side:
   for part in s['sources']:assert sha(part['file'])==part['sha256']
 reused.append(dict(seam=name,finalEvidence=ev['file'],priorEvidence=str(prior),pixelIdentical=True,currentSourcesStillMatch=True))
assert len(reused)==24
crosses=[Q/f'cross-r{r}-c{c}.png' for r in range(1,4) for c in range(1,4)]
sheet=Image.new('RGB',(1536,1536))
for i,p in enumerate(crosses):sheet.paste(Image.open(p).convert('RGB'),((i%3)*512,(i//3)*512))
sheetpath=Q/'cross-nine-native-contact.png';assert not sheetpath.exists();sheet.save(sheetpath)
write(sheetpath.with_suffix('.png.derivation.json'),dict(classification='QA only',operation='nine unscaled 512 square cross crops in row-major order',resamplingApplied=False,files=[str(p) for p in crosses],sha256=sha(sheetpath)))
F=T/'qa'/'external-20261013-v1';F.mkdir(exist_ok=False)
S=Sources();r,c=int(tile[1:3]),int(tile[5:7]);x,y=(c-1)*4096,(r-1)*4096;edges=[];crosses={}
for side in ['north','east','south','west']:
 if side=='south' and r==14:edges.append(dict(edge=side,status='outside_canvas_not_required'));continue
 k=x+4096 if side=='east' else x if side=='west' else y+4096 if side=='south' else y
 vert=side in ('east','west');start=y if vert else x
 segs=[]
 for i in range(4):
  b=[k-256,start+i*1024,k+256,start+(i+1)*1024] if vert else [start+i*1024,k-256,start+(i+1)*1024,k+256]
  segs.append(write_evidence(S,F,f'{side}-segment-{i+1}',b,dict(edge=side,seamGlobalCoordinate=k,seamCoordinateInStrip=256)))
 edges.append(dict(edge=side,segments=segs))
 for i in range(1,4):
  px,py=(k,start+i*1024) if vert else (start+i*1024,k);ident=f'intersection-x{px}-y{py}'
  crosses[ident]=write_evidence(S,F,ident,[px-384,py-384,px+384,py+384],dict(intersectionGlobal=[px,py],intersectionInImage=[384,384]))
write(F/'manifest.json',dict(tile=tile,createdAt=datetime.now(timezone.utc).isoformat(),edges=edges,intersections=list(crosses.values()),formalAccepted=False))
stable=sha(T/'selected-patches.json')==snapshot and all(sha(a['native'])==a['sha256'] for a in records)
assert stable
proof=dict(createdAt=datetime.now(timezone.utc).isoformat(),tile=tile,selectionSha256=snapshot,selectionAndSourcesStableAtStartEnd=stable,snapshotAtomic=False,rawSourceCount=16,coreCount=16,corePixels=1024,assembledSize=[4096,4096],candidate=str(candidate),candidateSha256=sha(candidate),candidatePixelDifference=0,replayedDirectlyFromActualBuiltinRaw=True,resamplingApplied=False,layoutPixelsUsed=False,records=records,reusedNativeSeamReviews=reused,crossContact=str(sheetpath),internalReady=False,formalAccepted=False,actualModel=None)
write(out,proof)
print(json.dumps(dict(tile=tile,coreReplay='PASS',candidateSha256=sha(candidate),reusedNativeSeams=len(reused),crosses=9,externalReadySegments=sum(e['sourceComplete'] for a in edges for e in a.get('segments',[])),proof=str(out))))
