from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util,shutil
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;BASE=D.parent.parent;STEM='bench-C2-best-v7-20261013';FRAME=[31750,40200,33004,41454]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,a):
 p=D/n;assert not p.exists(),p;p.write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
base=read(D/'bench-C2-final-v6.adoption-instructions.json');latest=read(D/'bench-C2-right-conditioned-v7.adoption-check.json')
z=np.load(base['replayNpz']);original=z['original'];a=original.copy();m4=z['mask_v4'];m6=z['mask_v6'];m7=np.zeros((1254,1254),bool);m7[275:360,597:666]=True
for v,m in [(4,m4),(6,m6),(7,m7)]:a[m]=np.asarray(Image.open(D/('bench-C2-right-conditioned-v'+str(v)+'-raw.png')).convert('RGB'))[m]
assert np.array_equal(a,np.asarray(Image.open(latest['boundedPreview']).convert('RGB')))
union=m4|m6|m7;assert np.array_equal(original[~union],a[~union])
npz=D/(STEM+'-native-source-replay.npz');assert not npz.exists();np.savez_compressed(npz,original=original,mask_v4=m4,mask_v6=m6,mask_v7=m7,final=a)
rs={(r['tile'],r['patch']):r for r in base['patches']};rs.update({(r['tile'],r['patch']):r for r in latest['patches']})
spec=importlib.util.spec_from_file_location('sources',BASE/'review_external_seams.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);sources=helper.Sources();patches=[]
for key,r in rs.items():
 cur,err=sources.source(*key);assert not err
 assert cur['file']==r['source'] and cur['sha256']==r['sourceSha256']
 assert sha(r['file'])==r['sha256']
 p=D/(STEM+'-'+key[0]+'-'+key[1]+'-provisional-native1254.png');assert not p.exists();shutil.copy2(r['file'],p)
 rr={'tile':key[0],'patch':key[1],'file':str(p),'sha256':sha(p),'source':r['source'],'sourceSha256':r['sourceSha256'],'nativeFrameWorld':r['nativeFrameWorld'],'componentCandidate':r['file'],'selected':False,'formalAccepted':False};patches.append(rr);sources.tile(key[0])['selection']['patches'][key[1]]=str(p)
rebuilt,_,missing=sources.extract(FRAME);assert not missing;assert np.array_equal(a,np.asarray(rebuilt))
review={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'upper_beam_local_geometry_repaired_material_pending','viewedEvidence':latest['evidence'],'allFiveCropsViewedNative':True,'observations':['The upper beam bright lower bevel now crosses world x32371 continuously; the previous abrupt local step is removed.','V7 adopts only guide[597,275,666,360] / world[32347,40475,32416,40560]; all prior v4 floor and v6 rim-face pixels outside this69x85 area are unchanged.','A rectangular orange-brown grain/tone patch is still visible around the local bevel infill; existing wider floor/rim material variations remain.'],'localUpperBeamGeometryPassed':True,'materialPending':True,'internalReady':False,'formalAccepted':False,'canonicalSelectionsModified':False,'statusDoesNotApproveOtherBenchJunctions':True}
save(STEM+'.native-review.json',review)
components=base['components']+[{'raw':latest['raw'],'rawSha256':latest['rawSha256'],'guideBox':latest['adoptGuideBox'],'worldBox':latest['adoptWorldBox']}]
save(STEM+'.adoption-instructions.json',{'schemaVersion':1,'status':'best_geometry_candidate_material_pending','frameWorld':FRAME,'overallAdoptionBoundingWorld':[32290,40475,32633,41015],'nativeCore':[115,115,1139,1139],'patches':patches,'componentsInOrder':components,'nativeSourceReplayExact':True,'nativeCoreReplayExact':True,'outsideUnionChangedPixels':0,'replayNpz':str(npz),'replayNpzSha256':sha(npz),'materialPending':True,'localUpperBeamGeometryPassed':True,'internalReady':False,'formalAccepted':False,'resampling':False,'pixelShift':False,'blur':False,'syntheticGeometry':False,'paidApiUsed':False,'actualModel':None,'actualQuality':None,'canonicalSelectionsModified':False,'review':str(D/(STEM+'.native-review.json')),'adoptionInstructions':'For root independent review, not a passed final tile. Verify current source hashes before any coordinated provisional geometry adoption of both exact native files; preserve every other patch and all source history. Material boundaries remain unresolved.'})
print(json.dumps({'adoptionInstructions':str(D/(STEM+'.adoption-instructions.json')),'patches':patches,'outsideUnionChangedPixels':0,'nativeCoreReplayExact':True}))

