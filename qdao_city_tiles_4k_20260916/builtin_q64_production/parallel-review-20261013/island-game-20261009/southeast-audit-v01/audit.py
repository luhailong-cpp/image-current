from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import json, hashlib, re, gc
from PIL import Image, ImageChops
import numpy as np

ROOT = Path('D:/work/image')
BASE = ROOT / 'qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southeast'
OUT = ROOT / 'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/southeast-audit-v01'
OUT.mkdir(parents=True, exist_ok=True)
SNAP = {}

def now(): return datetime.now(timezone.utc).isoformat()
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024), b''): h.update(b)
    return h.hexdigest()
def allowed(p):
    p=Path(p).resolve()
    return p.is_relative_to(BASE) or p in [ROOT/'AGENTS.md', BASE.parent/'production-contract.json']
def snap(p):
    p=Path(p).resolve()
    if not allowed(p): raise RuntimeError('outside allowed read scope: '+str(p))
    k=str(p)
    if k not in SNAP:
        s=p.stat(); SNAP[k]={'file':k,'sha256':digest(p),'bytes':s.st_size,'mtimeNs':s.st_mtime_ns}
    return SNAP[k]
def read(p):
    snap(p)
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,o): (OUT/n).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def image_info(p):
    a=snap(p)
    with Image.open(p) as im: return {**a,'dimensions':list(im.size),'mode':im.mode}
def rc(t): return tuple(map(int,re.match(r'r(\d+)_c(\d+)',t).groups()))
def core_box(p):
    m=re.search(r'_p([1-4])([1-4])_',Path(p).name)
    if not m:return None
    r,c=map(int,m.groups());return [(c-1)*1024,(r-1)*1024,(c)*1024,(r)*1024]
def iter_dicts(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from iter_dicts(v)
    elif isinstance(x,list):
        for v in x:yield from iter_dicts(v)

started=now()
progress=read(BASE/'progress.json')
contract=read(BASE.parent/'production-contract.json')
snap(ROOT/'AGENTS.md')
references=read(BASE/'references.json')
cache=OUT/'native-archive-audit.json'
native=json.loads(cache.read_text(encoding='utf-8'))['entries'] if cache.exists() else []
if native:
    for n in native:
        SNAP[n['file']]={k:n[k] for k in ['file','sha256','bytes','mtimeNs']}
for p in ([] if native else sorted((BASE/'native').glob('*.png'))):
    inf=image_info(p)
    mp=Path(str(p)+'.generation.json')
    m=read(mp) if mp.exists() else {}
    nm=re.match(r'(r\d+_c\d+)_p([1-4][1-4])_(v\d+)',p.stem)
    rr=[]
    for ref in m.get('references',[]):
        rp=Path(ref.get('file',''))
        rr.append({'file':str(rp),'sha256':ref.get('sha256'),'role':ref.get('role'),
            'verification':'metadata_only_external_reference' if not allowed(rp) else ('verified' if rp.exists() and snap(rp)['sha256']==ref.get('sha256') else 'missing_or_mismatch')})
    prompt=m.get('prompt')
    prompt_check=None
    if prompt and isinstance(prompt,str) and Path(prompt).exists() and allowed(Path(prompt)):
        prompt_check=snap(Path(prompt))['sha256']==m.get('promptSha256')
    native.append({**inf,'tileId':nm[1] if nm else None,'coordinate':nm[2] if nm else None,'version':nm[3] if nm else None,
        'metadata':str(mp) if mp.exists() else None,'metadataSha256Matches':inf['sha256']==m.get('sha256'),
        'nativeDimensionsMatchMetadata':inf['dimensions']==[m.get('width'),m.get('height')],
        'resizedAfterGeneration':m.get('resizedAfterGeneration'),
        'actualModel':m.get('actualModel'),'actualQuality':m.get('actualQuality'),
        'submittedParameters':m.get('submittedParameters'),'promptSha256Matches':prompt_check,'references':rr})
save('native-archive-audit.json',{'createdAtUtc':now(),'entries':native,'count':len(native),
    'unexpectedDimensions':[n['file'] for n in native if n['dimensions']!=[1254,1254]],
    'metadataMismatch':[n['file'] for n in native if not n['metadataSha256Matches']],
    'note':'Historical archive, including rejected versions. Never equate archive count with selected coverage. Actual models remain unconfirmed.'})
native_by_file={n['file'].lower():n for n in native}
print('native archive audited',len(native),flush=True)

reviews={
'r08_c11':['qa/r08_c11-v01-sol/root-internal-acceptance-20261013.json','qa/r08_c11-v01-sol/native-visual-review-sol-20261012.json','qa/r08_c11-v01-sol/root-independent-source-replay-20261013.json'],
'r08_c12':['qa/r08_c12.resume-review-final.json','qa/r08_c12.v15-final-review-evidence.json','qa/r08_c12.replay-v15.json'],
'r09_c11':['qa/r09_c11-v05/root-review.json','qa/r09_c11-v05/prior-reviewed-pixel-replay.json'],
'r09_c12':['qa/r09_c12-v09/root-review.json','qa/r09_c12-v09/prior-reviewed-pixel-replay.json'],
'r09_c13':['qa/r09_c13-v02/independent-review.json','qa/r09_c13.root-review-v02.json'],
'r10_c11':['qa/r10_c11-independent-v04/root-independent-review.json','qa/r10_c11-independent-v04/repair-review.json'],
'r10_c12':['qa/r10_c12.root-review-v02.json','qa/center-r10c12-external-20261011/manifest.json'],
'r10_c13':['qa/r10_c13-v02/visual-review.json'],
'r11_c11':['qa/r11_c11-v02/root-independent-review.json','qa/r11_c11-v02/visual-review.json'],
'r11_c12':['qa/r11_c12-v02/repair-review.json','qa/r11_c12-independent-review-v02.json'],
'r11_c13':['qa/r11_c13-v02/visual-review.json'],
'r12_c11':['qa/r12_c11-sol-20261012-upper-v03/root-changed-region-review.json','qa/r12_c11-sol-20261012-upper-v03/source-pixel-proof.json'],
'r12_c12':['qa/r12_c12-sol-20261012-v01/root-visual-review.json','root-candidate-independent-review.json'],
'r12_c13':['qa/r12_c13-resume-sol-20261012/candidate-v02-seam-review.json','qa/r12_c13-resume-sol-20261012/root-qa-identity-audit.json'],
'r13_c12':['qa/r13_c12-sol-20261013-v01/root-visual-review.json','qa/r13_c12-sol-20261013-v01/actual-north.json'],
}

def evidence(p,candidate_sha):
    if not p.exists(): return {'file':str(p),'exists':False}
    d=read(p);e={**snap(p),'exists':True,'status':d.get('status'),
        'candidateHashMatches':candidate_sha in [d.get(k) for k in ['candidateSha256','sha256','candidateHash']],
        'reviewedAtUtc':d.get('reviewedAtUtc',d.get('reviewedAt',d.get('updatedAtUtc')))}
    checks=[]
    for z in iter_dicts(d):
        if isinstance(z.get('file'),str) and isinstance(z.get('sha256'),str):
            fp=Path(z['file'])
            if allowed(fp) and fp.exists(): checks.append({'file':str(fp),'hashMatches':snap(fp)['sha256']==z['sha256']})
    e['listedEvidenceHashChecks']=checks
    e['allListedEvidenceHashesMatch']=all(z['hashMatches'] for z in checks)
    return e

def replay(p,meta):
    sources=meta.get('sources',[])
    map_name=next((meta[k] for k in ['sourceID','sourceIdMap'] if isinstance(meta.get(k),str)),None)
    if map_name and sources and all('id' in s for s in sources):
        mp=Path(map_name);snap(mp)
        with Image.open(mp) as im: ids=np.array(im)
        with Image.open(p) as im: actual=np.array(im.convert('RGB'))
        mismatch=0;owned=0;entries=[]
        for s in sources:
            mask=ids==s['id'];ys,xs=np.nonzero(mask);n=len(xs);owned+=n
            if not n:continue
            fp=Path(s['file']);inf=image_info(fp)
            off=s.get('tileToNativeOffset')
            if off is None:off=[-v for v in s['originInTile']]
            with Image.open(fp) as im: a=np.array(im.convert('RGB'))
            xx=xs+off[0];yy=ys+off[1]
            if min(xx)<0 or min(yy)<0 or max(xx)>=a.shape[1] or max(yy)>=a.shape[0]:raise RuntimeError('source bounds')
            mm=int(np.count_nonzero(np.any(actual[ys,xs]!=a[yy,xx],axis=1)));mismatch+=mm
            entries.append({'file':str(fp),'sha256':inf['sha256'],'sha256MatchesManifest':inf['sha256']==s['sha256'],'dimensions':inf['dimensions'],'id':s['id'],'ownedPixels':n,'mismatchedPixels':mm,'tileToNativeOffset':off})
            del a,mask,ys,xs
        del ids,actual
        return {'method':'current_source_id_pixel_replay','coveredPixels':owned,'uncoveredPixels':4096*4096-owned,'mismatchedPixels':mismatch,'sources':entries,'fullCoverage':owned==4096*4096 and mismatch==0}
    keys=[k for k in ['contributions','derivedFrom','entries','sources'] if isinstance(meta.get(k),list)]
    seq=meta[keys[0]] if keys else []
    seq=list(seq)+list(meta.get('repairOverlays',[]))+list(meta.get('overlays',[]))
    if not seq:return {'method':'unavailable','fullCoverage':False}
    canvas=Image.new('RGB',(4096,4096));covered=Image.new('1',(4096,4096));entries=[]
    for s in seq:
        if 'sourceCrop' not in s:continue
        fp=Path(s['file']);inf=image_info(fp)
        box=s['sourceCrop'];dest=tuple(s.get('destination',s.get('destinationBox',[0,0])[:2])[:2])
        with Image.open(fp) as im: tile=im.convert('RGB').crop(box)
        if tile.width!=box[2]-box[0] or tile.height!=box[3]-box[1]:raise RuntimeError('resize forbidden')
        canvas.paste(tile,dest);covered.paste(1,tuple(dest)+tuple([dest[0]+tile.width,dest[1]+tile.height]))
        entries.append({'file':str(fp),'sha256':inf['sha256'],'sha256MatchesManifest':inf['sha256']==s['sha256'],'dimensions':inf['dimensions'],'sourceCrop':box,'destination':dest})
    with Image.open(p) as im:
        mm=int(np.count_nonzero(np.any(np.array(canvas)!=np.array(im.convert('RGB')),axis=2)))
    count=int(np.count_nonzero(np.array(covered)));del canvas,covered
    return {'method':'current_rectangular_operations_pixel_replay','coveredPixels':count,'uncoveredPixels':4096*4096-count,'mismatchedPixels':mm,'sources':entries,'fullCoverage':count==4096*4096 and mm==0}

adopted={x['tile']:x for x in progress['currentAdoptedCandidates']}
pending={x['tile']:x for x in progress.get('pendingCandidates',[])}
full={**adopted,**pending}
tiles=[]
for r in range(8,15):
  for c in range(8,15):
    t=f'r{r:02d}_c{c:02d}'
    z={'tileId':t,'row':r,'column':c,'globalBox':[(c-1)*4096,(r-1)*4096,c*4096,r*4096],
       'fullCoverage':False,'coreCount':0,'file':None,'sha256':None,'dimensions':None,'adopted':False,'internalPassed':False,'externalPassed':False,'formalAccepted':False}
    if t in full:
        a=full[t];p=Path(a['candidate']);inf=image_info(p)
        mp=next((q for q in [Path(str(p)+'.generation.json'),Path(str(p)+'.sources.json')] if q.exists()),None)
        if t=='r08_c11':mp=BASE/'qa/r08_c11-v01-sol/source-audit.json'
        m=read(mp);rep=replay(p,m)
        ev=[evidence(BASE/e,inf['sha256']) for e in reviews.get(t,[])]
        z.update({'file':str(p),'sha256':inf['sha256'],'manifestSha256Matches':inf['sha256']==a.get('sha256'),
            'dimensions':inf['dimensions'],'fullCoverage':rep['fullCoverage'],'coreCount':16 if rep['fullCoverage'] else None,
            'adopted':t in adopted,'internalPassed':bool(a.get('internalPassed')),'externalPassed':bool(a.get('externalPassed')),
            'pending':a.get('pending',a.get('status')),'assemblyMetadata':str(mp),'sourceReplay':rep,'internalEvidence':ev})
        save(t+'-audit.json',z)
        print(t,rep['method'],'mismatch',rep.get('mismatchedPixels'),flush=True)
    else:
        pp=BASE/f'progress-{t}.json'
        if pp.exists():
            pd=read(pp);vers=pd.get('selectedVersions',pd.get('workingVersions',{}))
            if t=='r13_c11':vers=read(BASE/'selection-r13_c11.json')['patchVersions']
            selected=[]
            for coord,version in sorted(vers.items()):
                npth=BASE/'native'/f'{t}_p{coord}_{version}.png'
                if npth.exists():selected.append({**image_info(npth),'coordinate':coord,'coreLocalBox':core_box(npth),'sourceCrop':[115,115,1139,1139]})
            z['coreCount']=len(selected);z['selectedNativeCores']=selected
            z['missingCoreCoordinates']=[f'{a}{b}' for a in range(1,5) for b in range(1,5) if f'{a}{b}' not in [s['coordinate'] for s in selected]]
            z['partialEvidence']=[]
            if t=='r14_c12':z['partialEvidence']=[evidence(BASE/'qa/r14_c12-partial-local-20261013/partial-proof-and-review-queue.json','')]
            if t=='r13_c13':z['savedRejectedOrUnselectedCoordinates']=['13']
    tiles.append(z);gc.collect()

bytile={z['tileId']:z for z in tiles}
for t,z in bytile.items():
    r,c=rc(t);neighbors=[]
    for direction,dr,dc in [('north',-1,0),('east',0,1),('south',1,0),('west',0,-1)]:
        nr,nc=r+dr,c+dc
        if 1<=nr<=14 and 1<=nc<=14:
            nt=f'r{nr:02d}_c{nc:02d}';n=bytile.get(nt)
            neighbors.append({'direction':direction,'tileId':nt,'status':'outside_read_scope_root_review' if not n else ('available_full_candidate' if n['fullCoverage'] else ('partial_native' if n['coreCount'] else 'missing_native'))})
        else:neighbors.append({'direction':direction,'tileId':None,'status':'outer_map_boundary'})
    z['neighbors']=neighbors

inventory={'schemaVersion':1,'zone':'southeast','createdAtUtc':now(),'snapshotStartedAtUtc':started,
  'readScope':[str(BASE),str(BASE.parent/'production-contract.json'),str(ROOT/'AGENTS.md')],
  'outputRoot':str(OUT),'actualModel':'unconfirmed_historical_assets','newGenerationPerformed':False,
  'contract':{'rows':[8,14],'columns':[8,14],'tileDimensions':[4096,4096],'coreDimensions':[1024,1024],'haloPixels':115,'target4kCount':49},
  'counts':{'fullCoverage':sum(z['fullCoverage'] for z in tiles),'adoptedFullCoverage':sum(z['fullCoverage'] and z['adopted'] for z in tiles),
    'internalPassedAsRecorded':sum(z['internalPassed'] for z in tiles),'formalAccepted':0,
    'partialTiles':sum(0<z['coreCount']<16 for z in tiles),'selectedPartialCores':sum(z['coreCount'] for z in tiles if 0<z['coreCount']<16),
    'missingFullTiles':sum(not z['fullCoverage'] for z in tiles),'emptyTiles':sum(z['coreCount']==0 for z in tiles)},
  'tiles':tiles,'missingFullTiles':[z['tileId'] for z in tiles if not z['fullCoverage']],
  'countDiscrepancies':['progress.remainingAssigned4kCount=37 and historical coveredTiles/latestCandidates lists are stale relative to current 15 full candidate files. Current adopted list has 14 internally passed candidates plus one full pending candidate.'],
  'sourceStateMayChange':True,'finalMapComplete':False}
save('inventory.json',inventory)
save('snapshot-inputs.json',{'createdAtUtc':now(),'inputs':list(SNAP.values()),'count':len(SNAP)})
print('inventory',inventory['counts'],flush=True)
