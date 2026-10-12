import json,hashlib,datetime
from pathlib import Path
import numpy as np
from PIL import Image
t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14");s=t.parent
version="north-far-east-ledges-20261012-v1";d=t/"repairs"/version
assert not d.exists();d.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
base=t/"candidate/r14_c14-4k-west-material-composed-v1-20261012.png"
north=s/"r13_c14/candidate/r13_c14-4k-repaired-west-remove-grout-stub-20261011T082322-15c2e7ac-masked.png"
halo=t/"repairs/north-halo-audit-20261012/south-halo-4096x115-exact.png"
prov=t/"repairs/north-halo-audit-20261012/provenance.json"
assert sha(base)=="66848fcdb5ff648de5f448588dbb4cd1c70693dee07ea43f3b15da0ed353d377"
assert sha(north)=="89c0bd8fcf2a507c90a1b690a2e0911a8b490f195820502eb026c56f298bc2d4"
b=Image.open(base).convert("RGB");n=Image.open(north).convert("RGB")
clean=Image.new("RGB",(1254,1254));clean.paste(n.crop((2842,3456,4096,4096)),(0,0));clean.paste(b.crop((2842,0,4096,614)),(0,640))
cp=d/"reference-current-join-native-1254.png";clean.save(cp)
continuity=Image.new("RGB",(1254,755));continuity.paste(n.crop((2842,3456,4096,4096)),(0,0));continuity.paste(Image.open(halo).convert("RGB").crop((2842,0,4096,115)),(0,640))
hp=d/"reference-audited-north-continuity-1254x755.png";continuity.save(hp)
mask=np.zeros((300,1254),dtype=bool)
for x in range(32,1254):
 ymax=810 if x<175 else round(922-0.17*x)
 mask[:ymax-640,x]=True
# 24px inward alpha; top is a fixed-core join and is not feathered vertically.
dist=np.zeros(mask.shape,dtype=np.uint8);cur=mask.copy()
for k in range(24):
 dist[cur]+=1
 padded=np.pad(cur,((0,1),(1,1)),constant_values=False)
 up=np.concatenate([cur[:1],cur[:-1]],axis=0)
 cur=cur & up & padded[1:,1:-1] & padded[:-1,:-2] & padded[:-1,2:]
alpha=np.rint(dist.astype(float)/24*255).astype(np.uint8);alpha[~mask]=0
am=np.zeros((1254,1254),np.uint8);am[640:940]=alpha
ap=d/"alpha-native-1254.png";Image.fromarray(am).save(ap)
Image.fromarray(alpha).save(d/"alpha-crop.png")
Image.fromarray(mask.astype(np.uint8)*255).save(d/"mask-crop.png")
target=np.array(clean);target[640:940][mask]=(255,0,255);tp=d/"edit-target-native-1254.png";Image.fromarray(target).save(tp)
prompt="""Use case: precise-object-edit.
Return one native 1254 x 1254 RGB image at exactly the framing, perspective and object scale of image 1.
Image 1 is the edit target; only the magenta area on the lower/new side is editable. Image 2 is the unmarked current true-core join, preserving the complete existing construction. Image 3 is a 1254 x 755 native continuity reference: its top 640 rows are the immutable northern core and its final 115 rows are individually traced, reviewed real native pixels from that northern image. It is a structural/wood-grain continuation reference only, not a finished join to the lower image; do not stretch it or copy its bottom as a straight cut.
Repair the narrow junction at image y=640: continue the actual upper wooden platform's bevel, front-face grain, and broad cast shadow smoothly downward into the new-side magenta area, then join the existing lower structure. The shadow crosses the boundary around x690..1050 and must remain one continuous, naturally soft dark shape, with no horizontal cut, strip, pale hole, or duplicate edge at y640 or at the mask's lower outline.
The platform has TWO distinct horizontal wooden levels: the large upper tabletop/platform with its thick bright beveled rim, and the lower projecting ledge/step with its own bright front upper edge and darker front fascia. Preserve BOTH, their spacing, slope and existing right/left connections. Preserve the tall left upright and the existing legs/supports, gray paving and all shadows below. Do not erase, merge, thin into one slab, complete, move or add any platform, ledge, leg, seam, object or trim. Match the fixed upper-core geometry exactly; make only the child-side adjustment needed to reconcile it with the existing lower ledge. The native continuity reference should guide the broad upper-face grain and shadow, while the unmarked full target governs the lower ledge and all surrounding structure.
Keep all y<640 pixels untouched. Preserve all pixels outside magenta, especially the lower ledge's bright rim below the mask, the leftmost strip, the far-right join, supports, and stone. Use the existing warm wood color and brush detail; no global color/contrast change, blur, seam-hiding glow, text, extra marks or border. Remove magenta completely.
"""
pp=d/"prompt.txt";pp.write_text(prompt,encoding="utf-8")
req={"schemaVersion":1,"tile":"r14_c14","version":version,"status":"offline_prepared_not_generated","tool":"image_gen.imagegen","route":"builtin","actualModel":None,"actualQuality":None,"submittedParameters":{"prompt":prompt,"referenced_image_paths":[str(tp),str(cp),str(hp)],"transparent_background":False}}
rp=d/"request.json";rp.write_text(json.dumps(req,indent=2)+"\n")
prep={"schemaVersion":1,"tile":"r14_c14","version":version,"preparedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"offline_prepared_not_generated","sourceCandidate":info(base),"neighborCore":info(north),"auditedNativeHalo":info(halo),"provenance":info(prov),"target":info(tp),"references":[info(cp),info(hp)],"fixedNorthCoreSourceBox":[2842,3456,4096,4096],"childSourceBox":[2842,0,4096,614],"seamTargetY":640,"nativeCrop":[0,640,1254,940],"pasteBoxIn4096":[2842,0,4096,300],"alpha":info(d/"alpha-crop.png"),"fullAlpha":info(ap),"mask":info(d/"mask-crop.png"),"maskRule":"x32..1253, from y640 to y810 for x<175 or y round(922-0.17*x) otherwise; 24px inward alpha at child-side mask boundaries, no vertical fading at fixed-core join. x32 and x1253 have only 1/24 alpha; outside alpha remains unchanged.","frozenNW630Untouched":True,"partial10dUsed":False,"partial10dStatus":"unpublished; retained separately; x2842/2874 old transition remains to recheck, not certified","styleReferences":"Only actual existing native wood construction; no general style/layout changes","prompt":info(pp),"request":info(rp),"blendArithmetic":"(old*(255-alpha)+new*alpha+127)//255 uint32","resampling":False,"RGBColorCorrection":False,"formalAccepted":False,"qaRequirements":["y640 fixed-core join in all three x sections","two intact platform levels","shadow continuation x690..1050","entire shaped bottom alpha boundary","new right edge against unchanged r14_c15 west q0","left endpoint x2874 and unpublished partial transition"],"noNetworkCallMade":True}
pr=d/"preparation.json";pr.write_text(json.dumps(prep,indent=2)+"\n")
resume=t/"production-resume-20261012.json"
r=json.loads(resume.read_text(encoding="utf-8-sig"));r["latestOfflinePreparation"]={"version":version,"preparation":info(pr),"request":info(rp),"status":"awaiting_root_builtin_original","currentPublishedCandidate":info(base),"workerNetworkRetried":False};resume.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":version,"request":info(rp),"preparation":info(pr),"target":info(tp)}))
