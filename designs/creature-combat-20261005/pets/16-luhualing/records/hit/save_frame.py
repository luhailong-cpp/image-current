from pathlib import Path
from PIL import Image
import json, hashlib, shutil, sys
from datetime import datetime, timezone
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/16-luhualing")
direction, num, src=sys.argv[1:]
name=direction+num
out=base/".work"/"hit"/direction/(num+".png")
out.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(src,out)
im=Image.open(out)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
refpaths=[
("D:/work/image/designs/pets-xianling-20260924/source/16-luhualing-E.png","original E identity"),
("D:/work/image/designs/pets-xianling-20260924/source/16-luhualing-W.png","original W identity"),
("D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png","primary painted style/material")]
record={
"file":"runtime/hit/"+direction+"/"+num+".png",
"generatedAt":datetime.now(timezone.utc).isoformat(),
"nativeFile":str(out.relative_to(base)).replace(chr(92),"/"),
"nativeSHA256":sha(out),
"nativeWidth":im.width,"nativeHeight":im.height,"format":"PNG","mode":im.mode,
"tool":"image_gen.imagegen","route":"builtin",
"configSnapshot":json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),
"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":[p for p,r in refpaths]},
"actualModel":None,"actualQuality":None,
"unverifiedReason":"Host-managed: builtin tool exposes no model/quality selectors and returned no model/quality metadata.",
"prompt":"prompts/hit/"+name+".txt",
"references":[{"path":p,"role":r,"sha256":sha(p)} for p,r in refpaths],
"evidence":{"receipt":"records/hit/"+name+".receipt.json","imageDataURL":"Returned image_url data:PNG bytes saved in nativeFile; no duplicated base64 in textual receipt."},
"durationMs":40,"pivot":[0.5,0.08],"anchor":[512,942],
"visualReview":{"status":"reviewed-single-frame","dynamicReview":"pending-root"},
"exportStatus":"pending root common transform; no per-frame alignment"}
dest=base/"records"/"hit"/direction/(num+".generation.json")
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(out),"size":im.size,"mode":im.mode,"sha256":sha(out)},ensure_ascii=False))
