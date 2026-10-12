import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
B=Path(__file__).resolve().parents[1];Z=B.parent
sys.path.insert(0,str(Z))
import production_v2 as p
def sha(x):return hashlib.sha256(Path(x).read_bytes()).hexdigest()
def read(x):return json.loads(Path(x).read_text(encoding='utf-8-sig'))
def save(x,v):Path(x).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(x):return {'file':str(x),'sha256':sha(x)}
now=datetime.now(timezone.utc).isoformat()
oldn='r05_c06-candidate-minimum-error-b710fa388f5b'
newn='r05_c06-candidate-minimum-error-03d4dd9f7332'
old=read(B/'candidate'/f'{oldn}.assembly.json');new=read(B/'candidate'/f'{newn}.assembly.json')
oldq={Path(e['file']).name:e for e in old['qa']};newq={Path(e['file']).name:e for e in new['qa']}
observations={
'internal-x1024-segment02.png':'Slight fine-grain transition; structural lines continue.',
'internal-x3072-segment02.png':'Fine repeating grain differs slightly between stone regions; no geometric break.',
'internal-y1024-segment03.png':'Minor stone-grain variation, continuous real grout.',
'internal-y1024-segment04.png':'Minor stone-grain variation follows paver boundaries.',
'internal-y2048-segment01.png':'Subtle grain transition, no false hard band.',
'internal-y2048-segment02.png':'Subtle grain transition, closed grout corner.',
'internal-y2048-segment03.png':'Subtle grain transition, continuous horizontal stone boundary.',
'internal-y2048-segment04.png':'Subtle grain scale variation, complete T-joint.',
'internal-y3072-segment02.png':'Minor native fine-grain transition; vertical joint remains continuous.',
}
oldreview={'schemaVersion':1,'reviewedAt':now,'tile':'r05_c06','candidate':old['output'],'status':'repair_required','actuallyViewed':True,'nativeSeamSegments':24,'junctions':9,'reviewMethod':'All33 source-size crops actually viewed with view_image; whole candidate preview also viewed.','entries':[]}
for name,e in oldq.items():
    oldreview['entries'].append({'file':e['file'],'sha256':e['sha256'],'actuallyViewed':True,'status':'blocking' if name=='internal-y1024-segment01.png' else 'passed_with_nonblocking_observation' if name in observations else 'passed','note':'False horizontal tone reset across masonry at native y229; corrected in s02_01_tone02.' if name=='internal-y1024-segment01.png' else observations.get(name,'Complete geometry; no blocking seam.')})
oldfile=B/'qa'/'internal-review-b710fa388f5b.json';save(oldfile,oldreview)
entries=[];changed=[]
for name,e in newq.items():
    same=e['sha256']==oldq[name]['sha256']
    if not same:changed.append(name)
    assert not (same and name=='internal-y1024-segment01.png')
    entries.append({'file':e['file'],'sha256':e['sha256'],'status':'passed_with_nonblocking_observation' if name in observations else 'passed','actuallyViewed':True,'reviewBasis':'SHA-identical crop inherited from actual prior view' if same else 'Changed crop actually re-viewed at original pixel scale','inheritedFrom':ref(oldfile) if same else None,'note':observations.get(name,'Complete geometry; no blocking seam.')})
assert len(changed)==8
# Verify every candidate pixel is an unchanged source sample at the same world coordinate.
out=Path(new['output']['file']);arr=np.asarray(Image.open(out).convert('RGB'));mask=np.zeros((4096,4096),dtype=bool)
coords=read(B/'coordinates.json');tx,ty=coords['tileWorldBox'][:2]
sources=[]
for e in coords['patches']:
    path=p.selected_path(B,e['id']);v=p.validate_native(path,B,e['id']);sources.append({'id':e['id'],**v})
    a=np.asarray(Image.open(path).convert('RGB'));wx,wy,_,_=e['worldBoxWithHalo']
    x0=max(0,wx-tx);y0=max(0,wy-ty);x1=min(4096,wx-tx+1254);y1=min(4096,wy-ty+1254)
    sx=x0-(wx-tx);sy=y0-(wy-ty)
    mask[y0:y1,x0:x1]|=np.all(arr[y0:y1,x0:x1]==a[sy:sy+y1-y0,sx:sx+x1-x0],axis=2)
assert mask.all()
proof={'candidate':ref(out),'verifiedPixels':int(mask.size),'unmatchedPixels':int((~mask).sum()),'passed':True,'sameWorldCoordinate':True,'resized':False,'blended':False,'colorAdjusted':False}
proofpath=B/'qa'/'source-pixel-verification-03d4dd9f7332.json';save(proofpath,proof)
review={'schemaVersion':1,'reviewedAt':now,'tile':'r05_c06','candidate':ref(out),'status':'passed','actuallyViewed':True,'seamSegments':24,'junctions':9,'changedActuallyReviewed':8,'identicalActuallyViewedInherited':25,'previousReview':ref(oldfile),'entries':entries,'sourcePixelVerification':ref(proofpath),'nonblockingObservations':list(observations.values()),'limitations':'Outer whole-tile joint assembly remains separate; this is internal candidate QA only.'}
rpath=B/'qa'/'internal-review-03d4dd9f7332.json';save(rpath,review)
extpath=B/'qa'/'external-native-pairs'/'manifest.json';ext=read(extpath);extreview=[]
for e in ext:
    assert e['status']=='pending'
    extreview.append({**e,'status':'passed_with_nonblocking_observation' if e['side']=='south' or (e['side']=='west' and e['segment'] in (3,4)) else 'passed','actuallyViewed':True,'note':'No orphan grout or disconnected road remains. Minor native fine-grain/line-width variation retained.'})
er={'schemaVersion':1,'reviewedAt':now,'status':'native_pair_diagnostics_passed','actuallyViewed':True,'segments':8,'entries':extreview,'north':'pending; r04_c06 absent','east':'pending; r05_c07 absent','west':'4 native source pairs viewed, continuous; final cross-tile candidate boundary/junctions pending','south':'4 native source pairs viewed, final segment re-viewed after root-delegated s01_04_fix03 repair; final candidate boundary/junctions pending','formalAccepted':False}
erpath=B/'qa'/'external-native-pairs'/'review.json';save(erpath,er)
accept={'schemaVersion':1,'tile':'r05_c06','candidate':ref(out),'internalQA':{'status':'passed','actuallyViewed':True,'seamSegments':24,'junctions':9,'reviewer':'east_next_tile actual native-pixel view','reviewBasis':'Initial33 actual views, then8 changed actual views and25 exact-hash inheritances.','evidence':ref(rpath)},'externalQA':{'status':'pending','actuallyViewed':True,'reviewedSides':[],'worldBoundarySides':[],'nativePairDiagnostics':ref(erpath),'pending':['north neighbor absent','east neighbor absent','west/south final candidate cross-boundary and junction assembly review']},'formalAccepted':False,'actualModel':None,'actualQuality':None,'runtimeIntegration':False,'capacity5000Validated':False,'updatedAt':now}
save(B/'qa'/'acceptance.json',accept)
local=read(B/'local-continuation-20261011.json')
local.update({'updatedAt':now,'logicalNativeCompleted':16,'selectedNativeCount':16,'rawNativeOutputs':len(list((B/'native').glob('*.png.generation.json'))),'candidate':ref(out),'assemblyManifest':ref(B/'candidate'/f'{newn}.assembly.json'),'internalQA':accept['internalQA'],'externalQA':accept['externalQA'],'missingCoordinates':[],'formalAccepted':False,'blockingCurrentInternalIssues':[],'nextStep':'Root integrate current 4K candidate with neighboring candidates, inspect cross-tile junctions; north/east wait for actual neighbor art. No more local generation needed.'})
local['networkEvent']['firstPostRecoveryOutput']['sha256']=sha(B/'native'/'s04_03_resume01.png');save(B/'local-continuation-20261011.json',local)
receipt=read(B/'receipts'/'s04_03_resume01.request.json')
roundrec={'tile':'r05_c06','resumedAt':receipt['recordedAt'],'resumedAtBasis':'First recorded request after explicit network-restoration authorization','firstNewSuccessfulOutput':local['networkEvent']['firstPostRecoveryOutput'],'candidate':ref(out),'internalQA':accept['internalQA'],'externalQA':accept['externalQA'],'formalAccepted':False,'selectedSources':sources,'selectedNativeCount':16,'rawNativeOutputs':local['rawNativeOutputs'],'stillMissing':[],'error':{'historical':local['networkEvent']['message'],'resolved':True,'current':None},'next':local['nextStep'],'updatedAt':now}
save(B/'continuation-round-20261011.json',roundrec)
preview=B/'candidate'/'r05_c06-preview-only-1024.png';Image.open(out).resize((1024,1024),Image.Resampling.LANCZOS).save(preview)
save(preview.with_suffix('.png.derivation.json'),{'role':'preview-only, not native game art','source':ref(out),'operation':'downsample to1024 for display','formalArt':False})
print(json.dumps({'candidate':ref(out),'nativeSelected':16,'rawNative':local['rawNativeOutputs'],'internal':'passed33','nativePairDiagnostics':'8passed','formalAccepted':False,'sourcePixelProof':proof,'localContinuation':str(B/'local-continuation-20261011.json'),'roundContinuation':str(B/'continuation-round-20261011.json')},indent=2))

