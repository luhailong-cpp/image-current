from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
import json, hashlib, datetime, re, gc

ROOT = Path('D:/work/image')
BASE = ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009'
OUT = Path(__file__).resolve().parent
SNAP = {}

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''): h.update(chunk)
    return h.hexdigest()

def track(p):
    p=Path(p); s=sha(p); SNAP[p.as_posix()]=s; return s

def read(p):
    track(p); return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def write(p,d):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def info(p):
    p=Path(p)
    with Image.open(p) as im: sz=list(im.size); mode=im.mode
    return {'file':p.as_posix(),'sha256':track(p),'dimensions':sz,'mode':mode}

def world(tid):
    r,c=map(int,re.fullmatch(r'r(\d+)_c(\d+)',tid).groups())
    return [(c-1)*4096,(r-1)*4096,c*4096,r*4096]

def native(p, expected=None):
    d=info(p); q=Path(str(p)+'.generation.json'); rec=read(q)
    assert d['dimensions']==[1254,1254], p
    assert d['sha256']==rec['sha256'], p
    assert rec.get('resizedAfterGeneration') is False, p
    assert rec['coreCrop']==[115,115,1139,1139], p
    if expected: assert rec['coreWorldBox']==expected,(p,rec['coreWorldBox'],expected)
    d.update(generationRecord=q.as_posix(),generationRecordSha256=SNAP[q.as_posix()],coreCrop=rec['coreCrop'],coreWorldBox=rec.get('coreWorldBox'),references=rec.get('references'),actualModel=rec.get('actualModel'),actualQuality=rec.get('actualQuality'))
    return d

def replay(z,tid,cores,overlays,file):
    ox,oy,_,_=world(tid); srcs=[]; ol=[]; count=0
    out=Image.new('RGB',(4096,4096))
    for r,row in enumerate(cores):
        for c,ident in enumerate(row):
            if not ident: continue
            p=z/'native'/f'{ident}.png'
            exp=[ox+c*1024,oy+r*1024,ox+(c+1)*1024,oy+(r+1)*1024]
            d=native(p,exp); d.update(id=ident,tileLocalPaste=[c*1024,r*1024]);srcs.append(d);count+=1
            with Image.open(p) as im: out.paste(im.crop((115,115,1139,1139)),(c*1024,r*1024))
    for ident in overlays:
        qp=z/'qa'/f'{ident}.overlay.json'; q=read(qp)
        assert q['review'].startswith('passed'),qp
        d=info(q['source']);assert d['sha256']==q['sha256'],qp
        with Image.open(q['source']) as im:out.paste(im.crop(tuple(q['coreCrop'])),tuple(q['tileLocalPaste']))
        ol.append({'id':ident,'record':qp.as_posix(),'recordSha256':SNAP[qp.as_posix()],**q})
    match=None; fi=None
    if count==16:
        fi=info(file); assert fi['dimensions']==[4096,4096],file
        with Image.open(file) as im:match=ImageChops.difference(out,im.convert('RGB')).getbbox() is None
    out.close();gc.collect()
    return count,srcs,ol,fi,match

def save_image(im,p):
    im.save(p)
    return {'file':p.as_posix(),'sha256':sha(p),'dimensions':list(im.size),'resized':False}

def group(name,ids,tiles):
    # Exactly four adjacent tiles, one bounded 8192-square canvas at a time.
    d=OUT/name; d.mkdir(exist_ok=True)
    boxes=[world(t) for t in ids]; x0=min(b[0] for b in boxes); y0=min(b[1] for b in boxes)
    x1=max(b[2] for b in boxes);y1=max(b[3] for b in boxes)
    assert (x1-x0,y1-y0)==(8192,8192)
    im=Image.new('RGB',(8192,8192)); inputs=[]
    for tid in ids:
        t=tiles[tid]; assert t['fullCoverage'] and t['replayMatchesCandidate'],tid
        b=world(tid)
        with Image.open(t['file']) as src:im.paste(src,(b[0]-x0,b[1]-y0))
        inputs.append({'tileId':tid,'file':t['file'],'sha256':t['sha256'],'worldBox':b})
    output=save_image(im,d/'native-hard-join-8192.png')
    preview=im.resize((1536,1536),Image.Resampling.LANCZOS)
    banner=Image.new('RGB',(1536,1576),(35,35,35));banner.paste(preview,(0,40))
    ImageDraw.Draw(banner).text((12,12),'PREVIEW ONLY - downsampled from exact 8192 hard join - '+name,fill='white')
    banner.save(d/'preview-only-1536.png');banner.close();preview.close()
    strips=[]
    for orientation in ['h','v']:
        for side in range(2):
            for segment in range(4):
                start=side*4096+segment*1024
                box=(start,3840,start+1024,4352) if orientation=='h' else (3840,start,4352,start+1024)
                p=d/f'{orientation}-{side+1}-segment-{segment+1}-100pct.png'
                cr=im.crop(box); e=save_image(cr,p);cr.close();e.update(groupLocalBox=list(box),worldBox=[box[0]+x0,box[1]+y0,box[2]+x0,box[3]+y0],status='pending_visual_review');strips.append(e)
    cr=im.crop((3840,3840,4352,4352)); cross=save_image(cr,d/'cross-100pct.png');cr.close();cross['status']='pending_visual_review'
    im.close();gc.collect()
    result={'group':name,'coordinates':ids,'worldBox':[x0,y0,x1,y1],'inputs':inputs,'output':output,'operation':'exact unscaled 4096 pixel paste; no blending, painting, filling or correction','preview':(d/'preview-only-1536.png').as_posix(),'seams':strips,'cross':cross,'formalAccepted':False}
    write(d/'manifest.json',result)
    return result

OUT.mkdir(parents=True,exist_ok=True)
tiles={}; selections=[]
z=BASE/'northeast'; progress=read(z/'progress.json')
for p in sorted(z.glob('selection-*.json')):
    q=read(p); tid=q['tileId']; candidate=Path(q.get('candidatePath',z/'tiles'/f'{tid}.png'))
    count,srcs,ols,fi,match=replay(z,tid,q['cores'],q.get('overlays',[]),candidate)
    t={'tileId':tid,'zone':'northeast','worldBox':world(tid),'coreCount':count,'fullCoverage':count==16,'selectedCores':q['cores'],'sources':srcs,'overlays':ols,'selectionFile':p.as_posix(),'selectionSha256':SNAP[p.as_posix()],'internalReview':q.get('internalReview',progress.get('tileSummary',{}).get(tid,{}).get('internalPassed')),'pendingIssues':q.get('pendingIssues',[]),'replayMatchesCandidate':match,'formalAccepted':False}
    if fi:t.update(fi)
    else:t['missingCoreCoordinates']=[f'p{r+1:02}_{c+1:02}' for r,row in enumerate(q['cores']) for c,ident in enumerate(row) if not ident]
    tiles[tid]=t;selections.append(t)
    print(tid,count,match,flush=True)
a=BASE/'accelerated-northeast-coast';q=read(a/'current-selection-20261012.json')
completion=read(a/'production-completion-20261012.json')
completion_by_id={c['tileId']:c for c in completion['currentCandidates']}
for c in q['candidates']:
    tid=c['tileId'];count,srcs,ols,fi,match=replay(a,tid,c['selectedCores'],[],c['file'])
    assert fi['sha256']==c['sha256'],tid
    cc=completion_by_id[tid]
    t={'tileId':tid,'zone':'accelerated-northeast-coast','worldBox':world(tid),'coreCount':count,'fullCoverage':count==16,'selectedCores':c['selectedCores'],'sources':srcs,'overlays':ols,'selectionFile':(a/'current-selection-20261012.json').as_posix(),'internalReview':'passed_in_current_completion_record','qaReport':cc['qaReport'],'qaReportSha256':track(cc['qaReport']),'pendingIssues':[],'replayMatchesCandidate':match,'formalAccepted':False,**fi}
    assert t['qaReportSha256']==cc['qaReportSha256']
    assert tid not in tiles,'duplicate coordinate'
    tiles[tid]=t;selections.append(t);print(tid,count,match,flush=True)
groups=[]
for name,ids in [
    ('g01-coast-r01-r02-c13-c14',['r01_c13','r01_c14','r02_c13','r02_c14']),
    ('g02-cross-zone-r02-r03-c13-c14',['r02_c13','r02_c14','r03_c13','r03_c14']),
    ('g03-main-r03-r04-c11-c12',['r03_c11','r03_c12','r04_c11','r04_c12']),
    ('g04-main-r04-r05-c13-c14',['r04_c13','r04_c14','r05_c13','r05_c14'])]:
    groups.append(group(name,ids,tiles));print('group',name,flush=True)

# Legacy cross-zone crops are reusable only when current RGB pixels are identical.
legacy=read(z/'qa/cross-zone-20261011/review.json');reuse=[]
g=groups[1]
for i,r in enumerate(legacy['records']):
    for j,e in enumerate(r['evidence']):
        new=g['seams'][i*4+j];old=Path(e['file']);valid=track(old)==e['sha256']
        with Image.open(old) as oi, Image.open(new['file']) as ni:
            identical=oi.size==ni.size and ImageChops.difference(oi.convert('RGB'),ni.convert('RGB')).getbbox() is None
        reuse.append({'pair':r['pair'],'segment':j+1,'oldEvidence':e,'newEvidence':new,'oldEvidenceHashValid':valid,'currentPixelsIdentical':identical,'canReusePassedEvidence':valid and identical and e['status'].startswith('passed')})
write(OUT/'legacy-cross-zone-reuse.json',reuse)
write(OUT/'inventory.json',{'generatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'zones':['northeast','accelerated-northeast-coast'],'tiles':selections,'fullCoverageCount':sum(t['fullCoverage'] for t in selections),'partialCount':sum(not t['fullCoverage'] for t in selections),'selectedCoreCount':sum(t['coreCount'] for t in selections),'groups':[g['group'] for g in groups],'actualImageModel':'unconfirmed for existing images','newImageCalls':0,'formalAcceptedCount':0})
write(OUT/'input-snapshot.json',{'files':[{'file':p,'sha256':s} for p,s in sorted(SNAP.items())]})
print('summary',len(selections),sum(t['fullCoverage'] for t in selections),sum(t['coreCount'] for t in selections),'reused',sum(e['canReusePassedEvidence'] for e in reuse),flush=True)
