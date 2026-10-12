from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
from datetime import datetime,timezone
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parent.parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
box=[11648,15700,12902,16954]
layout=Path(read(R.parent/'production-contract.json')['layoutReference'])
ref=Image.open(layout); ob=[q*ref.width/57344 for q in box]
im=ref.transform((1254,1254),Image.Transform.EXTENT,tuple(ob),resample=Image.Resampling.BICUBIC)
ids=np.zeros((1254,1254),np.uint8); sources=[]
def paste(p,bb,src,dst,sid,role):
 global im
 im.paste(Image.open(p).crop(src),tuple(dst[:2]));ids[dst[1]:dst[3],dst[0]:dst[2]]=sid
 sources.append({'sourceId':sid,'file':str(p),'sha256':sha(p),'globalNativeBox':bb,'sourceCrop':src,'destinationBox':dst,'role':role,'resampled':False})
# Correct upper geometry direct from preceding native bridge; no failed hard-cut diagnostic pixels.
b=R/'native/r04_c03_c04_blue_net_corner_bridge_v01.png';bb=read(str(b)+'.generation.json')['globalNativeBox']
paste(b,bb,[0,596,1254,1254],[0,0,1254,658],1,'correct existing upper bridge mesh and corner knot, exact native')
# Southern existing native owns all known lower-left including eastern115 halo.
b=R/'native/r05_c03_s01_s04_v03.png';bb=read(str(b)+'.generation.json')['globalNativeBox']
paste(b,bb,[499,89,1254,685],[0,658,755,1254],2,'existing southern native net anchors, exact native')
# Known right-tile lower26 continues current right native; boundary continuity reference only.
b=R/'native/r04_c04_s04_s01_v01.png';bb=read(str(b)+'.generation.json')['globalNativeBox']
paste(b,bb,[230,1113,729,1139],[755,658,1254,684],3,'known right tile existing lowest26 pixels; reconnect to upper new net')
name='r04_c03_c04_lower_net_transition_bridge_v01'
gp=D/(name+'.guide.png');ip=D/(name+'.guide-source-id.png')
im.save(gp);Image.fromarray(ids).save(ip)
for s in sources:
 yy,xx=np.nonzero(ids==s['sourceId']);a=np.asarray(Image.open(s['file']).convert('RGB'));bx,by,_,_=s['globalNativeBox']
 assert np.array_equal(np.asarray(im)[yy,xx],a[yy+box[1]-by,xx+box[0]-bx])
rp=R/'work-r03_c04/resume-20261010'
refs=[layout,Path(read(R.parent/'production-contract.json')['detailStyleReference']),rp/'designs/mail-ui-v1/01-mail-event.png',gp]
roles=['approved whole-map layout, not framing target','independent material and paint style','primary mail painting style, not objects','1254x1254 edit target with exact upper and lower native anchors and guide-only lower-right pixels']
record={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'edit-guide-only','name':name,'globalNativeBox':box,'globalCoreBox':[11763,15815,12787,16839],'size':[1254,1254],'guide':str(gp),'sha256':sha(gp),'sourceIdMap':str(ip),'sourceIdSha256':sha(ip),'sources':sources,'layoutGuideOnly':{'file':str(layout),'sha256':sha(layout),'fractionalSourceBox':ob,'sourceId':0,'count':int((ids==0).sum()),'notFinalPixels':True},'nativePixelsVerified':int((ids!=0).sum()),'repair':'Reconcile complete lower net mesh between upper bridge and existing south native. Hard source join y658 is a defect to remove. Preserve upper230 and lower230 left755 as native-coordinate anchors. Unknown lower-right is genuinely redrawn.'}
write(D/(name+'.plan.json'),record)
prompt='''Use case: compositing, precise seam repair for a continuous Q-style fishing-village game map.
OUTPUT: exactly 1254 by 1254 native pixels, same camera, no zoom, no crop/reframe, no layout scaling.
Reference roles: images 1/2/3 are mandatory approved global layout, independent detail materials, and primary bright polished painterly mail style. Image 4 is the ONLY framing and coordinate/edit target; output the same square close-up as image 4, not the whole map or UI.
Repair target: one continuous slate-blue hanging fishing net on clean warm sand. This exact crop is global [11648,15700,12902,16954]. Image4 top658 rows come directly from the already-correct upper native bridge. Lower-left rectangle x0..755,y658..1254 comes from the actual existing southern native net. Lower-right x755..1254,y684..1254 is blurry layout-only guidance: redraw at full native detail, continuing the right blue net and clean sand without adding props.
The hard horizontal step at y658 and tiny right step at y684 are construction defects, not intended lines. Integrate the middle mesh as a single natural soft draped fishing net: each thick grey-blue boundary rope and each thinner twisted mesh rope remains attached to knots, each mesh hole is cleanly enclosed, no dangling ends, double strands, clipped diamonds, or hard straight horizontal/vertical cut lines. Reconcile the top mesh into the bottom mesh across the middle area y250..1024.
LOCK: top230 rows, including the existing blue corner knot near (590,50), and all rope crossing locations at the top edge, are precise unchanged anchors. Bottom230 rows x0..755 and left outer115px are precise existing southern native anchors: preserve the exact visible existing knots and strand crossing coordinates so the new region can reconnect. Preserve rightmost existing wood-post edge and existing net at x1139..1254,y0..684. Match brightness and brush size across boundaries. Preserve overall net shape, hanging direction and rope thickness. Existing naturally overlapping net folds are okay; do not invent extra knots, props, pebbles, cracks, walls or plants.
Compose one coherent material transition between these fixed native anchors. Only adjust internal rope trajectories as needed to close the mesh. The unknown lower-right continues the existing right net toward lower cropped edge; do not force a full decorative net into the frame. No text, grid, labels, watermarks, borders, blur, vignette, dark seam strips, or graphic overlays. Keep exact local frame positions.'''
pf=D/(name+'.prompt.txt');pf.write_text(prompt,encoding='utf-8')
req={'createdAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','name':name,'promptFile':str(pf),'prompt':prompt,'referenced_image_paths':[str(x) for x in refs],'references':[{'file':str(p),'sha256':sha(p),'role':role} for p,role in zip(refs,roles)],'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'configSnapshot':read(rp/'config/image-generation.json'),'configEvidence':{'file':str(rp/'config/image-generation.json'),'sha256':sha(rp/'config/image-generation.json'),'recoveredHistoricalBatchSnapshot':True},'globalNativeBox':box,'globalCoreBox':[11763,15815,12787,16839]}
write(D/(name+'.request.json'),req)
print(json.dumps({'guide':str(gp),'request':str(D/(name+'.request.json')),'planSha256':sha(D/(name+'.plan.json')),'layoutOnlyPixels':int((ids==0).sum())}))

