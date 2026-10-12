from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone
ROOT=Path("D:/work/image/designs/creature-combat-20261005/pets/14-feierling")
G=ROOT/"generation/cast/W"
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=Path(sys.argv[1])
native=G/"14.native.png"
target=ROOT/"runtime/cast/W/14.png"
shutil.copyfile(source,native)
t=json.loads((ROOT/"EXPORT_TRANSFORMS.json").read_text(encoding="utf-8"))["directions"]["W"]
assert t["resizedCanvas"]==[853,853] and t["offset"]==[50,126]
with Image.open(native) as im:
 assert im.size==(1254,1254) and im.mode=="RGBA"
 native128=im.getchannel("A").point(lambda v:255 if v>=128 else 0).getbbox()
 out=Image.new("RGBA",(1024,1024))
 out.paste(im.resize(tuple(t["resizedCanvas"]),Image.Resampling.LANCZOS),tuple(t["offset"]))
 out.save(target)
 a=out.getchannel("A");hist=a.histogram()
r=json.loads((G/"14.rejected-size.generation.json").read_text(encoding="utf-8"))
rejected=dict(r)
rejected["status"]="rejected-size"
rejected["rejectionReason"]="No-glow revision enlarged head/body roughly 10% relative to cast W13/W16; replaced by fresh AI pose edit of W16."
rejected["prompt"]="generation/cast/W/14.rejected-size.prompt.txt"
rejected["file"]=None
rejected["runtimeOverwriteNote"]="Prior runtime W14 superseded; historical sha256 retained."
(G/"14.rejected-size.generation.json").write_text(json.dumps(rejected,ensure_ascii=False,indent=2),encoding="utf-8")
(G/"14.rejected-size.receipt.json").write_text(json.dumps(rejected.get("evidence",{}),ensure_ascii=False,indent=2),encoding="utf-8")
receipt=json.loads((G/"14.receipt.json").read_text(encoding="utf-8"))
shutil.copyfile(G/"14.repair-size.prompt.txt",G/"14.prompt.txt")
r.update(generatedAt=receipt["returnedAt"],startedAt=receipt["startedAt"],file=target.relative_to(ROOT).as_posix(),sha256=sha(target),width=1024,height=1024,mode="RGBA",format="PNG",actualModel=None,actualQuality=None,unverifiedReason="宿主管理，工具未披露型号/质量，无可核实元数据",nativeFile=str(native),nativeSavedPath=str(native),prompt="generation/cast/W/14.prompt.txt",supersedes="generation/cast/W/14.rejected-size.generation.json",repairReason="Match W16 head/body/foot pixel scale and positions with only anatomical RIGHT hand tucked closer to torso; no glow.")
r["submittedParameters"]={"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":receipt["referenced_image_paths"]}
roles=["identity-E","identity-W-authoritative-direction","PRIMARY-approved-style-materials","W16-native-authoritative-scale-composition-and-foot-anchor"]
r["references"]=[{"file":p,"role":role,"sha256":sha(p)} for p,role in zip(receipt["referenced_image_paths"],roles)]
r["native"]={"file":str(native),"sha256":sha(native),"width":1254,"height":1254,"mode":"RGBA","format":"PNG","alpha128BBox":native128}
r["evidence"]={"returnKeys":["image_url","output_hint"],"output_hint":receipt["output_hint"],"returnedSourcePath":str(source),"receipt":"generation/cast/W/14.receipt.json","image_url":"Returned data URL omitted from textual receipt; saved native image SHA recorded."}
r["operation"]={"type":"fixed-direction-export",**t}
r["derivedFrom"]={"sha256":sha(native),"nativeFile":str(native),"operation":r["operation"]}
anchor=Path(receipt["referenced_image_paths"][3])
r["editedFrom"]={"file":str(anchor),"sha256":sha(anchor),"generationRecord":"generation/cast/W/16.generation.json"}
r["alpha"]={"extrema":a.getextrema(),"bbox":a.getbbox(),"transparentPixels":hist[0],"partialPixels":sum(hist[1:255]),"opaquePixels":hist[255]}
r["finalExportAt"]=datetime.now(timezone.utc).isoformat()
r.pop("preFinalExport",None)
r["visualStatus"]="size-repair-native-individually-viewed; parent-final-playback-pending"
r["visualReview"]={"method":"Viewed W13/W14-old/W16 native with view_image; final native displayed by imagegen and compared to W16.","identity":"copper-red fox boy; two ears; exactly one screen-right black-tip tail","direction":"true three-quarter rear upper-left","ownership":"anatomical LEFT wooden mask, anatomical RIGHT empty seal tucked closer than W16","glow":"none","scale":"head and boot sizes and locations visually closely match native W16","clientVerified":False,"groupPlayback":"parent final QA pending"}
(G/"14.generation.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
with Image.open(anchor) as im:
 anchor128=im.getchannel("A").point(lambda v:255 if v>=128 else 0).getbbox()
print(json.dumps({"file":str(target),"sha256":r["sha256"],"nativeSHA":sha(native),"nativeAlpha128BBox":native128,"anchorW16Alpha128BBox":anchor128,"exportSize":[1024,1024],"alphaExtrema":a.getextrema(),"transform":t}))

