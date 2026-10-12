from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util,shutil
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;BASE=D.parent.parent;STEM='eastdeck-G2-final-v5';FRAME=[32141,37925,33395,39179]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(n):return json.loads((D/n).read_text(encoding='utf-8-sig'))
def save(n,a):
 p=D/n;assert not p.exists(),p;p.write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
original=np.asarray(Image.open(D/'eastdeck-G2-conditioned-v1-guide-native1254.png').convert('RGB'))
a=original.copy()
m3=np.zeros((1254,1254),bool);m3[340:1100,440:850]=True
m4=np.asarray(Image.open(D/'eastdeck-G2-conditioned-v4-adopt-mask-native1254.png'))==255
m5=np.asarray(Image.open(D/'eastdeck-G2-conditioned-v5-top-adopt-mask-native1254.png'))==255
for v,m in [(3,m3),(4,m4),(5,m5)]:
 raw=np.asarray(Image.open(D/f'eastdeck-G2-conditioned-v{v}-raw.png').convert('RGB'));a[m]=raw[m]
final=np.asarray(Image.open(D/'eastdeck-G2-conditioned-v5-bounded-preview-native1254.png').convert('RGB'))
assert np.array_equal(a,final)
union=m3|m4|m5;assert np.array_equal(original[~union],final[~union])
npz=D/(STEM+'-native-source-replay.npz');np.savez_compressed(npz,original=original,mask_v3=m3,mask_v4=m4,mask_v5=m5,final=final)
base=read('eastdeck-G2-conditioned-v4.composite-base-manifest.json');latest=read('eastdeck-G2-conditioned-v5.adoption-check.json')
records={(r['tile'],r['patch']):r for r in base['patches']};records.update({(r['tile'],r['patch']):r for r in latest['patches']})
spec=importlib.util.spec_from_file_location('native_sources',BASE/'review_external_seams.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);sources=helper.Sources()
patches=[]
for key,r in records.items():
 cur,error=sources.source(*key);assert not error
 assert cur['file']==r['source'] and cur['sha256']==r['sourceSha256']
 p=D/(STEM+'-'+key[0]+'-'+key[1]+'-provisional-native1254.png');assert not p.exists();shutil.copy2(r['file'],p)
 old=np.asarray(Image.open(r['source']).convert('RGB'));new=np.asarray(Image.open(p).convert('RGB'))
 patches.append({'tile':key[0],'patch':key[1],'file':str(p),'sha256':sha(p),'source':r['source'],'sourceSha256':r['sourceSha256'],'selectedNativeSourceVerifiedCurrent':True,'componentCandidate':r['file'],'componentCandidateSha256':r['sha256'],'nativeFrameWorld':r['nativeFrameWorld'],'coreChangedPixels':int(np.any(old[115:1139,115:1139]!=new[115:1139,115:1139],axis=2).sum()),'selected':False,'formalAccepted':False})
 sources.tile(key[0])['selection']['patches'][key[1]]=str(p)
rebuilt,pieces,missing=sources.extract(FRAME);assert not missing;assert np.array_equal(np.asarray(rebuilt),final)
v=final.mean(2);rows={}
for x in [779,780,914,915]:
 centers=[390,503,644,818,1014];rows[x]=[int(v[y-20:y+21,x].argmin()+y-20) for y in centers]
review={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'geometry_candidate_material_pending_independent_review','viewed':['v4 20 actual local perimeters native atlas','v5 top mask4perimeters and fixed stone boundary','v5 final4outer and full G2 core context'],'fiveGapRightDarkestRows':rows,'leftEndpointDeltaPixels':[-1,-1,0,0,0],'rightEndpointDeltaPixels':[0,-1,-1,1,0],'observations':['Six main plank grooves are now connected across x32768; original gap-spacing discrepancy is distributed by shallow native curves.','Stone pixels were protected by source object mask; no stone silhouette shift adopted.','Main source/candidate RGB and density rectangles remain visible at original upper shadow cut and bounded wood edges, particularly x32921/x33056 around the five endpoint infills.'],'geometryReadyForIndependentReview':True,'materialPending':True,'internalReady':False,'formalAccepted':False,'canonicalSelectionsModified':False}
save(STEM+'.native-review-v1.json',review)
instruction={'schemaVersion':1,'status':'candidate_material_pending','frameWorld':FRAME,'overallAdoptionBoundingWorld':[32581,38135,33056,39025],'nativeCore':[115,115,1139,1139],'patches':patches,'components':[{'raw':str(D/'eastdeck-G2-conditioned-v3-raw.png'),'rawSha256':sha(D/'eastdeck-G2-conditioned-v3-raw.png'),'guideBox':[440,340,850,1100],'worldBox':[32581,38265,32991,39025]},{'raw':str(D/'eastdeck-G2-conditioned-v4-raw.png'),'rawSha256':sha(D/'eastdeck-G2-conditioned-v4-raw.png'),'adoptMask':str(D/'eastdeck-G2-conditioned-v4-adopt-mask-native1254.png'),'maskSha256':sha(D/'eastdeck-G2-conditioned-v4-adopt-mask-native1254.png')},{'raw':str(D/'eastdeck-G2-conditioned-v5-raw.png'),'rawSha256':sha(D/'eastdeck-G2-conditioned-v5-raw.png'),'adoptMask':str(D/'eastdeck-G2-conditioned-v5-top-adopt-mask-native1254.png'),'maskSha256':sha(D/'eastdeck-G2-conditioned-v5-top-adopt-mask-native1254.png')}],'exactNativeSourceReplay':True,'nativeCoreReplayExact':True,'outsideUnionChangedPixels':0,'replayNpz':str(npz),'replayNpzSha256':sha(npz),'resampling':False,'pixelShift':False,'blur':False,'syntheticGeometry':False,'paidApiUsed':False,'internalReady':False,'formalAccepted':False,'materialPending':True,'adoptionInstructions':'Root may independently inspect geometry then coordinate all four exact native files atomically. Preserve all other selected patch entries and original sources. These are geometry candidates with material pending; do not mark tile internalReady or formalAccepted.'}
save(STEM+'.adoption-instructions.json',instruction)
save('eastdeck-G2-conditioned-v4.native-review-v1.json',{'schemaVersion':1,'status':'geometry_endpoint_candidate_material_pending','viewed20ActualLocalPerimeters':True,'darkestRows':rows,'materialPending':True,'formalAccepted':False,'canonicalSelectionsModified':False})
save('eastdeck-G2-conditioned-v5.native-review-v1.json',review)
save('bench-C2-right-conditioned-v2.native-review-v1.json',{'schemaVersion':1,'status':'rejected_new_floor_and_rim_discontinuities','viewed':['center','left','top','right','bottom'],'observation':'Upper gold beam nearer original, but floor groove/rising lower rim shifted at new right boundary; no adoption.','formalAccepted':False,'canonicalSelectionsModified':False})
print(json.dumps({'adoptionInstructions':str(D/(STEM+'.adoption-instructions.json')),'patches':[{'tile':r['tile'],'patch':r['patch'],'coreChangedPixels':r['coreChangedPixels']} for r in patches],'outsideUnionChangedPixels':0,'nativeCoreReplayExact':True}))

