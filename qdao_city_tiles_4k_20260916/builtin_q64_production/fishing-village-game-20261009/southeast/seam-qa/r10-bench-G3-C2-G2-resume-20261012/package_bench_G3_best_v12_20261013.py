from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util,shutil
from datetime import datetime,timezone
D=Path(__file__).resolve().parent; BASE=D.parent.parent; STEM='bench-G3-best-v12-20261013'; FRAME=[30550,40200,31804,41454]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(n):return json.loads((D/n).read_text(encoding='utf-8-sig'))
def save(n,a):
 p=D/n; assert not p.exists(),p; p.write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
versions=['6','9b','10b','11','12']
checks=[read('bench-G3-left-conditioned-v'+v+'.adoption-check.json') for v in versions]
original=np.asarray(Image.open(checks[0]['beforeGuide']).convert('RGB')); result=original.copy()
union=np.zeros((1254,1254),bool); data={'original':original}; components=[]
for v,c in zip(versions,checks):
 assert sha(c['raw'])==c['rawSha256']
 box=c['adoptGuideBox']; mask=np.zeros((1254,1254),bool);mask[box[1]:box[3],box[0]:box[2]]=True
 raw=np.asarray(Image.open(c['raw']).convert('RGB')); result[mask]=raw[mask]; union|=mask
 assert np.array_equal(result,np.asarray(Image.open(c['boundedPreview']).convert('RGB')))
 data['mask_v'+v]=mask
 components.append({'version':v,'raw':c['raw'],'rawSha256':c['rawSha256'],'adoptGuideBox':box,'adoptWorldBox':c['adoptWorldBox'],'report':str(D/('bench-G3-left-conditioned-v'+v+'.adoption-check.json'))})
assert np.array_equal(original[~union],result[~union])
data['final']=result; npz=D/(STEM+'-native-source-replay.npz'); assert not npz.exists(); np.savez_compressed(npz,**data)
spec=importlib.util.spec_from_file_location('native_sources',BASE/'review_external_seams.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);sources=helper.Sources()
original_replay,pieces,missing=sources.extract(FRAME);assert not missing;assert np.array_equal(original,np.asarray(original_replay))
patches=[]
for r in checks[-1]['patches']:
 cur,error=sources.source(r['tile'],r['patch']);assert not error
 assert cur['file']==r['source'] and cur['sha256']==r['sourceSha256']
 assert sha(r['file'])==r['sha256']
 p=D/(STEM+'-'+r['tile']+'-'+r['patch']+'-provisional-native1254.png');assert not p.exists();shutil.copy2(r['file'],p)
 old=np.asarray(Image.open(r['source']).convert('RGB'));new=np.asarray(Image.open(p).convert('RGB'))
 core_diff=np.any(old[115:1139,115:1139]!=new[115:1139,115:1139],axis=2)
 patches.append({'tile':r['tile'],'patch':r['patch'],'file':str(p),'sha256':sha(p),'source':r['source'],'sourceSha256':r['sourceSha256'],'selectedNativeSourceVerifiedCurrent':True,'nativeFrameWorld':r['nativeFrameWorld'],'componentCandidate':r['file'],'componentCandidateSha256':r['sha256'],'coreChangedPixels':int(core_diff.sum()),'selected':False,'formalAccepted':False})
 sources.tile(r['tile'])['selection']['patches'][r['patch']]=str(p)
rebuilt,pieces,missing=sources.extract(FRAME);assert not missing;assert np.array_equal(np.asarray(rebuilt),result)
raw12=np.asarray(Image.open(checks[-1]['raw']).convert('RGB'))
before12=np.asarray(Image.open(checks[-1]['beforeGuide']).convert('RGB'))
rows=[]
for x,center in [(584,763),(585,763),(709,835),(710,835)]:
 ys=np.arange(center-12,center+13); vals=result[ys,x].mean(axis=1)
 rows.append({'guideX':x,'darkDeckGapY':int(ys[vals.argmin()])})
review={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'best_geometry_candidate_deferred_material_pending','reviewedEvidence':checks[-1]['evidence'],'allFiveEvidenceViewedNative':True,'currentWhole1254ContextViewed':True,'endpointRows':rows,'observations':['v12 gap crosses the former inner hole with a continuous thin dark outline and matching diagonal direction; no fork or added plank.','Golden upper beam and prior endpoint repairs are preserved.','Visible inherited rectangular material and color transitions remain, including the long horizontal cut near guide y760 and narrow vertical transitions near x515/x585/x710. Small local lower beam edge tangency is also not a final material pass.'],'materialPending':True,'internalReady':False,'formalAccepted':False,'canonicalSelectionsModified':False,'accelerationDisposition':'Preserve this best candidate and stop repeated repair on this same local joint; continue independent missing native cores before grouped material finishing.','furtherGenerationQueued':False}
save(STEM+'.native-review.json',review)
save(STEM+'.adoption-instructions.json',{'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'best_candidate_preserved_not_ready_for_final_adoption','frameWorld':FRAME,'overallAdoptionBoundingWorld':[31065,40520,31312,41060],'nativeCore':[115,115,1139,1139],'patches':patches,'componentsInOrder':components,'exactNativeSourceReplay':True,'nativeCoreReplayExact':True,'outsideUnionChangedPixels':0,'replayNpz':str(npz),'replayNpzSha256':sha(npz),'review':str(D/(STEM+'.native-review.json')),'actualModel':None,'actualQuality':None,'entry':'builtin image_gen.imagegen','paidApiUsed':False,'resampling':False,'pixelShift':False,'blur':False,'syntheticGeometry':False,'internalReady':False,'formalAccepted':False,'materialPending':True,'adoptionInstructions':'Retained for root independent review only; do not mark accepted. If later coordinating a provisional geometry adoption, verify both canonical source hashes then replace both exact1254 files together, preserving every other selected patch. Full native-source chain is replayable from v6,v9b,v10b,v11,v12 rectangles; no scaling or blending.'})
save('joint-resume-checkpoint-20261013-v2.json',{'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'lastGeneration':'bench-G3-left-conditioned-v12','receipt':str(D/'bench-G3-left-conditioned-v12.generation-receipt.json'),'bestCandidate':str(D/(STEM+'.adoption-instructions.json')),'inFlight':False,'rawSaved':True,'canonicalSelectionsModified':False,'deferredMaterialProblems':['benchG3 v12 material rectangles','eastdeckG2 finalv5 material rectangles','benchC2 finalv6 local upperbeam step and material boundaries','root-adopted wallG4/G5 and sharedstairsG3 material finishing'],'currentAssignmentCompleteWithDeferredIssues':True,'internalReady':False,'formalAccepted':False})
print(json.dumps({'adoptionInstructions':str(D/(STEM+'.adoption-instructions.json')),'patches':patches,'endpointRows':rows,'exactReplay':True,'materialPending':True}))

