"""Publish the independently inspected local repair without tile acceptance."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,os,uuid
from PIL import Image
T=Path(__file__).resolve().parent;D=T/'repairs'/'single-stone-railing-bottom-20261012-v3';B=T/'repairs'/'single-stone-railing-20261012-v2';Q=T/'review'/'single-railing-v3-20261012-root'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def file(p):return {'path':str(p),'sha256':sha(p)}
def art(p):
    d=file(p)
    with Image.open(p) as im:d['pixels']=list(im.size)
    return d
def atomic(p,d):
    tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,p)
def exclusive(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
base=read(B/'composition.json');m=read(D/'composition.json')
assert m['candidate']['sha256']=='3f0ba6b330136574a1ea9508d2a213fc9b66a5a42c95c737ee0820a6cb0798a9'
for chain,folder in [(base,B),(m,D)]:
    for key in ['sourceCandidate','sourceContext','sourceAssembly','native','generationRecord','preparation','request','prompt','receipt','alpha','seamPaths','compositor','algorithm','candidate','context']:assert sha(chain[key]['path'])==chain[key]['sha256']
    replay=read(folder/'replay-verification.json');assert replay['candidateExactReplay'] and replay['outsideRepairBoxUnchanged'] and replay['contextCoreExactMatch']
Q.mkdir(parents=True,exist_ok=True)
with Image.open(m['candidate']['path']) as im:
    for sx,sy in [(1024,2048),(1024,3072)]:
        p=Q/f'junction-x{sx}-y{sy}-100pct.png'
        if not p.exists():
            with p.open('xb') as f:im.crop((sx-450,sy-450,sx+450,sy+450)).save(f,format='PNG')
    preview=Q/'overview-preview-only.png'
    if not preview.exists():
        with preview.open('xb') as f:im.resize((1024,1024),Image.Resampling.LANCZOS).save(f,format='PNG')
report=Q/'local-root-review.json'
if not report.exists():exclusive(report,{'schemaVersion':1,'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','candidate':m['candidate'],'reviewedNativeImages':[dict(art(B/n),resized=False) for n in ['composed-local-1254.png','top-boundary-100pct.png','left-boundary-100pct.png','right-boundary-100pct.png']]+[dict(art(D/n),resized=False) for n in ['composed-local-1254.png','top-boundary-100pct.png','bottom-boundary-100pct.png','left-boundary-100pct.png','right-boundary-100pct.png']],'observations':['Duplicate front railing and restarted lower post removed; original single back railing retained.','Second true native repair closes clipped foliage at the first repair lower join.','No hard geometry step or doubled outline observed in these inspected local perimeter crops.'],'result':'local_improvement_pass_pending_full_tile_and_neighbor_QA','formalAccepted':False,'fullInternalArtQA':'pending_independent_report','externalNeighborSeamQA':'pending','scope':'Only the exact two local repair placements. Original 16 active natives and all other candidate pixels preserved outside those placements.'})
candidate=T/'candidate'/'r14_c15-4k-single-railing-v3-20261012.png';context=T/'candidate'/'r14_c15-context-4326-single-railing-v3-20261012.png'
for src,dst in [(m['candidate']['path'],candidate),(m['context']['path'],context)]:
    if not dst.exists():shutil.copyfile(src,dst)
    assert sha(src)==sha(dst)
manifest=T/'candidate'/'r14_c15-single-railing-v3-20261012-manifest.json'
if not manifest.exists():exclusive(manifest,{'schemaVersion':1,'tile':T.name,'selectedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'local_single_railing_repairs_published_pending_full_QA','baseAssembly':base['sourceAssembly'],'repairChain':[file(B/'composition.json'),file(D/'composition.json')],'replayChecks':[file(B/'replay-verification.json'),file(D/'replay-verification.json')],'candidate':art(candidate),'context':art(context),'nativeSources':[base['native'],m['native']],'rootLocalQA':file(report),'activeNativeCount':16,'actualNativeOutputCount':18,'sourceResampling':False,'RGBColorCorrection':False,'formalAccepted':False})
status='local_single_railing_repairs_published_pending_full_QA'
latest={'schemaVersion':2,'tile':T.name,'status':status,'manifest':file(manifest),'candidate':art(candidate),'context':art(context),'rootLocalQA':file(report),'internalArtQA':'pending_independent_full_tile_review','externalNeighborSeamQA':'pending','formalAccepted':False}
atomic(T/'candidate'/'latest-assembly.json',latest)
p=read(T/'progress.json');p.update(status=status,updatedAt=datetime.now(timezone.utc).isoformat(),candidate=str(candidate),context=str(context),assemblyManifest=str(manifest),rootLocalQA=file(report),currentPatch=None,currentVersion='single-railing-v3-20261012',activeNativeCount=16,activeRepairNativeCount=2,nativeActualOutputCount=18,complete4kCandidateCount=1,internalArtQA='pending_independent_full_tile_review',externalNeighborSeamQA='pending',formalAccepted=False,nextStep='Complete independent full tile QA and current-core north/west neighbor joins; continue remaining native tiles.')
atomic(T/'progress.json',p)
print(json.dumps({'candidate':art(candidate),'manifest':file(manifest),'rootLocalQA':file(report),'junctions':[str(p) for p in Q.glob('junction*png')]}))
