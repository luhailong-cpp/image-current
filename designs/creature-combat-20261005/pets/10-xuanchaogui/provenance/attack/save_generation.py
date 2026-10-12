from pathlib import Path
from PIL import Image
import sys,json,hashlib,datetime
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/10-xuanchaogui")
job=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
src=Path(job["source"])
out=base/"runtime"/"attack"/job["direction"]/(job["frame"]+".png")
out.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(src); native={"width":im.width,"height":im.height,"mode":im.mode,"format":im.format}
source_sha=hashlib.sha256(src.read_bytes()).hexdigest()
rgba=im.convert("RGBA")
if rgba.size!=(1024,1024): rgba=rgba.resize((1024,1024),Image.Resampling.LANCZOS)
rgba.save(out)
alpha=rgba.getchannel("A")
record={**job,"file":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"native":native,"width":1024,"height":1024,"format":"PNG","mode":"RGBA","alphaExtrema":alpha.getextrema(),"alphaBbox":alpha.getbbox(),"generatedAt":job["completedAt"],"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":job["references"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具无model/quality选择器且返回未披露。","derivedFrom":{"path":str(src),"sha256":source_sha},"operation":{"name":"uniform full-canvas resize","inputSize":[im.width,im.height],"outputSize":[1024,1024],"filter":"Lanczos","translation":[0,0],"bboxAutoAlignment":False},"durationMs":30,"pivot":[0.5,0.08],"event":"impact" if job["frame"]=="07" else None}
p=base/"provenance"/"attack"/job["direction"]/(job["frame"]+".generation.json")
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(out),"sha256":record["sha256"],"native":native,"alpha":record["alphaExtrema"],"bbox":record["alphaBbox"]},ensure_ascii=False))

