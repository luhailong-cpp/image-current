from pathlib import Path
import json, hashlib, datetime, re, gc
from collections import Counter
from PIL import Image
import numpy as np

ROOT = Path('D:/work/image')
BASE = ROOT / 'qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southwest'
OUT = ROOT / 'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/southwest-audit-v01'
OUT.mkdir(parents=True, exist_ok=True)
(OUT/'snapshots').mkdir(exist_ok=True)
TRACKED = {}

def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def track(p, image=False):
    p=Path(p); k=p.as_posix()
    if k in TRACKED: return TRACKED[k].copy()
    d={'path':k, 'exists':p.is_file()}
    if p.is_file():
        st=p.stat(); d.update(sha256=sha(p), bytes=st.st_size, mtimeNs=st.st_mtime_ns)
        if image:
            with Image.open(p) as im: d.update(dimensions=list(im.size),mode=im.mode)
    TRACKED[k]=d
    return d.copy()
def load(p):
    track(p)
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(name,v):
    (OUT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def snap(p):
    p=Path(p); raw=p.read_bytes(); q=OUT/'snapshots'/p.name
    q.write_bytes(raw); track(p)
    return json.loads(raw.decode('utf-8-sig'))

START=stamp()
N=snap(BASE/'current-native-map.json')
P=snap(BASE/'progress.json')
C=snap(BASE.parent/'production-contract.json')
PLAN=load(BASE/'coordinate-plan.json')
dump('snapshot-control.json',{'startedAtUtc':START,'currentNativeMap':track(BASE/'current-native-map.json'),'progress':track(BASE/'progress.json'),'contract':track(BASE.parent/'production-contract.json')})
art=N['candidateArtifacts']
known_reviews={
 'r09_c03':['connected-stepfoot-group-v01-root-review.json'],
 'r09_c04':['connected-stepfoot-group-v01-root-review.json'],
 'r10_c03':['connected-stepfoot-group-v01-root-review.json'],
 'r10_c04':['central-r11c04-resume-final-west-review.json','central-r11c04-pond-right-crisp-v02-west-supplement.json'],
 'r08_c03':['north-r08c03-resume-v01-native-review.json'],
}
issues=[]
def review_items(t,a):
    paths={}
    for k in ('review','pairedNorthReview'):
        if a.get(k): paths[str(Path(a[k]))]=Path(a[k])
    for v in known_reviews.get(t,[]): paths[str(BASE/'qa'/v)]=BASE/'qa'/v
    result=[]
    for path in paths.values():
        if not path.is_file():
            result.append({'file':track(path),'validity':'missing'});continue
        d=load(path); result.append({'file':track(path),'record':d,'validity':'reused_historical_evidence; candidate hash/path compared where recorded'})
        for key in ('findings','issues','remainingInternalIssues','remainingBoundaryIssues'):
            for item in d.get(key,[]):
                issues.append({'tileId':t,'sourceReview':path.as_posix(),'category':key,**item})
    return result

def validate(t,a,rep):
    fp=Path(a['path']); mp=a['sourceIdMask']; mp=Path(mp['path'] if isinstance(mp,dict) else mp)
    im=np.asarray(Image.open(fp).convert('RGB'))
    mask=np.asarray(Image.open(mp))
    if mask.ndim!=2: raise ValueError('Unexpected source-ID mask encoding')
    x0,y0=tile_origin(t); mism=0; valid_count=0; input_info=[]; covered=set()
    for inp in rep.get('inputs',[]):
        sid=inp.get('sourceId')
        if sid is None: continue
        source=track(inp['path'],True); source['record']=track(inp['record']) if inp.get('record') else None
        source['expectedSha256']=inp.get('sha256');source['hashMatchesReport']=not inp.get('sha256') or source.get('sha256')==inp['sha256']
        source['sourceId']=sid;source['nativeGlobalBox']=inp.get('nativeGlobalBox');source['recordHashMatchesReport']=not inp.get('recordSha256') or source['record'].get('sha256')==inp['recordSha256']
        box=inp.get('nativeGlobalBox')
        if not box: input_info.append(source);continue
        sx,sy,ex,ey=box; ax=max(sx,x0);ay=max(sy,y0);bx=min(ex,x0+4096);by=min(ey,y0+4096)
        if ax>=bx or ay>=by: input_info.append(source);continue
        selected=(mask[ay-y0:by-y0,ax-x0:bx-x0]==sid)
        cnt=int(selected.sum());source['selectedPixelCount']=cnt
        if cnt:
            native=np.asarray(Image.open(inp['path']).convert('RGB'))
            aa=im[ay-y0:by-y0,ax-x0:bx-x0]
            bb=native[ay-sy:by-sy,ax-sx:bx-sx]
            bad=int(np.count_nonzero(selected & np.any(aa!=bb,axis=2)))
            source['mismatchedSelectedPixels']=bad;mism+=bad;valid_count+=cnt;covered.add(sid)
        input_info.append(source)
    total=4096*4096
    result={'checkedAtUtc':stamp(),'pixelCount':total,'verifiedSelectedPixelCount':valid_count,'mismatchedPixels':mism,'unverifiedPixels':total-valid_count,'sameGlobalCoordinateExact':mism==0 and valid_count==total,'sources':input_info,'sourceIdMask':track(mp,True)}
    del im,mask;gc.collect()
    return result
def tile_origin(t):
    r,c=map(int,re.match(r'r(\d+)_c(\d+)',t).groups());return ((c-1)*4096,(r-1)*4096)

tiles=[];conflicts=[];record_refs=Counter();model=Counter();selected_native=[]
for r in range(8,15):
 for c in range(1,8):
    t=f'r{r:02}_c{c:02}'; matrix=N.get(t,[[None]*4 for _ in range(4)]); cores=[];missing=[]
    for sr in range(1,5):
     for sc in range(1,5):
        stem=matrix[sr-1][sc-1];x,y=tile_origin(t);gx=x+(sc-1)*1024;gy=y+(sr-1)*1024
        d={'subrow':sr,'subcolumn':sc,'coreGlobalBox':[gx,gy,gx+1024,gy+1024]}
        if not stem: missing.append(d);continue
        fp=BASE/'native'/(stem+'.png');rp=Path(str(fp)+'.generation.json');f=track(fp,True)
        d.update(stem=stem,file=f['path'],sha256=f.get('sha256'),dimensions=f.get('dimensions'),record=track(rp))
        if rp.exists():
            gr=load(rp);d['recordShaMatchesImage']=gr.get('sha256')==f.get('sha256'); d['coordinates']=gr.get('coordinates');d['actualModel']=gr.get('actualModel');d['recordStatus']=gr.get('status')
            model[str(gr.get('actualModel'))]+=1
            refs=[]
            for ref in gr.get('references',[]):
                role=ref.get('role','');rh=ref.get('sha256');record_refs[(role,rh)]+=1;refs.append({'path':ref.get('path'),'role':role,'recordedSha256':rh,'actualReferenceFileRehashed':False})
            d['recordedReferences']=refs
        d['native1254Verified']=f.get('dimensions')==[1254,1254]
        cores.append(d);selected_native.append(d)
    a=art.get(t);entry={'tileId':t,'origin':list(tile_origin(t)),'coreCount':len(cores),'fullCoverage':False,'selectedCores':cores,'missingCores':missing,'file':None,'sha256':None,'dimensions':None,'formalAccepted':False}
    if a:
        f=track(a['path'],True);rep=load(a['sourceReport']);v=validate(t,a,rep)
        exp=a.get('sha256') or next((x.get('sha256') for x in rep.get('outputs',[]) if x.get('sha256')==f.get('sha256')),None)
        entry.update(file=f['path'],sha256=f.get('sha256'),dimensions=f.get('dimensions'),candidateExists=f['exists'],candidateHashMatchesRecord=not exp or exp==f.get('sha256'),sourceReport=track(a['sourceReport']),nativePixelValidation=v,fullCoverage=len(cores)==16 and v['sameGlobalCoordinateExact'],internalPassedRecorded=a.get('internalPassed',a.get('internalTileSeamsPassed',False)),internalStatusRecorded=a.get('internalStatus',a.get('status')),sharedEdgesRecorded=a.get('sharedEdges',{}),internalEvidence=review_items(t,a),allOuterTileEdgesPassed=False)
        old=P.get('currentCandidateByTile',{}).get(t,{}).get('path')
        if old and Path(old)!=Path(a['path']): conflicts.append({'tileId':t,'field':'progress.currentCandidateByTile.path','historical':old,'selected':a['path']})
    else: entry.update(internalPassedRecorded=False,internalEvidence=[])
    tiles.append(entry)
    print(t,len(cores),entry['fullCoverage'],entry.get('nativePixelValidation',{}).get('mismatchedPixels'),flush=True)

full={t['tileId']:t for t in tiles if t['fullCoverage']}
edges=[]
for t in tiles:
 if not t['fullCoverage']: continue
 r,c=map(int,re.match(r'r(\d+)_c(\d+)',t['tileId']).groups())
 for side,dr,dc in [('north',-1,0),('east',0,1),('south',1,0),('west',0,-1)]:
    nr,nc=r+dr,c+dc;neighbor=f'r{nr:02}_c{nc:02}'
    if side in ('north','west') and neighbor in full:continue
    localNeighbor=8<=nr<=14 and 1<=nc<=7
    edges.append({'tileId':t['tileId'],'side':side,'neighbor':neighbor,'neighborFullCandidateAvailable':neighbor in full,'crossZone':not localNeighbor and 1<=nr<=14 and 1<=nc<=14,'status':'pending_current_pair_review' if neighbor in full else ('cross_zone_root_review' if not localNeighbor else 'neighbor_native_coverage_missing')})

inventory={'schemaVersion':1,'map':'eight-immortals-island','zone':'southwest','startedAtUtc':START,'builtAtUtc':stamp(),'scope':'independent read-only audit; no generation/AI edit; no production writes; no Git operations','selectionAuthority':'snapshots/current-native-map.json candidateArtifacts; agrees with progress.currentAdopted4kFiles; currentCandidateByTile may be historical','tiles':tiles,'edges':edges,'recordedOpenIssues':issues,'metadataConflicts':conflicts,'sourceReferenceAudit':{'actualModelCounts':dict(model),'actualModelVerified':False,'recordedReferenceRoleHashCounts':[{'role':k[0],'recordedSha256':k[1],'count':v} for k,v in record_refs.items()],'referenceHashesReportedFromGenerationRecordsOnly':True},'summary':{'targetTiles':49,'complete4kCandidates':len(full),'fullSelectedCoreTiles':sum(t['coreCount']==16 for t in tiles),'selectedCoreCount':sum(t['coreCount'] for t in tiles),'missingCoreCount':784-sum(t['coreCount'] for t in tiles),'partialTiles':[{'tileId':t['tileId'],'coreCount':t['coreCount']} for t in tiles if 0<t['coreCount']<16],'internallyPassedRecorded':sum(t.get('internalPassedRecorded',False) for t in tiles),'formalAcceptedCount':0},'snapshotInputFiles':list(TRACKED.values()),'sourceChangeAudit':{'status':'pending_final_rehash'}}
dump('inventory.json',inventory)
print('SUMMARY',json.dumps(inventory['summary'],ensure_ascii=False),flush=True)
