from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re
from PIL import Image
import numpy as np

ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production'
PROD=BASE/'island-game-20261009/southeast'
REVIEW=BASE/'parallel-review-20261013/island-game-20261009'
OUT=REVIEW/'resume-v02/southeast'
OUT.mkdir(parents=True,exist_ok=True)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
start=now()
baseline=read(REVIEW/'southeast-audit-v01/inventory.json')
prior={str(Path(x['file'])).lower():x for x in read(REVIEW/'southeast-audit-v01/snapshot-inputs.json')['inputs']}
docs={}; checks=[]
def capture(p):
    p=Path(p); stat=p.stat(); b=p.read_bytes(); after=p.stat(); h=hashlib.sha256(b).hexdigest()
    old=prior.get(str(p).lower())
    c={'file':str(p),'sha256':h,'bytes':len(b),'mtimeNs':stat.st_mtime_ns,'stableDuringRead':stat.st_mtime_ns==after.st_mtime_ns and stat.st_size==after.st_size,'baselineSha256':old.get('sha256') if old else None,'baselineHashMatches':h==old['sha256'] if old else None}
    checks.append(c)
    return b,c
# Capture only live top-level bookkeeping, not historical native archives.
names=set()
for pat in ['progress*.json','selection*.json','selected-native*.json','*native-spec*.json','current-zone-counts*.json']:
    names.update(PROD.glob(pat))
for p in sorted(names):
    b,c=capture(p); docs[p.name]=json.loads(b.decode('utf-8-sig'))
write('metadata-snapshot.json',{'startedAtUtc':start,'capturedAtUtc':now(),'documents':docs,'checks':checks.copy()})
original_checks=[]
for t in baseline['tiles']:
    if t.get('file'):
        b,c=capture(t['file']); c.update(tile=t['tileId'],expectedSha256=t['sha256'],unchanged=c['sha256']==t['sha256']); original_checks.append(c)
write('baseline-candidate-reuse.json',{'checks':original_checks,'allUnchanged':all(x['unchanged'] for x in original_checks),'scope':'15 current baseline candidates only; no history scan; prior 8192 assemblies not rebuilt'})
cut_records=[]
def savecut(im,box,name,source):
    q=OUT/(name+'.png'); q.parent.mkdir(parents=True,exist_ok=True); crop=im.crop(tuple(box)); crop.save(q)
    check=Image.open(q); assert check.size==crop.size and check.tobytes()==crop.tobytes()
    rec={'file':str(q),'sha256':sha(q),'source':source,'sourceBox':list(box),'dimensions':list(crop.size),'pixelExact':True,'visualReview':'pending'}
    cut_records.append(rec); return rec
# r14_c12 now has a selected-source manifest and a complete candidate.
sel=docs['selected-native-r14_c12-sol-20261013-v01.json']
b,c=capture(sel['candidate']); full=Image.open(sel['candidate']); arr=np.array(full)
assert full.size==(4096,4096)
replay=[]
for s in sel['sources']:
    b,sc=capture(s['file']); im=Image.open(s['file']); off=s['tileToNativeOffset']; x=115-off[0]; y=115-off[1]
    core=im.crop((115,115,1139,1139)); mismatch=int(np.any(np.array(core)!=arr[y:y+1024,x:x+1024],axis=2).sum())
    replay.append({**sc,'coordinate':re.search(r'_p(\d{2})_',s['file'])[1],'dimensions':list(im.size),'expectedSha256':s['sha256'],'hashMatchesManifest':sc['sha256']==s['sha256'],'destination':[x,y],'mismatchedPixels':mismatch})
partial=read(PROD/'qa/r14_c12-partial-local-20261013/partial-proof-and-review-queue.json')
known_boxes={tuple(x['sourceCrop']) for k in ['knownInternalSeams','knownJunctions'] for x in partial[k]}
inherit=[]
for k in ['knownInternalSeams','knownJunctions']:
    for rec in partial[k]:
        p=Path(rec['file']); _,sc=capture(p); old=Image.open(p); crop=full.crop(tuple(rec['sourceCrop']))
        inherit.append({'id':rec['id'],'file':str(p),'sha256':sc['sha256'],'hashMatches':sc['sha256']==rec['sha256'],'pixelsMatchCurrent':old.size==crop.size and old.tobytes()==crop.tobytes(),'sourceBox':rec['sourceCrop'],'priorStatus':rec.get('status')})
for r in range(4):
    for cc in range(1,4):
        box=(cc*1024-256,r*1024,cc*1024+256,(r+1)*1024)
        if box not in known_boxes: savecut(full,box,f'r14_c12/new-v-r{r+1}-c{cc}',sel['candidate'])
for rr in range(1,4):
    for cc in range(4):
        box=(cc*1024,rr*1024-256,(cc+1)*1024,rr*1024+256)
        if box not in known_boxes: savecut(full,box,f'r14_c12/new-h-r{rr}-c{cc+1}',sel['candidate'])
for rr in range(1,4):
    for cc in range(1,4):
        box=(cc*1024-256,rr*1024-256,cc*1024+256,rr*1024+256)
        if box not in known_boxes: savecut(full,box,f'r14_c12/new-j-r{rr}-c{cc}',sel['candidate'])
north=Image.open(partial['northCandidate']); capture(partial['northCandidate'])
northChecks=[]
for rec in partial['actualNorthCuts']:
    capture(rec['file'])
    # Existing check's exact crop definitions are preserved for replay trace.
    northChecks.append(rec)
write('r14_c12-source-review.json',{'candidate':sel['candidate'],'candidateSha256':c['sha256'],'candidateHashMatchesManifest':c['sha256']==sel['candidateSha256'],'nativeCoreCount':len(replay),'sourceReplay':replay,'sourcePixelMismatch':sum(x['mismatchedPixels'] for x in replay),'priorChecksReused':inherit,'actualNorthChecksPrior':northChecks,'northCandidateUnchanged':sha(partial['northCandidate'])==partial['northSha256'],'newChecks':[x for x in cut_records if '/r14_c12/' in x['file'].replace('\\','/')],'adoptedInRootProduction':any(x['tile']=='r14_c12' for x in docs['progress.json']['currentAdoptedCandidates']),'formalAccepted':False})
# r13_c11 only newly selected bottom-left two cores; no complete image invented.
pv=docs['selection-r13_c11.json']['patchVersions']; new_13=[]
for key in ['31','32','41','42']:
    p=PROD/'native'/f'r13_c11_p{key}_{pv[key]}.png'; _,sc=capture(p); new_13.append({**sc,'coordinate':key})
band=Image.new('RGB',(2048,2048))
for key in ['31','32','41','42']:
    im=Image.open(PROD/'native'/f'r13_c11_p{key}_{pv[key]}.png')
    band.paste(im.crop((115,115,1139,1139)),((int(key[1])-1)*1024,(int(key[0])-3)*1024))
for box,name in [((0,768,1024,1280),'p31-p41'),((1024,768,2048,1280),'p32-p42'),((768,1024,1280,2048),'p41-p42'),((768,768,1280,1280),'j31-32-41-42')]:
    rec=savecut(band,box,'r13_c11/'+name,'exact-pasted-4-core-local-band'); rec['tileLocalBox']=[box[0],box[1]+2048,box[2],box[3]+2048]; rec['sources']=new_13
write('r13_c11-selection-review.json',{'selectedCoreCount':len(pv),'versions':pv,'newSelectedSinceBaseline':['41','42'],'newCoreCountSincePreviousDelta':0,'missingCoordinates':[f'{r}{c}' for r in range(1,5) for c in range(1,5) if f'{r}{c}' not in pv],'checkedSources':new_13,'completeCandidate':False,'formalAccepted':False,'inFlightRecord':docs['progress-r13_c11.json'].get('inFlightRequests',[])})
# Existing r12_c13 v02 remains current; v03 is an unadopted local ownership proposal.
v2=Path(docs['progress-r12_c13.json']['candidate']); v3=PROD/'tiles/r12_c13.candidate-sol-20261013-v03-local-ownership.png'; cap3,sc3=capture(v3); meta3=read(str(v3)+'.generation.json'); capture(str(v3)+'.generation.json')
im2=Image.open(v2); im3=Image.open(v3)
for box,name in [((768,1911,1280,2423),'floor-issue'),((2816,3474,3328,3986),'sail-issue'),((397,1421,1651,2675),'whole-floor-proposal')]:
    savecut(im3,box,'r12_c13/v03-'+name,str(v3))
    if name!='whole-floor-proposal': savecut(im2,box,'r12_c13/v02-'+name,str(v2))
diff=np.any(np.array(im2)!=np.array(im3),axis=2); yy,xx=np.where(diff)
write('r12_c13-proposal-delta.json',{'currentCandidate':str(v2),'currentCandidateSha256':sha(v2),'currentSourceUnchanged':sha(v2)==docs['progress-r12_c13.json']['candidateSha256'],'unadoptedProposal':str(v3),'proposalSha256':sc3['sha256'],'proposalHashMatchesMetadata':sc3['sha256']==meta3['sha256'],'proposalStatus':meta3['status'],'proposalChangedPixels':int(diff.sum()),'changedPixelBox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'v03NotPromotedToCurrent':True,'formalAccepted':False})
write('crop-manifest.json',{'cuts':cut_records,'mechanicalOperation':'exact integer crop/paste; no scaling, filtering, blending, drawing or AI','allPixelExact':all(x['pixelExact'] for x in cut_records)})
write('source-checks.json',{'snapshotStartedAtUtc':start,'snapshotCompletedAtUtc':now(),'checks':checks,'allStableDuringRead':all(x['stableDuringRead'] for x in checks),'archiveRescanned':False})
print(json.dumps({'startedAtUtc':start,'finishedAtUtc':now(),'baselineCandidatesUnchanged':all(x['unchanged'] for x in original_checks),'r14CoreCount':len(replay),'r14PixelMismatch':sum(x['mismatchedPixels'] for x in replay),'priorR14ChecksMatching':sum(x['pixelsMatchCurrent'] and x['hashMatches'] for x in inherit),'newCrops':len(cut_records),'crops':[x['file'] for x in cut_records]},ensure_ascii=False))
