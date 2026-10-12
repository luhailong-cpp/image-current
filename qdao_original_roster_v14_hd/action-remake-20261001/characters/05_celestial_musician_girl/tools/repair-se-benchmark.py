"""Export only the five reviewed SE shoe corrections with the existing fixed transform.
Preparation cannot approve artwork. Promotion requires a SHA-bound visual acceptance.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, sys, shutil
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
REVIEW=ROOT/'provenance/bamboo-reference-20261003'
VERSIONS={1:3,2:3,3:3,12:2,13:3}
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
reg=load(ROOT/'registration.json');scale=reg['globalScale'];sx,sy=reg['sequences']['run/SE']['sourceRoot'];tx,ty=reg['targetRoot']
assert scale==0.65 and [sx,sy]==[680,1195] and [tx,ty]==[512,942]
matrix=(1/scale,0,sx-tx/scale,0,1/scale,sy-ty/scale)
rows=[]
for frame,version in VERSIONS.items():
    native=f'staging/run/SE/{frame:02}-v{version}.native.png';record=f'provenance/run/SE{frame:02}-v{version}.generation.json'
    if not (ROOT/native).exists(): continue
    generation=load(ROOT/record)
    assert sha(ROOT/native)==generation['sha256']
    im=Image.open(ROOT/native);im.load();assert im.size==(1254,1254) and im.mode=='RGBA'
    if '--prepare' in sys.argv:
        out=f'staging/run/SE/review-{frame:02}.png'
        exported=im.convert('RGBa').transform((1024,1024),Image.Transform.AFFINE,matrix,Image.Resampling.BICUBIC,fillcolor=(0,0,0,0)).convert('RGBA')
        alpha=exported.getchannel('A')
        border=max(alpha.crop(b).getextrema()[1] for b in [(0,0,1024,1),(0,1023,1024,1024),(0,0,1,1024),(1023,0,1024,1024)])
        assert border==0
        box=im.getchannel('A').point(lambda a:255 if a>32 else 0).getbbox()
        projected=[scale*(box[0]-sx)+tx,scale*(box[1]-sy)+ty,scale*(box[2]-sx)+tx,scale*(box[3]-sy)+ty]
        assert min(projected[:2])>=4 and max(projected[2:])<=1020
        exported.save(ROOT/out)
        meta={'operation':'uniform_resample_and_constant_sequence_registration','status':'pending_visual_review','createdAt':now,'file':out,'sha256':sha(ROOT/out),'width':1024,'height':1024,'mode':'RGBA','source':{'file':native,'sha256':generation['sha256'],'nativeSize':[1254,1254],'generationRecord':record},'actualModel':None,'actualQuality':None,'transform':{'globalScale':scale,'sourceRoot':[sx,sy],'targetRoot':[tx,ty],'inverseAffine':matrix,'registrationFile':'registration.json','perFrameNormalization':False},'edgeMaxAlpha':border,'projectedVisibleBBox':projected,'finalVisualPassed':False,'clientValidated':False,'sourceGeneration':generation,'nativeSourceRecord':record}
        save(ROOT/(out+'.generation.json'),meta)
    rows.append({'frame':frame,'native':native,'record':record,'nativeSha256':generation['sha256'],'reviewFile':f'staging/run/SE/review-{frame:02}.png'})
if '--promote' in sys.argv:
    assert len(rows)==5
    accepted=load(REVIEW/'SE-repair-acceptance.json')
    assert accepted['accepted'] is True and accepted['clientValidated'] is False
    accepted_by_frame={r['frame']:r for r in accepted['frames']}
    selection=load(ROOT/'final-selection.json');manifest=load(ROOT/'final/manifest.json')
    old_records=[]
    for item in rows:
        frame=item['frame'];accepted_item=accepted_by_frame[frame]
        assert accepted_item['nativeSha256']==item['nativeSha256']
        meta=load(ROOT/(item['reviewFile']+'.generation.json'))
        assert sha(ROOT/item['reviewFile'])==meta['sha256']==accepted_item['sha256']
        row=next(r for r in selection if r['action']=='run' and r['direction']=='SE' and r['frame']==frame)
        old_records.append({'selection':dict(row),'generationRecord':load(ROOT/row['generationRecord'])})
    # Keep text lineage; old PNGs are superseded in place only after visual acceptance.
    assert not (REVIEW/'SE-superseded-records.json').exists()
    save(REVIEW/'SE-superseded-records.json',{'replacedAt':now,'records':old_records})
    for item in rows:
        frame=item['frame'];row=next(r for r in selection if r['action']=='run' and r['direction']=='SE' and r['frame']==frame)
        meta=load(ROOT/(item['reviewFile']+'.generation.json'))
        shutil.copyfile(ROOT/item['reviewFile'],ROOT/row['file'])
        meta.update(file=row['file'],status='offline_artwork_accepted_client_pending',finalVisualPassed=True,offlineAcceptance='provenance/bamboo-reference-20261003/SE-repair-acceptance.json',sourceRetention='native/intermediate PNG removed after final-reference verification per user policy; text lineage retained')
        save(ROOT/row['generationRecord'],meta)
        row.update(sha256=meta['sha256'],nativeSourceFile=item['native'],nativeSha256=item['nativeSha256'],visualStatus='竹弓同向复核后的近右靴方向局部修复通过；客户端未验收',finalVisualPassed=True,clientValidated=False)
    manifest.update(frames=selection,artworkUpdatedAt=now,status='offline_artwork_complete_client_pending',latestVisualAcceptance='provenance/bamboo-reference-20261003/SE-repair-acceptance.json')
    save(ROOT/'final-selection.json',selection);save(ROOT/'final/manifest.json',manifest)
    save(REVIEW/'SE-repair-promotion.json',{'promotedAt':now,'frames':rows,'changedFinalFiles':[f'final/run/SE/{r["frame"]:02}.png' for r in rows]})
print(json.dumps({'preparedOrPromoted':len(rows),'mode':sys.argv[1:]},ensure_ascii=False))
