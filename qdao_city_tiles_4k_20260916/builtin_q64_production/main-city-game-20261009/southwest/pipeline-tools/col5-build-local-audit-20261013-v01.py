from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image, ImageDraw

B=Path(__file__).resolve().parents[1]
O=B/'pipeline-tools/col5-local-audit-20261013-v01'
assert not O.exists(); O.mkdir()
read=lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,d: Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
catalog=B/'current-candidates.json'; cat=read(catalog)['tiles']
model=Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')
records=[]; sources={}; images={}
for row in range(9,15):
    tile=f'r{row:02d}_c05'; entry=cat[tile]; e=entry['candidate']; p=Path(e['file'])
    assert sha(p)==e['sha256']; im=Image.open(p).convert('RGB'); assert im.size==(4096,4096)
    sources[tile]={'candidate':e,'assembly':entry.get('assembly'),'assemblySha256':sha(Path(entry['assembly'])) if entry.get('assembly') else None,'sourceEntry':entry}
    images[tile]=im
def save(name,im,kind,source,box=None,extra=None):
    p=O/(name+'.png');p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();im.save(p)
    with Image.open(p) as v:assert v.size==im.size and v.tobytes()==im.tobytes()
    e={'id':name,'file':str(p),'sha256':sha(p),'pixels':list(im.size),'kind':kind,'source':source,'cropBox':box,'QAOnly':True,'sourceResampling':False,'visualQa':'pending'}
    if extra:e.update(extra)
    records.append(e);return e
def panel(name,entries,vertical=False):
    first=Image.open(entries[0]['file']).convert('RGB');w,h=first.size
    canvas=Image.new('RGB',((w+16)*len(entries),h+24) if vertical else (w,(h+24)*len(entries)),(255,255,255));d=ImageDraw.Draw(canvas)
    for k,e in enumerate(entries):
        part=Image.open(e['file']).convert('RGB');assert part.size==first.size
        x,y=((w+16)*k,24) if vertical else (0,(h+24)*k+24)
        canvas.paste(part,(x,y));d.text((x+3,y-20),e['id'].split('/')[-1],fill=(0,0,0))
    return save(name,canvas,'native-crop-panel',[{'file':e['file'],'sha256':e['sha256']} for e in entries],extra={'members':[e['id'] for e in entries],'cropPixelsUnchanged':True})
for tile in ['r13_c05','r14_c05']:
    im=images[tile];src=sources[tile]['candidate'];groups={}
    for c in range(1,4):
        group=[]
        for r in range(4):
            box=[c*1024-119,r*1024,c*1024+119,(r+1)*1024]
            group.append(save(f'{tile}/V{c}-{r+1}',im.crop(box),'internal-vertical-seam',src,box))
        panel(f'{tile}/V{c}-panel',group,True)
    for r in range(1,4):
        group=[]
        for c in range(4):
            box=[c*1024,r*1024-119,(c+1)*1024,r*1024+119]
            group.append(save(f'{tile}/H{r}-{c+1}',im.crop(box),'internal-horizontal-seam',src,box))
        panel(f'{tile}/H{r}-panel',group)
    for r in range(1,4):
        group=[]
        for c in range(1,4):
            box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256]
            group.append(save(f'{tile}/X{r}-{c}',im.crop(box),'internal-intersection',src,box))
        panel(f'{tile}/X{r}-panel',group,True)
for row in range(9,14):
    upper=f'r{row:02d}_c05';lower=f'r{row+1:02d}_c05';group=[]
    for k in range(4):
        box1=[k*1024,3968,(k+1)*1024,4096];box2=[k*1024,0,(k+1)*1024,128]
        a=images[upper].crop(box1);b=images[lower].crop(box2);im=Image.new('RGB',(1024,256));im.paste(a,(0,0));im.paste(b,(0,128))
        group.append(save(f'chain/{upper}--{lower}-{k+1}',im,'external-horizontal-junction',[sources[upper]['candidate'],sources[lower]['candidate']],extra={'sourceBoxes':[box1,box2],'boundaryPixelY':128,'upperTile':upper,'lowerTile':lower,'externalJunctionReviewed':False}))
    panel(f'chain/{upper}--{lower}-panel',group)
# Existing r13c06 partial candidate provides exactly the top1024 pixels of the right boundary.
PA=B/'r13_c06/pipeline/output/e7b5e8d88639ad53/assembly.json';a=read(PA);p=Path(a['output']['file']);assert sha(p)==a['output']['sha256'];n=Image.open(p).convert('RGB');assert n.size==(2048,1024)
im=Image.new('RGB',(256,1024));im.paste(images['r13_c05'].crop((3968,0,4096,1024)),(0,0));im.paste(n.crop((0,0,128,1024)),(128,0))
save('r13_c05/right-partial-row1',im,'external-partial-vertical-junction',[sources['r13_c05']['candidate'],a['output']],extra={'sourceBoxes':[[3968,0,4096,1024],[0,0,128,1024]],'boundaryPixelX':128,'availableBoundaryPixels':1024,'remainingBoundaryPixels':3072,'neighborAssembly':str(PA),'neighborAssemblySha256':sha(PA)})
inventory=[]
for row in range(9,17):
    tile=f'r{row:02d}_c05';t=B/tile;selection=read(t/'refinement/selection.json') if (t/'refinement/selection.json').is_file() else {};present=[];missing=[]
    for r in range(1,5):
        for c in range(1,5):
            pid=f'p{r:02d}_{c:02d}';rel=selection.get(pid,'native/'+pid+'.png.generation.json');record=t/rel
            if record.is_file() and Path(read(record)['file']).is_file():present.append(pid)
            else:missing.append(pid)
    inventory.append({'tile':tile,'selectedNativeSlots':len(present),'missingNativeSlots':len(missing),'presentPatchIds':present,'missingPatchIds':missing,'currentCandidate':sources.get(tile),'formalAccepted':False})
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'purpose':'local-only exact native QA and repair queue support; no image generation','modelRequirement':{'file':str(model),'sha256':sha(model),'requestedExactModel':'GPT Image 2.5','verifiedExplicitGenerationRouteAvailable':False,'newGenerationPaused':True},'catalogRead':{'file':str(catalog),'sha256':sha(catalog),'copiedOrEdited':False},'sourceCandidates':sources,'inventory':inventory,'records':records,'sourceResampling':False,'artworkModified':False,'generationCalls':0,'actualModel':None,'actualQuality':None,'internalAccepted':False,'formalAccepted':False,'missingExternalNeighbors':{'r13_c05':['left r13_c04 entire4096','right r13_c06 remaining3072'],'r14_c05':['left r14_c04 entire4096','right r14_c06 entire4096','bottom r15_c05 entire4096']}}
write(O/'manifest.json',manifest)
print(json.dumps({'folder':str(O),'manifest':str(O/'manifest.json'),'nativeCropsAndPanels':len(records),'missingLaneNativeSlots':sum(x['missingNativeSlots'] for x in inventory)},ensure_ascii=False))
