from pathlib import Path
import sys,json,hashlib,copy,shutil
from datetime import datetime,timezone
from PIL import Image
import numpy as np
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent; B=W.parent; O=W/'recovered-v1-20261012'; O.mkdir(exist_ok=True); Q=O/'qa'; Q.mkdir(exist_ok=True)
sys.path.insert(0,str(B/'work-r03_c04'))
from apply_r03_c04_repairs import window_mask
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=read(W/'final-v1/assembly.json'); base=Path(a['candidate']['file']); assert sha(base)==a['candidate']['sha256']
pixels=np.asarray(Image.open(base).convert('RGB')).copy(); ids=np.asarray(Image.open(a['sourceIdMap']['file'])).astype(np.uint16).copy(); sources=copy.deepcopy(a['sources']); overlays=[]
caches=['8d0d717b66b317ab-exec-d86849a7-2803-41dd-8026-bc2bd38b4c80.png','23acb3722e8ec97a-exec-c1633a53-82f1-44a1-9eae-f0cb53674b72.png']
for k,cache in enumerate(caches,1):
    original=B/'migration-cache-outputs-20261011'/cache; p=B/'native'/f'r05_c04_recovered_sand_{k:02d}_v01_20261012.png'
    if not p.exists():shutil.copy2(original,p)
    assert sha(p)==sha(original)
    repair=np.asarray(Image.open(p).convert('RGB')); assert repair.shape==(1254,1254,3)
    box=[13850+(k-1)*1024,16900,15104+(k-1)*1024,18154]
    target=W/'guides'/f'r05_c04_sand_band_bridge_{k:02d}_v01.native-target.png'
    evidence={'schemaVersion':1,'file':str(p),'sha256':sha(p),'width':1254,'height':1254,'globalNativeBox':box,'nativeScaleResampled':False,'actualModel':None,'actualQuality':None,'provenanceStatus':'recovered-cache-dispatch-unknown','originalPreservedCache':{'file':str(original),'sha256':sha(original)},'registration':{'method':'visual framing comparison and recorded target coordinate; no resizing or warping','target':str(target),'targetSha256':sha(target),'historicalPreparedRequest':str(W/'receipts'/f'r05_c04_sand_band_bridge_{k:02d}_v01.request.json'),'requestAssociationVerified':False},'tool':None,'route':None,'prompt':None,'references':None,'request':None,'receipt':None,'unverifiedReason':'No tool receipt or verified dispatch association survives for this cache. Registration is an assembly decision, not recovered generation evidence.','recordedAt':datetime.now(timezone.utc).isoformat()}
    rp=Path(str(p)+'.recovered-source.json');write(rp,evidence)
    sid=max(s['sourceId'] for s in sources)+1; sources.append({'sourceId':sid,'file':str(p),'sha256':sha(p),'recoveredSourceRecord':str(rp),'recoveredSourceRecordSha256':sha(rp),'globalNativeBox':box,'nativeScaleResampled':False,'actualModel':None,'actualQuality':None,'provenanceStatus':evidence['provenanceStatus']})
    x,y=box[0]-12288,box[1]-16384; crop=pixels[y:y+1254,x:x+1254]; before=crop.copy(); mask,paths=window_mask(crop,repair,[0,390,1254,910]); crop[mask]=repair[mask];ids[y:y+1254,x:x+1254][mask]=sid
    mp=O/f'recovered-sand-{k}.mask.png';Image.fromarray(mask.astype(np.uint8)*255).save(mp)
    Image.fromarray(before).save(Q/f'sand-{k}.before.100pct.png');Image.fromarray(crop).save(Q/f'sand-{k}.after.100pct.png')
    overlays.append({'sourceId':sid,'id':f'recovered-sand-{k}','file':str(p),'sha256':sha(p),'globalNativeBox':box,'mask':str(mp),'maskSha256':sha(mp),'paths':paths,'selectedPixels':int(mask.sum()),'dispatchAssociationKnown':False})
out=O/'r05_c04.candidate.png';ip=O/'r05_c04.source-id.png';Image.fromarray(pixels).save(out);Image.fromarray(ids).save(ip)
arrays={};counts=[];miss=0
for s in sources:
    assert sha(s['file'])==s['sha256']; arr=np.asarray(Image.open(s['file']).convert('RGB'));arrays[s['sourceId']]=arr
    yy,xx=np.nonzero(ids==s['sourceId']);g=s['globalNativeBox'];sx=xx+12288-g[0];sy=yy+16384-g[1]
    assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254)); n=int(np.any(arr[sy,sx]!=pixels[yy,xx],axis=1).sum());miss+=n;counts.append({'sourceId':s['sourceId'],'pixelCount':int(xx.size),'pixelMismatches':n})
assert miss==0 and ids.min()>0
proof={'verifiedPixels':4096**2,'pixelMismatches':miss,'uncovered':int((ids==0).sum()),'allPixelsNativeExact':True,'noResampling':True,'counts':counts,'generationProvenanceComplete':False,'limitations':['Recovered cache sources have no verified dispatch, prompt, reference list or receipt. Exact source pixels are verified separately from generation provenance.']}; pp=O/'replay-proof.json';write(pp,proof)
a.update({'candidate':{'file':str(out),'sha256':sha(out)},'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'sources':sources,'createdAt':datetime.now(timezone.utc).isoformat(),'baseline':{'candidate':{'file':str(base),'sha256':sha(base)},'assembly':{'file':str(W/'final-v1/assembly.json'),'sha256':sha(W/'final-v1/assembly.json')}},'overlays':a['overlays']+overlays,'proof':{'file':str(pp),'sha256':sha(pp)},'status':'recovered-cache-assembly-pending-visual-QA-and-generation-evidence','formalAccepted':False,'composition':{'method':'baseline exact native source-ID assembly plus minimum-error hard cuts in sand repair windows','resample':False,'feather':False,'paint':False,'colorMatching':False},'script':{'file':str(Path(__file__)),'sha256':sha(__file__)}});write(O/'assembly.json',a)
for name in ['north-delta.json','r04_c04.with-north-head.png','r04_c04.assembly.json','r04_c04.source-id.png','r04_c04.delta-mask.png','r04_c04.delta-source-id.png','north-head-bridge.mask.png']:
    shutil.copy2(W/'final-v1'/name,O/name)
for r in range(4):
    for c in range(4):Image.fromarray(pixels[r*1024:(r+1)*1024,c*1024:(c+1)*1024]).save(Q/f'core-{r+1}-{c+1}.100pct.png')
for r in range(4):
    outm=Image.new('RGB',(1200,1024))
    for k in (1,2,3):outm.paste(Image.fromarray(pixels[r*1024:(r+1)*1024,k*1024-200:k*1024+200]),((k-1)*400,0))
    outm.save(Q/f'vertical-row-{r+1}.native.png')
for c in range(4):
    outm=Image.new('RGB',(1024,1200))
    for k in (1,2,3):outm.paste(Image.fromarray(pixels[k*1024-200:k*1024+200,c*1024:(c+1)*1024]),(0,(k-1)*400))
    outm.save(Q/f'horizontal-col-{c+1}.native.png')
north=np.asarray(Image.open(O/'r04_c04.with-north-head.png').convert('RGB'));west=np.asarray(Image.open(B/'work-r05_c03/final-v1/r05_c03.candidate.png').convert('RGB'))
for j in range(4):
    Image.fromarray(np.concatenate([north[-200:,j*1024:(j+1)*1024],pixels[:200,j*1024:(j+1)*1024]],axis=0)).save(Q/f'north-{j+1}.100pct.png')
    Image.fromarray(np.concatenate([west[j*1024:(j+1)*1024,-200:],pixels[j*1024:(j+1)*1024,:200]],axis=1)).save(Q/f'west-{j+1}.100pct.png')
    Image.fromarray(pixels[j*1024:(j+1)*1024,-400:]).save(Q/f'east-interior-{j+1}.100pct.png')
    Image.fromarray(pixels[-400:,j*1024:(j+1)*1024]).save(Q/f'south-interior-{j+1}.100pct.png')
Image.fromarray(pixels).resize((1024,1024),Image.Resampling.LANCZOS).save(Q/'overview-review-only.png')
print(json.dumps({'candidate':str(out),'sha256':sha(out),'sources':len(sources),'overlays':[{k:v for k,v in z.items() if k in ['sourceId','selectedPixels','sha256']} for z in overlays],'proof':{k:proof[k] for k in ['verifiedPixels','pixelMismatches','uncovered','generationProvenanceComplete']}}))
