from pathlib import Path
import sys,json,hashlib,datetime
from PIL import Image
BASE=Path(r"D:/work/image/designs/creature-combat-20261005/pets/05-yanyuling")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt=Path(sys.argv[1]); data=json.loads(receipt.read_text(encoding="utf-8"))
src=Path(data["sourcePath"]); direction,num=data["id"].split("/")
out=BASE/"runtime"/"attack"/direction/(num+".png");out.parent.mkdir(parents=True,exist_ok=True)
with Image.open(src) as im:
    native={"width":im.width,"height":im.height,"format":im.format,"mode":im.mode,"sha256":sha(src)}
    rgba=im.convert("RGBA")
    if rgba.size!=(1024,1024): rgba=rgba.resize((1024,1024),Image.Resampling.LANCZOS)
    rgba.save(out)
    alpha=rgba.getchannel("A")
    bounds=alpha.getbbox()
refs=[{"path":p,"sha256":sha(p),"role":role} for p,role in zip(data["references"],["E original identity","W original identity","main painting/material style","same direction framing / previous accepted frame"])]
rec={"file":str(out),"action":"attack","direction":direction,"frame":int(num),"durationMs":30,"pivot":[0.5,0.08],"targetFootPoint":[512,942],"generatedAt":data["completedAt"],"generationStartedAt":data["startedAt"],"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":data["references"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"Host managed; tool exposes no model/quality selectors and returned no verifiable model/quality metadata.","evidence":{"receipt":str(receipt),"disclosedFields":["output_hint"]},"prompt":str(BASE/"provenance"/"attack"/direction/(num+".prompt.txt")),"references":refs,"native":native,"nativeSourcePath":str(src),"export":{"width":1024,"height":1024,"format":"PNG","mode":"RGBA","sha256":sha(out),"alphaExtrema":alpha.getextrema(),"alphaBounds":bounds},"derivedFrom":{"path":str(src),"sha256":native["sha256"]},"operation":"Whole-canvas RGBA PNG export; uniform 1024 square resize only if needed. No frame alignment, mirroring, interpolation or pose synthesis.","visualReview":{"status":"viewed","notes":data.get("review","Generated frame visually inspected; identity, two wings/two feet, accessory sides and direction reviewed.")},"runtimeIntegration":"not tested"}
out.with_suffix(".png.generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"frame":str(out),"native":native,"export":rec["export"]},ensure_ascii=False))

