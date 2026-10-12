from pathlib import Path
from PIL import Image
import json, hashlib, shutil, sys, datetime
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/16-luhualing")
direction, num, source, started, ended = sys.argv[1:6]
dst=root/".work"/"attack"/direction/(num+".png")
dst.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,dst)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.open(dst)
refs=[(r"D:/work/image/designs/pets-xianling-20260924/source/16-luhualing-E.png","original E identity"),(r"D:/work/image/designs/pets-xianling-20260924/source/16-luhualing-W.png","original W identity/rear anatomy"),(r"D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png","main confirmed painting and material style")]
record={"file":f"runtime/attack/{direction}/{num}.png","sourceFile":str(dst.relative_to(root)).replace(chr(92),"/"),"sourceSha256":sha(dst),"generatedAt":ended,"generationStartedAt":started,"width":im.width,"height":im.height,"format":"PNG","mode":im.mode,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":[p for p,r in refs]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露model/quality选择器和实际版本质量","prompt":f"prompts/attack/{direction}{num}.txt","references":[{"path":p,"role":r,"sha256":sha(p)} for p,r in refs],"evidence":{"receipt":f"records/attack/{direction}{num}.receipt.json","originalGeneratedPath":source},"durationMs":30,"pivot":[0.5,0.08],"anchor":[512,942],"event":"release" if num=="07" else None,"visualStatus":"individual_frame_reviewed; dynamic_review_pending","alphaExtrema":list(im.getchannel("A").getextrema()) if "A" in im.getbands() else None,"exportStatus":"awaiting_direction_uniform_export"}
recdir=root/"records"/"attack"/direction
recdir.mkdir(parents=True,exist_ok=True)
(recdir/(num+".generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(dst),"size":im.size,"mode":im.mode,"sha256":sha(dst),"alphaExtrema":record["alphaExtrema"]}))

