from pathlib import Path
import json, hashlib, shutil, sys
from PIL import Image
ROOT=Path(r"D:/work/image/designs/creature-combat-20261005/pets/05-yanyuling")
P=ROOT/"provenance/cast/E"
n=sys.argv[1]
receipt=json.loads((P/(n+".receipt.json")).read_text("utf-8"))
src=Path(receipt["nativePath"])
out=ROOT/"runtime/cast/E"/(n+".png")
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
native_sha=sha(src)
im=Image.open(src); im.load()
native={"path":str(src),"sha256":native_sha,"width":im.width,"height":im.height,"mode":im.mode,"format":im.format}
out.parent.mkdir(parents=True,exist_ok=True)
im.convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS).save(out)
refs=[{"path":v,"sha256":sha(Path(v))} for v in receipt["referencePaths"]]
final=Image.open(out)
a=final.getchannel("A")
record={"file":str(out),"sha256":sha(out),"generatedAt":receipt["completedAt"],"tool":"image_gen.imagegen","route":"builtin","native":native,"export":{"width":1024,"height":1024,"format":"PNG","mode":final.mode,"alphaExtrema":a.getextrema(),"alphaBBox":a.getbbox(),"operation":"uniform whole canvas resize to 1024x1024, no crop or alignment"},"configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text("utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":receipt["referencePaths"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"Host-managed; builtin tool has no model/quality selector and returned no verified model/quality metadata.","evidence":{"receipt":str(P/(n+".receipt.json"))},"prompt":str(P/(n+".prompt.txt")),"references":refs,"visualReview":{"status":"individual frame visually inspected","note":receipt["visualNote"]},"cleanup":{"nativeCacheDeleted":False}}
# User retention rule allows deletion once final exists and image opens; this is one known tool-produced file, never recursive.
if final.size==(1024,1024) and out.exists():
    src.unlink()
    record["cleanup"]["nativeCacheDeleted"]=True
(P/(n+".generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2),"utf-8")
print(json.dumps({"frame":n,"sha256":record["sha256"],"native":native,"alphaBBox":a.getbbox(),"alphaExtrema":a.getextrema()},ensure_ascii=False))

