from pathlib import Path
import json,hashlib,re
from datetime import datetime,timezone
import numpy as np
from PIL import Image
from assemble_r03_c03 import append_hard
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def resolve(p):return Path(p) if Path(p).is_absolute() else ROOT/p
records=[]
for rp in sorted((ROOT/'native').glob('*.png.generation.json')):
 r=read(rp);p=resolve(r['file'])
 records.append({'id':p.stem,'file':str(p),'sha256':sha(p),'generationRecord':str(rp),'generationRecordSha256':sha(rp),'globalCoreBox':r['globalCoreBox'],'globalNativeBox':r['globalNativeBox'],'hashMatchesRecord':sha(p)==r['sha256']})
coords={}
for e in records:
 m=re.match(r'(r\d{2}_c\d{2})_s(\d{2})_s(\d{2})_v',e['id'])
 if m:coords.setdefault(m[1],set()).add((int(m[2]),int(m[3])))
ack={'schemaVersion':1,'zone':'northwest','acknowledgedAt':datetime.now(timezone.utc).isoformat(),'gateFile':str(ROOT.parents[1]/'capacity-layout-gate-20261010.json'),'status':'generation-held-awaiting-root-layout-capacity-review','inFlightStatus':{'root':False,'cloth_center_column':False,'cloth_wall_column':False,'r03c04_qa':False,'pendingNativeToolResult':False},'newImageGenerationAllowed':False,'newCoordinatesAllowed':False,'existingArtworkPreserved':True,'target4kCount':49,'generatedCoordinatesByTile':{k:[list(v) for v in sorted(vs)] for k,vs in sorted(coords.items())},'missingCoreCoordinatesByStartedTile':{k:[[r,c] for r in range(1,5) for c in range(1,5) if (r,c) not in vs] for k,vs in sorted(coords.items())},'nativeResultsIncludingRetries':len(records),'nativeRecords':records,'worldSizeConfirmed':False,'capacity5000Validated':False,'releaseAuthority':'Main root after layout/scale review; zone cannot self-release','lastKnownReferenceIssue':{'file':'D:/work/image/designs/mail-ui-v1/01-mail-event.png','currentExists':Path('D:/work/image/designs/mail-ui-v1/01-mail-event.png').exists(),'historicalSha256':'3cf0b7d7b3bae337d51e947719588419a01ae21bdce9bccedd6258ce1feef0a2','note':'Historical evidence remains unchanged. Missing current reference blocks full reference-file revalidation and future generation, separately from capacity gate.'},'subordinateAcks':['work-r03_c04/qa/capacity-gate-ack-20261010.json','work-r05_c03/qa/capacity-gate-ack.json']}
write(ROOT/'capacity-gate-ack.json',ack)
# Compose only the existing selected 3x4 native pixels; no synthesized or resampled pixels.
sel=read(ROOT/'work-r04_c04/selected.json')['sources']
assert len(sel)==12 and [(s['row'],s['column']) for s in sel]==[(r,c) for r in range(1,4) for c in range(1,5)]
strips=[];stripids=[];seams=[]
for row in range(3):
 arrs=[np.array(Image.open(resolve(s['file'])).convert('RGB')) for s in sel[row*4:row*4+4]]
 a=arrs[0];ids=np.full(a.shape[:2],row*4+1,np.uint8)
 for col in range(1,4):
  a,ids,z=append_hard(a,ids,arrs[col],np.full(arrs[col].shape[:2],row*4+col+1,np.uint8),f'partial-row{row+1}-col{col}')
  seams.append(z)
 strips.append(a);stripids.append(ids)
a,ids=strips[0],stripids[0]
for row in range(1,3):
 a,ids,z=append_hard(a.transpose(1,0,2),ids.T,strips[row].transpose(1,0,2),stripids[row].T,f'partial-row{row}-to-{row+1}')
 a=a.transpose(1,0,2);ids=ids.T;seams.append(z)
a=a[115:3187,115:4211];ids=ids[115:3187,115:4211]
counts=[]
for s in sel:
 ys,xs=np.nonzero(ids==s['sourceId']);src=np.array(Image.open(resolve(s['file'])).convert('RGB'))
 sx=xs+115-(s['column']-1)*1024;sy=ys+115-(s['row']-1)*1024
 assert np.array_equal(a[ys,xs],src[sy,sx])
 counts.append({'sourceId':s['sourceId'],'pixels':len(xs)})
out=ROOT/'work-r04_c04/tiles';out.mkdir(exist_ok=True)
p=out/'r04_c04.first-three-rows.partial.png';Image.fromarray(a).save(p)
ip=out/'r04_c04.first-three-rows.source-id.png';Image.fromarray(ids).save(ip)
write(out/'r04_c04.first-three-rows.assembly.json',{'tile':'r04_c04','status':'partial-3x4-construction-only-known-defects','candidate':str(p),'sha256':sha(p),'size':[4096,3072],'globalBox':[12288,12288,16384,15360],'sources':sel,'pixelSourceVerified':True,'pixelCount':sum(v['pixels'] for v in counts),'sourceIdMap':str(ip),'sourceIdSha256':sha(ip),'seams':seams,'counts':counts,'resample':False,'blend':False,'newArtworkGenerated':False})
# Export true fixed 4K tile boundaries, not hypothetical adaptive pair cuts.
qa=ROOT/'qa/capacity-gate';qa.mkdir(parents=True,exist_ok=True)
pairs=[('r03c03-r04c03-north','v',ROOT/'tiles/r03_c03.candidate-repair-v5.png',ROOT/'work-r04_c03/output/r04_c03.candidate.png',4096),('r04c03-r04c04-west-partial','h',ROOT/'work-r04_c03/output/r04_c03.candidate.png',p,3072)]
outputs=[]
for name,direction,pa,pb,length in pairs:
 ia,ib=Image.open(pa),Image.open(pb)
 for start in range(0,length,512):
  end=min(start+512,length)
  if direction=='v':
   cut=Image.new('RGB',(end-start,460));cut.paste(ia.crop((start,4096-230,end,4096)),(0,0));cut.paste(ib.crop((start,0,end,230)),(0,230))
  else:
   cut=Image.new('RGB',(460,end-start));cut.paste(ia.crop((4096-230,start,4096,end)),(0,0));cut.paste(ib.crop((0,start,230,end)),(230,0))
  cp=qa/f'{name}-s{start//512+1}.png';cut.save(cp)
  outputs.append({'file':str(cp),'sha256':sha(cp),'pair':name,'axis':direction,'span':[start,end],'seamCoordinateInCrop':230,'unscaled':True})
write(qa/'true-boundary-crops.json',{'crops':outputs,'limitation':'fixed-final/partial boundaries; unchanged pixels; visual evaluation required'})
print(json.dumps({'ack':str(ROOT/'capacity-gate-ack.json'),'nativeResults':len(records),'coveredCoreCoordinates':sum(map(len,coords.values())),'partial':str(p),'partialPixelCount':a.shape[0]*a.shape[1],'boundaryCrops':len(outputs)}))

