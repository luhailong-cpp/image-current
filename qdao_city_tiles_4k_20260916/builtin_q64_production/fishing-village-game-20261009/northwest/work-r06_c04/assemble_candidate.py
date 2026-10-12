from pathlib import Path
import sys,json,hashlib,copy
from datetime import datetime,timezone
from PIL import Image
import numpy as np
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;B=W.parent;OX,OY=12288,20480
sys.path.insert(0,str(B));sys.path.insert(0,str(B/'work-r03_c04'))
from assemble_r03_c03 import compose
from apply_r03_c04_repairs import minimum_path,window_mask
from workflow import sample
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
version=sys.argv[1] if len(sys.argv)>1 else 'final-v1'
O=W/version;assert not (O/'assembly.json').exists(),'Never overwrite saved assembly; use new version'
O.mkdir(exist_ok=True);Q=O/'qa';Q.mkdir(exist_ok=True)
patches=[];sources=[]
for r in range(1,5):
 for c in range(1,5):
  e=read(W/'selections'/f's{r:02d}_s{c:02d}.json');p=Path(e['file']);g=read(str(p)+'.generation.json');assert sha(p)==e['sha256']==g['sha256']
  im=Image.open(p);assert im.size==(1254,1254);patches.append(np.asarray(im.convert('RGB')).copy())
  sources.append({'sourceId':len(sources)+1,'row':r,'column':c,'file':str(p),'sha256':sha(p),'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'globalNativeBox':g['globalNativeBox'],'globalCoreBox':g['globalCoreBox'],'nativeScaleResampled':False,'actualModel':None,'actualQuality':None})
pixels,ids,seams=compose(patches);ids=ids.astype(np.uint16)
north_ap= B/'work-r05_c04/final-v2-20261012/assembly.json'
north,valid,oldids,na=sample(north_ap,[OX,OY,OX+4096,OY+115]);assert valid.all()
cost=np.sum((pixels[:115].astype(np.int32)-north.astype(np.int32))**2,axis=2,dtype=np.int64)
path,total=minimum_path(cost.T,1,114)
take=np.arange(115)[:,None]<path[None,:]
mapping={}
for s in na['sources']:
 old=s.get('sourceId',s.get('jointSourceId'))
 if not ((oldids==old)&take).any():continue
 e=copy.deepcopy(s);e['sourceId']=len(sources)+1;e['inheritedFrom']={'assembly':str(north_ap),'sha256':sha(north_ap),'sourceId':old};sources.append(e);mapping[old]=e['sourceId']
pixels[:115][take]=north[take]
for old,new in mapping.items():ids[:115][take&(oldids==old)]=new
inherit={'assembly':str(north_ap),'sha256':sha(north_ap),'globalBox':[OX,OY,OX+4096,OY+115],'pathYByX':path.tolist(),'pathCostSumSquaredRGB':total,'selectionRule':'north native pixels where y<pathYByX in first115 rows','pixelCount':int(take.sum()),'sourceIdMapping':mapping,'resample':False,'feather':False}
overlays=[]
plan=W/'repair-plan.json'
if plan.exists():
 for e in read(plan)['overlays']:
  p=Path(e['file']);g=read(str(p)+'.generation.json');assert sha(p)==g['sha256'];box=g['globalNativeBox'];x,y=box[0]-OX,box[1]-OY
  assert 0<=x<=4096-1254 and 0<=y<=4096-1254
  incoming=np.asarray(Image.open(p).convert('RGB'));crop=pixels[y:y+1254,x:x+1254];mask,paths=window_mask(crop,incoming,e['window'])
  sid=len(sources)+1;sources.append({'sourceId':sid,'file':str(p),'sha256':sha(p),'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'globalNativeBox':box,'nativeScaleResampled':False,'actualModel':None,'actualQuality':None})
  crop[mask]=incoming[mask];ids[y:y+1254,x:x+1254][mask]=sid;mp=O/(e['id']+'.mask.png');Image.fromarray(mask.astype(np.uint8)*255).save(mp)
  overlays.append({'id':e['id'],'sourceId':sid,'globalNativeBox':box,'selectedPixels':int(mask.sum()),'window':e['window'],'mask':str(mp),'maskSha256':sha(mp),'paths':paths})
out=O/'r06_c04.candidate.png';ip=O/'r06_c04.source-id.png';Image.fromarray(pixels).save(out);Image.fromarray(ids).save(ip)
counts=[];evidence=[];miss=0
for s in sources:
 sid=s['sourceId'];p=Path(s['file']);assert sha(p)==s['sha256'];arr=np.asarray(Image.open(p).convert('RGB'));yy,xx=np.nonzero(ids==sid);g=s['globalNativeBox'];sx,sy=xx+OX-g[0],yy+OY-g[1]
 assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254))
 n=int(np.any(arr[sy,sx]!=pixels[yy,xx],axis=1).sum());miss+=n
 counts.append({'sourceId':sid,'pixelCount':int(xx.size),'pixelMismatches':n})
 if not xx.size:continue
 gp=Path(s['generationRecord']);assert sha(gp)==s['generationRecordSha256'];r=read(gp);pf=Path(r['prompt']);req=Path(r['evidence']['request']);rec=Path(r['evidence']['receipt']);q=read(req);rr=read(rec)
 assert r['tool']=='image_gen.imagegen' and r['route']=='builtin' and r['nativeScaleResampled'] is False
 assert r['sha256']==sha(p) and [r['width'],r['height']]==[1254,1254]
 assert q['prompt'].strip()==pf.read_text(encoding='utf-8-sig').strip() and rr['output_hint']
 assert [Path(z['file']) for z in r['references']]==[Path(z) for z in q['referenced_image_paths']]
 for ref in r['references']:assert sha(ref['file'])==ref['sha256'] and ref['role']
 original=Path(rr['originalFile']);assert sha(original)==sha(p)
 evidence.append({'sourceId':sid,'file':str(p),'sha256':sha(p),'generationRecord':{'file':str(gp),'sha256':sha(gp)},'prompt':{'file':str(pf),'sha256':sha(pf)},'request':{'file':str(req),'sha256':sha(req)},'receipt':{'file':str(rec),'sha256':sha(rec)},'toolOriginal':{'file':str(original),'sha256':sha(original)},'references':r['references'],'configSnapshot':r.get('configSnapshot'),'submittedParameters':r['submittedParameters'],'actualModel':r['actualModel'],'actualQuality':r['actualQuality'],'unverifiedReason':r.get('unverifiedReason')})
assert miss==0 and ids.min()>0 and sum(c['pixelCount'] for c in counts)==4096**2
proof={'verifiedPixels':4096**2,'pixelMismatches':miss,'uncovered':int((ids==0).sum()),'allPixelsNativeExact':True,'noResampling':True,'counts':counts,'generationEvidenceFilesVerifiedForUsedSources':True,'actualModelQualityUnverified':True}
pp=O/'replay-proof.json';write(pp,proof);ep=O/'source-evidence.json';write(ep,{'sources':evidence,'usedSources':len(evidence),'createdAt':datetime.now(timezone.utc).isoformat(),'route':'builtin'})
sp=O/'seams.json';write(sp,{'nativeOverlap':230,'method':'minimum-error hard cut; no feather','internal':seams,'northInheritance':inherit,'overlays':overlays})
a={'tile':'r06_c04','globalCoreBox':[OX,OY,OX+4096,OY+4096],'candidate':{'file':str(out),'sha256':sha(out)},'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'sources':sources,'nativeSize':[1254,1254],'nativeCoreSize':[1024,1024],'stride':1024,'halo':115,'overlap':230,'outputSize':[4096,4096],'createdAt':datetime.now(timezone.utc).isoformat(),'status':'complete-candidate-pending-visual-QA','formalAccepted':False,'published':False,'completeMap':False,'composition':{'method':'16 native patches minimum-error hard cuts plus exact north-native inheritance; optional recorded native repair windows','resample':False,'feather':False,'paint':False,'colorMatching':False,'pixelValueRewriting':False,'guidePixelsUsed':False,'allPixelsEqualRecordedNativeRGB':True},'seams':{'file':str(sp),'sha256':sha(sp)},'northInheritance':inherit,'overlays':overlays,'proof':{'file':str(pp),'sha256':sha(pp)},'sourceEvidence':{'file':str(ep),'sha256':sha(ep)},'script':{'file':str(Path(__file__)),'sha256':sha(__file__)},'clientValidated':False,'navigationValidated':False,'capacity5000Validated':False}
write(O/'assembly.json',a)
for r in range(4):
 for c in range(4):Image.fromarray(pixels[r*1024:(r+1)*1024,c*1024:(c+1)*1024]).save(Q/f'core-{r+1}-{c+1}.100pct.png')
for r in range(4):
 im=Image.new('RGB',(1200,1024))
 for k in [1,2,3]:im.paste(Image.fromarray(pixels[r*1024:(r+1)*1024,k*1024-200:k*1024+200]),((k-1)*400,0))
 im.save(Q/f'vertical-row-{r+1}.native.png')
for c in range(4):
 im=Image.new('RGB',(1024,1200))
 for k in [1,2,3]:im.paste(Image.fromarray(pixels[k*1024-200:k*1024+200,c*1024:(c+1)*1024]),(0,(k-1)*400))
 im.save(Q/f'horizontal-col-{c+1}.native.png')
for r in [1,2,3]:
 for c in [1,2,3]:Image.fromarray(pixels[r*1024-260:r*1024+260,c*1024-260:c*1024+260]).save(Q/f'junction-{r}-{c}.100pct.png')
northim=np.asarray(Image.open(na['candidate']['file']).convert('RGB'))
for j in range(4):
 Image.fromarray(np.concatenate([northim[-200:,j*1024:(j+1)*1024],pixels[:200,j*1024:(j+1)*1024]],axis=0)).save(Q/f'north-{j+1}.100pct.png')
 Image.fromarray(pixels[j*1024:(j+1)*1024,:400]).save(Q/f'west-interior-{j+1}.100pct.png')
 Image.fromarray(pixels[j*1024:(j+1)*1024,-400:]).save(Q/f'east-interior-{j+1}.100pct.png')
 Image.fromarray(pixels[-400:,j*1024:(j+1)*1024]).save(Q/f'south-interior-{j+1}.100pct.png')
Image.fromarray(pixels).resize((1024,1024),Image.Resampling.LANCZOS).save(Q/'overview-review-only.png')
print(json.dumps({'candidate':str(out),'sha256':sha(out),'sources':len(sources),'proof':{k:proof[k] for k in ['verifiedPixels','pixelMismatches','uncovered','generationEvidenceFilesVerifiedForUsedSources']}}))

