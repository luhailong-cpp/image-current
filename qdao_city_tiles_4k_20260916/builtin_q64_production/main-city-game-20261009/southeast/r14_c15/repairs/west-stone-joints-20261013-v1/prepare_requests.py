from pathlib import Path
from PIL import Image
import json,hashlib,datetime
import numpy as np
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c15/repairs/west-stone-joints-20261013-v1");i=json.loads((D/"diagnostic-index.json").read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
rules=[Path(r"D:/work/image/AGENTS.md"),Path(r"D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md")]
jobs=[
("W01",[640,470,1000,680],"""Remove the spurious diagonal grout branch that begins abruptly at target x640,y610 and runs upward-right to the existing major grout intersection near x975,y530. The fixed left stone face is continuous at y610; the child's short branch must not appear from nowhere. Replace only that entire erroneous branch with the same uninterrupted natural gray stone face, including its former bright bevel and dark groove, all the way to the existing major diagonal/near-vertical grout at the right. Keep that major grout and its rightward branch in place. Preserve the lower slab boundary and foliage shadows. Do not retain a shortened blind groove, T-stub, shadow line or ghost bevel at either end. The goal is one continuous slab across x640 in this small area, not a new grout line in the immutable left image."""),
("W02",[640,420,960,880],"""Repair the broken slab-joint topology immediately right of target x640. A genuine joint approaches the fixed boundary from the lower-left, from about (595,730) to (640,680), then stops. Continue that SAME diagonal joint across x640 toward the upper-right so it meets the existing upper-right joint within the mask, near target (915,470). Keep matching its existing width, dark center and bright stone bevel. The current isolated child slab corner near (645,600) and its diagonal segment toward (800,780) conflict with that incoming line; locally reconstruct this misplaced corner/branch so the slab borders connect naturally, without a gap, floating slot, doubled bevel or crossing grooves. Keep the unchanged main lower-left to lower-right slab boundary, the fixed outer-mask joint endpoints and the gray paving/shadows. The intended correction is a local junction rebuild confined to magenta, not a global shift or rescaling of the paving. Preserve every leaf, stone rail, red paper and their shadows outside magenta."""),
("W03",[640,490,915,920],"""Continue the real grout line coming from the fixed lower-left stone into the boundary around target (640,674). Extend that same diagonal groove upward-right to the existing main descending diagonal joint near (755,588), making a natural T-junction with the same width, dark center and highlighted bevel. There is a DIFFERENT erroneous lower child-side branch beginning near (640,839) and running toward (845,692); remove this entire lower orphaned branch, filling its groove and bevel with matching stone, because there is no matching grout at that height in the immutable left core. Retain the main descending diagonal joint and the existing branch extending from around (845,692) toward the upper-right outside the mask; it can meet that main line as a staggered T-junction. There must be no blind groove, new crossed lines, diagonal doubled edge, or stone-texture stripe. Keep natural stone cracks distinct from deep grout joints. Preserve red paper, foliage, red barrel and existing shadows outside magenta.""")
]
out=[]
for code,rect,local in jobs:
 w=next(x for x in i["windows"] if x["id"]==code);p=D/code
 assert sha(w["path"])==w["sha256"]
 ref=Image.open(w["path"]).convert("RGB");target=ref.copy();target.paste((255,0,255),tuple(rect))
 targetp=p/"edit-target-native-1254.png";assert not targetp.exists();target.save(targetp)
 x0,y0,x1,y1=rect;hh=y1-y0;ww=x1-x0
 yy,xx=np.indices((hh,ww))
 # No left feather at fixed-core boundary; top, right and bottom 24px inward taper.
 fade=np.minimum.reduce([np.ones((hh,ww)),yy/24,(hh-1-yy)/24,(ww-1-xx)/24])
 alpha=np.rint(np.clip(fade,0,1)*255).astype("uint8")
 ap=p/"alpha-crop.png";Image.fromarray(alpha).save(ap)
 full=np.zeros((1254,1254),np.uint8);full[y0:y1,x0:x1]=alpha
 af=p/"alpha-native-1254.png";Image.fromarray(full).save(af)
 mask=np.zeros((1254,1254),np.uint8);mask[y0:y1,x0:x1]=255
 maskp=p/"edit-mask-native-1254.png";Image.fromarray(mask).save(maskp)
 prompt=("Use case: precise-object-edit.\n"
 "Output exactly one native opaque 1254 x 1254 RGB PNG, with precisely the framing and object scale of image 1.\n"
 "Image 1 is the edit target; ONLY its magenta rectangle is editable. Image 2 is the exact unmarked true-core join at the same native pixel coordinates. Image x0..639 comes from the immutable western neighbor core; x640..1253 comes from the current child core. Do not rescale, rotate or move either side. The seam to repair is x640.\n"
 +local+"\n"
 "Match the existing warm daylight, fine hand-painted natural pale gray stone texture and leaf-shadow softness locally. Keep all x<640 absolutely unchanged. Keep all non-magenta pixels, fixed endpoints, approved object silhouettes and paving scale unchanged. Do not add ornaments, new objects, extra stone borders, blue bands, text or watermarks. No global recolor, contrast adjustment, blur or glow. Rebuild real line and material continuity inside magenta, rather than hiding a cut with a shadow. Remove all magenta in the final output.\n")
 pp=p/"prompt.txt";pp.write_text(prompt,encoding="utf-8")
 req={"schemaVersion":1,"tile":"r14_c15","version":D.name+"-"+code,"status":"offline_prepared_not_generated","tool":"image_gen.imagegen","route":"builtin","actualModel":None,"actualQuality":None,"modelPreference":"Prefer 2.5 if available through free/existing included route; otherwise existing builtin 2.0 permitted. Unknown actual metadata stays null. No paid API.","submittedParameters":{"prompt":prompt,"referenced_image_paths":[str(targetp),w["path"]],"transparent_background":False}}
 rq=p/"request.json";rq.write_text(json.dumps(req,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 childbox=[x0-640,w["originY"]+y0,x1-640,w["originY"]+y1]
 prep={"schemaVersion":1,"tile":"r14_c15","version":D.name+"-"+code,"preparedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"offline_prepared_not_generated","ruleFilesReadInFull":[info(r) for r in rules],"sourceCandidate":i["child"],"sourceContext":i["childContext"],"sourceManifest":i["childManifest"],"immutableWestCore":i["west"],"referencePixelSources":[{"source":"immutableWestCore","sourceBox":w["westernCoreBox"],"targetBox":[0,0,640,1254],"editable":False},{"source":"sourceCandidate","sourceBox":w["childCoreBox"],"targetBox":[640,0,1254,1254],"editable":"saved magenta rectangle only"}],"target":info(targetp),"references":[info(targetp),info(w["path"])],"unmarkedReference":info(w["path"]),"defectId":code,"nativeCrop":rect,"pasteBoxIn4096":childbox,"savedMask":info(maskp),"alpha":info(ap),"fullAlpha":info(af),"alphaRule":"24px inward linear taper at top/bottom/right; fixed western boundary x640 has no left taper. Alpha is 255 through interior. No neighbor pixels may be adopted or modified.","blendArithmetic":"(old*(255-alpha)+new*alpha+127)//255 uint32","currentBaseMustMatch":i["child"]["sha256"],"sequentialAdoptionRule":"All three preparations share base 5ce and have disjoint alpha support. Combine sequentially only after asserting the current pixels under this job alpha support remain identical to 5ce; carry all prior adopted pixels outside this support unchanged.","targetGeometry":"1254x1254 original-size true core join; no halo pixels","RGBColorCorrection":False,"resampling":False,"networkCallMade":False,"actualModel":None,"actualQuality":None,"prompt":info(pp),"request":info(rq),"formalAccepted":False,"qaRequired":["fixed western true-core line x640 across complete mask height","top/right/bottom alpha boundaries at 1:1","all intended grout endpoints with no blind groove","outside saved alpha and west core pixel exactness","local cropped internal seam segments affected by this repair","W04 material continuity remains separate until full west join reviewed"]}
 pr=p/"preparation.json";pr.write_text(json.dumps(prep,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 out.append({"id":code,"request":info(rq),"preparation":info(pr),"target":info(targetp),"reference":info(w["path"]),"mask":info(maskp),"alpha":info(ap),"nativeCrop":rect,"pasteBoxIn4096":childbox,"networkCallMade":False})
 # Save fixed-boundary closeup as diagnostic, not a generation input or art source.
 ref.crop((512,max(0,y0-48),min(1254,x1+48),min(1254,y1+48))).save(p/"boundary-detail-100pct.png")
for a in out:
 for b in out:
  if a["id"]<b["id"]:
   aa=a["pasteBoxIn4096"];bb=b["pasteBoxIn4096"];assert aa[3]<=bb[1] or bb[3]<=aa[1]
manifest={"schemaVersion":1,"tile":"r14_c15","version":D.name,"preparedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"sourceCandidate":i["child"],"immutableWestCore":i["west"],"jobs":out,"status":"three_offline_requests_ready_for_root_view_and_builtin","actualNewOutputs":0,"formalAccepted":False,"sourcePublishedFilesUnmodified":True}
mp=D/"ready-requests.json";mp.write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"manifest":info(mp),"jobs":out}))
