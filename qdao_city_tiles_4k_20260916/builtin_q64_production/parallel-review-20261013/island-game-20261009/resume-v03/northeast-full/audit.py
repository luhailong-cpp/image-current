from pathlib import Path
from PIL import Image, ImageChops
import json, hashlib, datetime, re

ROOT=Path('D:/work/image')
PROD=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast'
OUT=Path(__file__).resolve().parent
AUDIT=OUT.parent.parent
SNAP={}
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def track(p):
    p=Path(p); s=sha(p); SNAP[p.as_posix()]=s; return s
def read(p):
    track(p);return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def same(a,b): return a.size==b.size and ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox() is None
def info(p):
    with Image.open(p) as im: size=list(im.size)
    return dict(file=Path(p).as_posix(),sha256=track(p),dimensions=size)
def save(im,p,**kw):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
    return dict(file=p.as_posix(),sha256=sha(p),dimensions=list(im.size),resized=False,actuallyViewed=False,**kw)
def world(t):
    r,c=map(int,re.match(r'r(\d+)_c(\d+)',t).groups());return [(c-1)*4096,(r-1)*4096,c*4096,r*4096]
def bbox_for(name,size):
    n=re.findall(r'\d+',name);a,b=map(int,n[:2]);w,h=size
    if name.startswith('core'):return [(b-1)*1024,(a-1)*1024,b*1024,a*1024]
    if name.startswith('cross'):return [b*1024-w//2,a*1024-h//2,b*1024+w//2,a*1024+h//2]
    if name.startswith('horizontal'):return [(b-1)*1024,a*1024-h//2,b*1024,a*1024+h//2]
    if name.startswith('vertical'):return [a*1024-w//2,(b-1)*1024,a*1024+w//2,b*1024]
    raise ValueError(name)

start=now()
for p in [ROOT/'AGENTS.md',ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json']:track(p)
base=read(AUDIT/'resume-v02/northeast/summary.json')
older=read(AUDIT/'root-audit-v01/inventory.json')
baseline={t['tileId']:t for t in base['tiles']}
tiles=[];images={};evidence=[];reused=[];edges=[]
for tid in ['r03_c10','r05_c11']:
    sp=PROD/f'selection-{tid}.json';s=read(sp);write(OUT/'frozen'/sp.name,s)
    ox,oy,_,_=world(tid);canvas=Image.new('RGB',(4096,4096));srcs=[];ov=[]
    for r,row in enumerate(s['cores']):
        for c,ident in enumerate(row):
            assert ident
            p=PROD/'native'/f'{ident}.png';d=info(p);rec=read(str(p)+'.generation.json')
            assert d['sha256']==rec['sha256'] and d['dimensions']==[1254,1254]
            assert rec['coreCrop']==[115,115,1139,1139] and rec['resizedAfterGeneration'] is False
            assert rec['coreWorldBox']==[ox+c*1024,oy+r*1024,ox+(c+1)*1024,oy+(r+1)*1024]
            with Image.open(p) as im:canvas.paste(im.crop((115,115,1139,1139)),(c*1024,r*1024))
            srcs.append(dict(id=ident,**d,coreWorldBox=rec['coreWorldBox'],actualModel=rec.get('actualModel')))
    for ident in s.get('overlays',[]):
        p=PROD/'qa'/f'{ident}.overlay.json';q=read(p);d=info(q['source']);rec=read(q['source']+'.generation.json')
        assert q['review'].startswith('passed') and d['sha256']==q['sha256']==rec['sha256']
        assert d['dimensions']==[1254,1254] and q['coreCrop']==[115,115,1139,1139]
        assert rec.get('resizedAfterGeneration') is False
        with Image.open(q['source']) as im:canvas.paste(im.crop(tuple(q['coreCrop'])),tuple(q['tileLocalPaste']))
        ov.append(dict(record=p.as_posix(),**q))
    f=s['candidatePath'];fi=info(f);im=Image.open(f).convert('RGB');assert fi['dimensions']==[4096,4096] and same(canvas,im)
    images[tid]=im;canvas.close()
    rp=s['reviewPath'];q=read(rp);assert q['sha256']==fi['sha256'];write(OUT/'frozen'/Path(rp).name,q)
    qa=[]
    for e in q['inspectedCrops']:
        with Image.open(e['file']) as crop:
            box=bbox_for(Path(e['file']).name,crop.size);valid=same(im.crop(box),crop) and track(e['file'])==e['sha256']
        assert valid,(tid,e['file'],box)
        qa.append(dict(file=e['file'],sha256=e['sha256'],tileLocalBox=box,status=e['status'],currentPixelsIdentical=valid,reusable=e['status'].startswith('passed')))
    t=dict(tileId=tid,coreCount=16,fullCoverage=True,adopted=True,formalAccepted=False,**fi,selectedCores=s['cores'],selectionFile=sp.as_posix(),selectionSha256=SNAP[sp.as_posix()],sources=srcs,overlays=ov,replayMatchesCandidate=True,replayPixelCount=4096*4096,productionInternalReview=s['internalReview'],productionPendingIssues=s['pendingIssues'],evidence=qa)
    t['baselineDelta']=dict(priorCoreCount=baseline[tid]['coreCount'],priorCandidate=baseline[tid].get('file'),priorSha256=baseline[tid].get('sha256'),coreMatrixChanged=s['cores']!=baseline[tid]['selectedCores'])
    tiles.append(t)
    print(tid,'replay exact','reusable production crops',sum(e['reusable'] for e in qa),flush=True)

# r03_c10: all pixels outside the sole 1024-square overlay must equal the audited v1.
t=tiles[0];old=baseline['r03_c10'];assert track(old['file'])==old['sha256']
with Image.open(old['file']) as prev:
    diff=ImageChops.difference(prev.convert('RGB'),images['r03_c10']);change=diff.getbbox()
assert change and change[0]>=2560 and change[1]>=1024 and change[2]<=3584 and change[3]<=2048
t['baselineDelta'].update(changedPixelBoundingBox=list(change),outsideOverlayPixelIdentical=True)
box=[2304,768,3840,2304]
evidence.append(save(images['r03_c10'].crop(box),OUT/'r03_c10-overlay-and-boundaries-100pct.png',tileId='r03_c10',tileLocalBox=box,kind='changed_overlay_with_all_four_edges_and_corners'))

# r05_c11: new first-column cores, adjacent seams, and changed lantern core.
im=images['r05_c11']; d=OUT/'r05_c11-internal';d.mkdir(exist_ok=True)
entries=[]
for a in range(1,4):
    box=[0,a*1024-256,1024,a*1024+256]
    entries.append(save(im.crop(box),d/f'horizontal-{a}-segment-1-100pct.png',tileId='r05_c11',tileLocalBox=box,kind='new_column_horizontal_seam'))
for b in range(4):
    box=[768,b*1024,1280,(b+1)*1024]
    entries.append(save(im.crop(box),d/f'vertical-1-segment-{b+1}-100pct.png',tileId='r05_c11',tileLocalBox=box,kind='new_column_vertical_seam'))
for a in range(1,4):
    box=[768,a*1024-256,1280,a*1024+256]
    entries.append(save(im.crop(box),d/f'cross-{a}-1-100pct.png',tileId='r05_c11',tileLocalBox=box,kind='new_column_cross'))
for name,box in [('lantern-core',[3072,0,4096,1024]),('lantern-left-boundary',[2816,0,3328,1024]),('lantern-bottom-boundary',[3072,768,4096,1280]),('lantern-lower-left-cross',[2816,768,3328,1280])]:
    entries.append(save(im.crop(box),d/f'{name}-100pct.png',tileId='r05_c11',tileLocalBox=box,kind=name))
evidence.extend(entries)

# Full neighbors only. Partial neighbor work belongs to parent auditor.
for tid in ['r03_c11','r04_c11','r05_c12','r04_c12']:
    s=read(PROD/f'selection-{tid}.json');assert all(all(r) for r in s['cores'])
    p=s.get('candidatePath',str(PROD/'tiles'/f'{tid}.png'));fi=info(p);assert fi['dimensions']==[4096,4096]
    images[tid]=Image.open(p).convert('RGB')
    write(OUT/'frozen'/f'neighbor-{tid}.json',dict(selection=s,candidate=fi))
for a,b,ori in [('r03_c10','r03_c11','vertical'),('r04_c11','r05_c11','horizontal'),('r05_c11','r05_c12','vertical')]:
    edir=OUT/f'{a}__{b}';edir.mkdir(exist_ok=True);segs=[]
    wa=world(a)
    for n in range(4):
        if ori=='vertical':
            crop=Image.new('RGB',(512,1024));crop.paste(images[a].crop((3840,n*1024,4096,(n+1)*1024)),(0,0));crop.paste(images[b].crop((0,n*1024,256,(n+1)*1024)),(256,0))
            wb=[wa[2]-256,wa[1]+n*1024,wa[2]+256,wa[1]+(n+1)*1024]
        else:
            crop=Image.new('RGB',(1024,512));crop.paste(images[a].crop((n*1024,3840,(n+1)*1024,4096)),(0,0));crop.paste(images[b].crop((n*1024,0,(n+1)*1024,256)),(0,256))
            wb=[wa[0]+n*1024,wa[3]-256,wa[0]+(n+1)*1024,wa[3]+256]
        e=save(crop,edir/f'segment-{n+1}-100pct.png',tiles=[a,b],worldBox=wb,kind='complete_neighbor_edge',segment=n+1)
        segs.append(e)
    if a=='r03_c10':
        # Reuse independent resume-v02 edge where exact RGB is unchanged.
        oldedge=next(e for e in base['newEdgeReviews'] if e['tiles']==[a,b])
        for new,old in zip(segs,oldedge['segments']):
            with Image.open(new['file']) as ni,Image.open(old['file']) as oi:identical=same(ni,oi)
            valid=track(old['file'])==old['sha256']
            assert identical and valid
            new.update(status='passed_reused_identical_independent_evidence',reusedEvidence=old['file'],reusedSha256=old['sha256'],currentPixelsIdentical=True)
            reused.append(new)
    else:evidence.extend(segs)
    edges.append(dict(tiles=[a,b],orientation=ori,segments=segs,formalAccepted=False))

cross=Image.new('RGB',(1024,1024))
for tid,box,paste in [('r04_c11',(3584,3584,4096,4096),(0,0)),('r04_c12',(0,3584,512,4096),(512,0)),('r05_c11',(3584,0,4096,512),(0,512)),('r05_c12',(0,0,512,512),(512,512))]:cross.paste(images[tid].crop(box),paste)
evidence.append(save(cross,OUT/'r04-r05-c11-c12-cross-100pct.png',tiles=['r04_c11','r04_c12','r05_c11','r05_c12'],worldBox=[44544,15872,45568,16896],kind='complete_neighbor_fourway'))

# Contact sheets only paste original pixels, never rescale.
boards=[]
sets=[('new-column-horizontal',[e for e in entries if e['kind']=='new_column_horizontal_seam'],(1024,512),1),('new-column-vertical',[e for e in entries if e['kind']=='new_column_vertical_seam'],(512,1024),4),('new-column-cross',[e for e in entries if e['kind']=='new_column_cross'],(512,512),3),('north-edge',edges[1]['segments'],(1024,512),2),('east-edge',edges[2]['segments'],(512,1024),4)]
for name,es,cell,cols in sets:
    board=Image.new('RGB',(cell[0]*cols,cell[1]*((len(es)+cols-1)//cols)))
    for i,e in enumerate(es):
        with Image.open(e['file']) as im:board.paste(im,((i%cols)*cell[0],(i//cols)*cell[1]))
    bo=save(board,OUT/f'{name}-board-100pct.png',panels=[e['file'] for e in es],operation='exact unscaled pixel paste')
    boards.append(bo)
write(OUT/'input-snapshot.json',dict(capturedAtUtc=start,frozenAtUtc=now(),files=[dict(file=p,sha256=h) for p,h in SNAP.items()]))
write(OUT/'inspection-prepared.json',dict(capturedAtUtc=start,tiles=tiles,edges=edges,evidence=evidence,reused=reused,boards=boards,generationCalls=0,productionWrites=0,formalAcceptedCount=0))
print('ready',len(evidence),'new evidence',len(reused),'reused independent edge segments',flush=True)
