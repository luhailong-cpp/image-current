import json,hashlib,datetime
from pathlib import Path
import numpy as np
from PIL import Image
q=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c15");s=q.parent
version="north-board-joint-20261012-v1";d=q/"repairs"/version
assert not d.exists();d.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=q/"repairs/single-stone-railing-bottom-20261012-v3/candidate-4096.png"
north=s/"r13_c15/candidate/r13_c15-4k-unified-native-repairs-20261012T121123.png"
assert sha(base)=="3f0ba6b330136574a1ea9508d2a213fc9b66a5a42c95c737ee0820a6cb0798a9"
assert sha(north)=="173e67ac86c37595dd6ad272757093367dab48585f73c8192c832fcf3f42110f"
b=Image.open(base).convert("RGB");n=Image.open(north).convert("RGB")
ref=Image.new("RGB",(1254,1254));ref.paste(n.crop((0,3456,1254,4096)),(0,0));ref.paste(b.crop((0,0,1254,614)),(0,640))
clean=d/"reference-core-join-native-1254.png";ref.save(clean)
target=ref.copy();target.paste((255,0,255),(194,640,270,750));tp=d/"edit-target-native-1254.png";target.save(tp)
aa=np.zeros((1254,1254),dtype=np.uint8)
for y in range(640,750):
 for x in range(194,270):
  f=min(1,(x-194)/8,(269-x)/8,(749-y)/12)
  aa[y,x]=round(255*max(0,f))
ap=d/"alpha-native-1254.png";Image.fromarray(aa).save(ap)
Image.fromarray(aa[640:750,194:270]).save(d/"alpha-crop.png")
prompt="""Use case: precise-object-edit.
Output one native 1254 x 1254 RGB image, exactly the same framing and scale as image 1.
Image 1 is the edit target. Magenta marks the only editable area. Image 2 is the exact unmarked true-core join at the same pixel coordinates; it shows the existing material and the error clearly. This is a tiny continuity repair to the existing stylized golden wooden platform, not a redesign.
At image x about 230, the narrow dark vertical end-joint of a wooden deck board descends through the upper half and stops unnaturally at y=640, the tile boundary. Continue this SAME narrow joint straight into the magenta child-side area, matching its exact width, darkness, highlighted bevel, alignment and wood plane. It must meet and terminate naturally at the existing diagonal board seam below, around y=700. Preserve that diagonal seam and its highlight. Reconstruct only the surrounding tiny patch of golden wood grain.
All pixels at y<640 depict the immutable northern true core. Do not move, erase, retexture, recolor or change them. Do not shift either side, the platform edge, the board widths, lighting, wood knots, or surrounding grain. Outside the magenta patch preserve the reference exactly. No extra parallel groove, duplicated bevel, new plank, object, text, border, blur or glow. Remove all magenta in the final output.
"""
pp=d/"prompt.txt";pp.write_text(prompt,encoding="utf-8")
params={"prompt":prompt,"referenced_image_paths":[str(tp),str(clean)],"transparent_background":False}
req={"schemaVersion":1,"tile":"r14_c15","version":version,"status":"offline_prepared_not_generated","route":"builtin","tool":"image_gen.imagegen","submittedParameters":params,"actualModel":None,"actualQuality":None}
(d/"request.json").write_text(json.dumps(req,indent=2)+"\n")
info=lambda p:{"path":str(p),"sha256":sha(p)}
prep={"schemaVersion":1,"tile":"r14_c15","version":version,"preparedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"offline_prepared_not_generated","baseCandidate":info(base),"northCore":info(north),"target":info(tp),"unmarkedReference":info(clean),"referencePixelSources":[{"source":"northCore","sourceBox":[0,3456,1254,4096],"targetBox":[0,0,1254,640],"editable":False},{"source":"baseCandidate","sourceBox":[0,0,1254,614],"targetBox":[0,640,1254,1254],"editable":"only saved mask"}],"maskBoxInTarget":[194,640,270,750],"nativeCrop":[194,640,270,750],"pasteBoxIn4096":[194,0,270,110],"alpha":info(d/"alpha-crop.png"),"fullAlpha":info(ap),"prompt":info(pp),"request":info(d/"request.json"),"blendArithmetic":"(old*(255-alpha)+new*alpha+127)//255 uint32","compositionMustPreserve":"all north core, all child pixels outside saved alpha; no resize or RGB color correction","QARequired":["fixed core boundary y0 at x194..270","vertical groove joins existing diagonal board seam","three child-side mask edges at original pixel size"],"formalAccepted":False}
(d/"preparation.json").write_text(json.dumps(prep,indent=2)+"\n")
print(json.dumps({"version":version,"request":info(d/"request.json"),"preparation":info(d/"preparation.json"),"target":info(tp)}))
