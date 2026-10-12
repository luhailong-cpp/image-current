from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util,shutil
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;BASE=D.parent.parent;STEM='bench-C2-final-v6';FRAME=[31750,40200,33004,41454]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,a):
 p=D/n;assert not p.exists();p.write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
original=np.asarray(Image.open(D/'bench-C2-right-conditioned-v1-guide-native1254.png').convert('RGB'));a=original.copy()
m4=np.asarray(Image.open(D/'bench-C2-right-conditioned-v4-natural-floor-adopt-mask-native1254.png'))==255
m6=np.zeros((1254,1254),bool);m6[680:815,540:735]=True
for v,m in [(4,m4),(6,m6)]:a[m]=np.asarray(Image.open(D/f'bench-C2-right-conditioned-v{v}-raw.png').convert('RGB'))[m]
final=np.asarray(Image.open(D/'bench-C2-right-conditioned-v6-bounded-preview-native1254.png').convert('RGB'));assert np.array_equal(a,final)
union=m4|m6;assert np.array_equal(original[~union],final[~union])
npz=D/(STEM+'-native-source-replay.npz');np.savez_compressed(npz,original=original,mask_v4=m4,mask_v6=m6,final=final)
records=json.loads((D/'bench-C2-right-conditioned-v6.adoption-check.json').read_text())['patches']
spec=importlib.util.spec_from_file_location('native_sources',BASE/'review_external_seams.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);sources=helper.Sources()
patches=[]
for r in records:
 cur,error=sources.source(r['tile'],r['patch']);assert not error
 assert cur['file']==r['source'] and cur['sha256']==r['sourceSha256']
 p=D/(STEM+'-'+r['tile']+'-'+r['patch']+'-provisional-native1254.png');assert not p.exists();shutil.copy2(r['file'],p)
 old=np.asarray(Image.open(r['source']).convert('RGB'));new=np.asarray(Image.open(p).convert('RGB'))
 patches.append({'tile':r['tile'],'patch':r['patch'],'file':str(p),'sha256':sha(p),'source':r['source'],'sourceSha256':r['sourceSha256'],'componentCandidate':r['file'],'componentCandidateSha256':r['sha256'],'nativeFrameWorld':r['nativeFrameWorld'],'coreChangedPixels':int(np.any(old[115:1139,115:1139]!=new[115:1139,115:1139],axis=2).sum()),'formalAccepted':False,'selected':False})
 sources.tile(r['tile'])['selection']['patches'][r['patch']]=str(p)
rebuilt,pieces,missing=sources.extract(FRAME);assert not missing;assert np.array_equal(np.asarray(rebuilt),final)
review={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'shadow_candidate_material_and_upper_beam_geometry_pending','viewed':['v4 floor mask4outer and entire beam/rim natural boundaries','v6 actual rect4outer/rimface and combined final4outer/center'],'observations':['Original x32371 floor shadow/tone cutoff removed from the floor compartment.','Original x32371 shadow cutoff on gold rim top face now softened by native v6 color edit.','No new main floor-groove or gold-rim silhouette discontinuity observed after natural-mask and rect adoption.','Original upper crossbar small step at x32371 above floor repair remains untouched; bench geometry still open.','Adoption edge tone/grain-density variations remain, particularly left x32290/x32322 and bottom y41015; retain material pending.'],'materialPending':True,'benchGeometryPending':True,'internalReady':False,'formalAccepted':False,'canonicalSelectionsModified':False}
save(STEM+'.native-review-v1.json',review)
save(STEM+'.adoption-instructions.json',{'schemaVersion':1,'status':'candidate_shadow_material_pending','frameWorld':FRAME,'overallAdoptionBoundingWorld':[32290,40556,32633,41015],'nativeCore':[115,115,1139,1139],'patches':patches,'components':[{'raw':str(D/'bench-C2-right-conditioned-v4-raw.png'),'rawSha256':sha(D/'bench-C2-right-conditioned-v4-raw.png'),'mask':str(D/'bench-C2-right-conditioned-v4-natural-floor-adopt-mask-native1254.png'),'maskSha256':sha(D/'bench-C2-right-conditioned-v4-natural-floor-adopt-mask-native1254.png')},{'raw':str(D/'bench-C2-right-conditioned-v6-raw.png'),'rawSha256':sha(D/'bench-C2-right-conditioned-v6-raw.png'),'guideBox':[540,680,735,815],'worldBox':[32290,40880,32485,41015]}],'nativeSourceReplayExact':True,'nativeCoreReplayExact':True,'outsideUnionChangedPixels':0,'replayNpz':str(npz),'replayNpzSha256':sha(npz),'materialPending':True,'benchGeometryPending':True,'internalReady':False,'formalAccepted':False,'resampling':False,'pixelShift':False,'blur':False,'syntheticGeometry':False,'paidApiUsed':False,'canonicalSelectionsModified':False,'adoptionInstructions':'Root may independently inspect and coordinate both exact native files atomically. Preserve all other selected patch entries. Do not mark internalReady or formalAccepted; upper bench beam geometry and adoption-edge material finish remain open.'})
save('bench-C2-right-conditioned-v3.native-review-v1.json',{'schemaVersion':1,'status':'rejected_mask_partly_overlaps_gold_top_face','observation':'Coarse floor polygon cut across original shaded gold top face; original bright rim pixels/old floor slivers created broken boundary. Superseded by v4 natural mask.','formalAccepted':False})
save('bench-C2-right-conditioned-v4.native-review-v1.json',review)
save('bench-C2-right-conditioned-v5.native-review-v1.json',{'schemaVersion':1,'status':'rejected_doubled_top_edge','observation':'Inner-face mask included original upper highlight contour; native output shifted/doubled contour and left explicit material slot boundaries.','formalAccepted':False})
save('bench-C2-right-conditioned-v5b.native-review-v1.json',{'schemaVersion':1,'status':'rejected_visible_highlight_slot','observation':'Preserving original contour with smaller interior cut removed black double edge but left highlighted rectangular slot at old shadow cut. Superseded by v6 color-only native edit.','formalAccepted':False})
save('bench-C2-right-conditioned-v6.native-review-v1.json',review)
print(json.dumps({'adoptionInstructions':str(D/(STEM+'.adoption-instructions.json')),'patches':[{'tile':r['tile'],'patch':r['patch'],'coreChangedPixels':r['coreChangedPixels']} for r in patches],'outsideUnionChangedPixels':0,'nativeCoreReplayExact':True}))

