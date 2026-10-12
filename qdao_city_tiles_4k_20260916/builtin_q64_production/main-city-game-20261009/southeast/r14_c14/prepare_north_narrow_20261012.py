from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,uuid,sys,importlib.util
import numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent; R=T/'repairs'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):
 p=Path(p);v={'path':str(p.resolve()),'sha256':sha(p)}
 try:v['size']=list(Image.open(p).size)
 except OSError:pass
 return v
def write(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
def png(p,im):
 with p.open('xb') as f:im.save(f,format='PNG')
cur=rd(T/'candidate/latest-assembly.json')
assert cur['candidate']['sha256']=='66848fcdb5ff648de5f448588dbb4cd1c70693dee07ea43f3b15da0ed353d377'
old=R/'north-platform-boundary-20261012T123237-005dc910'
p0=rd(old/'preparation.json');g0=rd(old/'generation.json')
neighbor=p0['neighborCore'];refs=p0['references'][:3]
for a in [cur['candidate'],cur['context'],neighbor,g0['native']]+refs:assert sha(a['path'])==a['sha256']
assert neighbor['sha256']=='89c0bd8fcf2a507c90a1b690a2e0911a8b490f195820502eb026c56f298bc2d4'
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
d=R/('north-shadow-narrow-'+stamp+'-'+uuid.uuid4().hex[:8]);d.mkdir()
raw=Image.new('RGB',(1254,1254));nc=[2842,3456,4096,4096];cc=[2842,0,4096,614]
raw.paste(Image.open(neighbor['path']).convert('RGB').crop(nc),(0,0));raw.paste(Image.open(cur['candidate']['path']).convert('RGB').crop(cc),(0,640))
# Keep the original two-level ledges. The unaccepted native supplies only a
# small shadow/material reference crop, never the edit target or final pixels.
refcrop=[640,470,1150,890]
png(d/'native-detail-reference-unadopted.png',Image.open(g0['native']['path']).convert('RGB').crop(refcrop))
boxes=[[0,640,1254,736],[650,736,1190,880]]
mask=Image.new('L',(1254,1254),0);draw=ImageDraw.Draw(mask)
for x,y,x1,y1 in boxes:draw.rectangle((x,y,x1-1,y1-1),fill=255)
png(d/'source-1254.png',raw);png(d/'edit-mask.png',mask)
guide=np.array(raw);guide[np.array(mask)>0]=[255,0,255];png(d/'target-1254.png',Image.fromarray(guide))
prompt="""Use case: precise-object-edit. Edit ONLY the LAST image, the exact native1254x1254 magenta-hole target. The first3 images are approved illustration/material style references only. The FOURTH image is an unaccepted integer-cropped prior output showing only local amber wood grain and a broad diagonal soft shadow. It is NOT a layout authority: do not copy that output's removal of a middle ledge or simplify this target's existing layered wooden structure.

Fill ONLY the magenta pixels of the LAST image. Preserve ALL visible nonmagenta pixels, their exact framing, scale, sharp wood grain, ledges, posts, ground and lighting. The entire UPPER640 rows are the immutable actual north neighbor core. All edits must be BELOW y640. This is a giant cropped local porch/platform detail: do not turn it into a complete building or add any object.

The first missing band is only y640..735. Continue the actual wood faces, bevel edges, grain and light that enter from the fixed row directly above y640, with no horizontal color line, grain cutoff, doubled lip, thickness jump or offset. The existing lower wooden faces immediately below the magenta band are equally fixed: smoothly connect to their exact structure. Retain the existing TWO ledge layers and every visible support; never remove a whole ledge as in the fourth reference.

The additional small lower magenta area x650..1189,y736..879 is solely for the existing broad shadow to continue naturally across the stepped wood. At y640 the fixed shadow comes from x roughly690..1050: continue that same soft diagonal shadow, its wood-grain visibility and edge into the marked lower area while respecting the existing ledge planes. Match every exposed lower/side boundary exactly. Do not invent a new shadow, end it with a horizontal rectangular cutoff, stretch the ledge, or repaint the unmarked lower posts. Any shadow transition must follow the visible existing structure and illumination.

Return one opaque native1254x1254 PNG at the exact same framing, with every magenta pixel filled. No zoom, pan, crop, resize, blur, new cracks, blue bands, foliage, props, text or UI. Final mechanical selection uses only these small lower-side marked regions; the upper neighbor, lower supports outside the marks and all other artwork remain immutable."""
(d/'prompt.txt').write_text(prompt,encoding='utf-8')
refs=refs+[{**art(d/'native-detail-reference-unadopted.png'),'role':'Unadopted source8516 local shadow/material-only integer crop; not a layout or pixel authority'},{**art(d/'target-1254.png'),'role':'LAST exact1254 target; only magenta lower-side regions may be edited'}]
request={'prompt':prompt,'referenced_image_paths':[a['path'] for a in refs],'transparent_background':False};write(d/'request.json',request)
prep={'schemaVersion':1,'tile':'r14_c14','version':d.name,'preparedAt':datetime.now(timezone.utc).isoformat(),'status':'prepared_offline_not_generated','networkCallMade':False,'sourceCandidate':cur['candidate'],'sourceContext':cur['context'],'neighborCore':neighbor,'neighborCoreCrop':nc,'currentCoreCrop':cc,'neighborPlacement':[0,0,1254,640],'currentPlacement':[0,640,1254,1254],'direction':'north','targetSeam':{'axis':'y','value':640},'rectanglesBeforeProtection':boxes,'maskRule':'Union of lower96-row boundary band and small shadow continuation rectangle to localy880. Everything at or above fixednorthy639 and below localy879 immutable. Stored alpha v2 is created before new output.','rawTarget':art(d/'source-1254.png'),'guide':art(d/'target-1254.png'),'editMask':art(d/'edit-mask.png'),'guideFillRGB':[255,0,255],'references':refs,'request':art(d/'request.json'),'prompt':art(d/'prompt.txt'),'sourceNativeReference':g0['native'],'nativeReferenceCrop':refcrop,'nativeReferenceCopiedIntoFinal':False,'oldFailedTrialAdopted':False,'sourceCoreProblemBox':[2842,0,4096,240],'desiredFinalApplication':'Only saved mask below fixed north core; integer crop and alpha v2. Published west candidate remains authority. Preserve all ledges/supports outside the narrow mask.','actualModel':None,'actualQuality':None,'resized':False,'formalAccepted':False,'reservedCorner':[0,0,630,630]}
write(d/'preparation.json',prep)
spec=importlib.util.spec_from_file_location('compositor',T/'offline_native_composition_v2_20261012.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
plan=mod.stage(d.name)
alpha=np.array(Image.open(plan['alpha']['path']));assert not alpha[:640].any();assert not alpha[880:].any()
refverify=np.array(Image.open(g0['native']['path']).convert('RGB').crop(refcrop));assert np.array_equal(refverify,Image.open(d/'native-detail-reference-unadopted.png').convert('RGB'))
result={'version':d.name,'request':art(d/'request.json'),'preparation':art(d/'preparation.json'),'target':art(d/'target-1254.png'),'raw':art(d/'source-1254.png'),'assemblyPlan':art(d/'assembly-plan-v2.json'),'alpha':plan['alpha'],'nativeReference':refs[3],'currentCandidateUnchanged':cur['candidate'],'oldNorthTrialAdopted':False,'editablePixelCount':int((alpha>0).sum()),'editableNativeFraction':round(float((alpha>0).mean()),5),'integerCrops':True,'alphaPreparedBeforeOutput':True,'fixedUpperNeighborAlphaZero':True,'originalLowerSupportAlphaZeroBelowTargetY':880,'frozenCornerUntouched':True,'networkCallMade':False,'actualModel':None,'actualQuality':None,'followup':'Generate this target first. After actual native selection, review upper boundaryy640, first lower edgey736 and shadow lower edgey880. Only prepare a dependent second target if a new actual boundary still fails. Old trialy1020 stripe is absent because no pixels from that trial are adopted.'}
write(d/'handoff.json',result);print(json.dumps(result,indent=2))

