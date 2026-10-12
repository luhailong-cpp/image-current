import sys,json,hashlib,datetime
from pathlib import Path
from PIL import Image
r=Path("D:/work/image/designs/creature-combat-20261005/pets/04-guideng")
data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
source=Path(data["source"])
im=Image.open(source)
native={"width":im.width,"height":im.height,"format":im.format,"mode":im.mode}
source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
n=f'{data["num"]:02d}'
out=r/"runtime"/data["action"]/"E"/(n+".png")
rgba=im.convert("RGBA")
if rgba.size!=(1024,1024): rgba=rgba.resize((1024,1024),Image.Resampling.LANCZOS)
rgba.save(out)
a=rgba.getchannel("A")
record={"file":str(out),"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"generatedAt":data["start"],"savedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"width":1024,"height":1024,"format":"PNG","mode":"RGBA","native":native,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":data["refs"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露／无可核实元数据","evidence":{"rawToolResultText":data["output_hint"]},"prompt":str(r/"prompts"/("E-"+data["action"])/(n+".txt")),"references":[{"path":p,"purpose":["E身份与持物","W身份背部结构","主要画法材质","上一帧连续性"][min(i,3)]} for i,p in enumerate(data["refs"])],"derivedFrom":{"file":str(source),"sha256":source_sha,"native":native},"operation":"full-canvas uniform LANCZOS resize to 1024x1024; no cropping, alignment, mirroring, synthesis or interpolation" if native["width"]!=1024 or native["height"]!=1024 else "RGBA PNG export; no geometric transformation","alpha":{"min":a.getextrema()[0],"max":a.getextrema()[1],"bbox":a.getbbox()},"visualReview":{"viewed":True,"status":"reviewed-single-frame","notes":data["review"]}}
(r/"records"/("E-"+data["action"])/(n+".generation.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(out),"sha256":record["sha256"],"native":native,"alpha":record["alpha"]},ensure_ascii=False))

