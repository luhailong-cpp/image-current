from pathlib import Path
from PIL import Image
import json,hashlib,datetime,sys
ROOT=Path(r"D:/work/image/designs/creature-combat-20261005/pets/legacy-ling-yue")
j=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
raw=Path(j["raw"]); dst=ROOT/j["output"]; dst.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(raw).convert("RGBA")
native=list(im.size); sourcehash=hashlib.sha256(raw.read_bytes()).hexdigest()
if native!=[1254,1254]: raise ValueError("Unexpected native canvas; do not adapt per frame: "+str(native))
out=im.resize((1024,1024),Image.Resampling.LANCZOS);out.save(dst)
record={
"file":str(dst.relative_to(ROOT)).replace("\\","/"),"sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),"generatedAt":j["generatedAt"],
"width":1024,"height":1024,"format":"PNG","mode":"RGBA","nativeWidth":native[0],"nativeHeight":native[1],
"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),
"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":j["references"]},
"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未开放model/quality选择器且未披露可核实模型/质量元数据。",
"evidence":{"receipt":j["receipt"],"output_hint":j["output_hint"]},"prompt":j["prompt"],"references":j["references"],
"derivedFrom":{"path":str(raw),"sha256":sourcehash,"nativeWidth":native[0],"nativeHeight":native[1],"model":None,"quality":None},
"operation":{"type":"uniform_full_canvas_resize","source":[1254,1254],"target":[1024,1024],"filter":"LANCZOS","translation":[0,0],"perFrameFootAlignment":False},
"visualReview":j.get("visualReview","pending"),"alphaExtrema":out.getchannel("A").getextrema(),
"rawAlphaBBox":im.getchannel("A").getbbox(),"exportAlphaBBox":out.getchannel("A").getbbox()
}
Path(str(dst)+".generation.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
(ROOT/j["receipt"]).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":record["file"],"sha256":record["sha256"],"native":native,"alpha":record["alphaExtrema"]}))

