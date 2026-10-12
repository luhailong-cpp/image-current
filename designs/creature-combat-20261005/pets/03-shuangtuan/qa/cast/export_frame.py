from pathlib import Path
from PIL import Image
import json, hashlib, shutil, sys
BASE=Path(__file__).resolve().parents[2]
d,n,src,meta_path=sys.argv[1:]
num=f"{int(n):02d}"
meta=json.loads(Path(meta_path).read_text(encoding="utf-8-sig"))
runtime=BASE/"runtime"/"cast"/d/f"{num}.png"
source=BASE/"source"/"cast"/d/f"{num}.png"
record=BASE/"records"/"cast"/d/f"{num}.generation.json"
for p in (runtime,source,record): p.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(src,source)
im=Image.open(source)
native={"width":im.width,"height":im.height,"format":im.format,"mode":im.mode}
assert im.width==im.height
assert im.mode=="RGBA",im.mode
alpha=im.getchannel("A")
assert alpha.getextrema()[0]==0,alpha.getextrema()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_sha=sha(source)
if im.size!=(1024,1024): im.resize((1024,1024),Image.Resampling.LANCZOS).save(runtime)
else: shutil.copyfile(source,runtime)
record_data={
"file":runtime.relative_to(BASE).as_posix(),"sha256":sha(runtime),
"generatedAt":meta["endedAt"],"width":1024,"height":1024,"format":"PNG",
"tool":"image_gen.imagegen","route":"builtin",
"configSnapshot":json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),
"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":meta["references"]},
"actualModel":None,"actualQuality":None,
"unverifiedReason":"宿主管理，工具未披露 model/quality，无可核实元数据。提示词质量目标不等于实际选择器。",
"prompt":f"prompts/cast/{d}/{num}.txt",
"references":[{"path":p,"purpose":("E identity" if "03-shuangtuan-E" in p else "W identity" if "03-shuangtuan-W" in p else "primary approved painting and material style" if "attribute-panels" in p else "cast sequence framing and continuity reference")} for p in meta["references"]],
"evidence":{"receipt":Path(meta_path).relative_to(BASE).as_posix(),"returnedFields":["image_url","output_hint"],"output_hint":meta["output_hint"]},
"native":native,
"derivedFrom":{"file":source.relative_to(BASE).as_posix(),"sha256":source_sha,"generationRecord":record.relative_to(BASE).as_posix(),"deleted":False},
"operation":"uniform whole-canvas resize from native square to 1024x1024 using Lanczos; no translation, crop, flip, interpolation, foot alignment or synthesized pose",
"direction":d,"action":"cast","frame":int(n),"durationMs":45,"pivot":[0.5,0.08],
"event":"cast-release" if int(n)==11 else None,
"visualStatus":"individually viewed; sequence review pending"
}
record.write_text(json.dumps(record_data,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(runtime),"native":native,"sha256":record_data["sha256"],"alpha":Image.open(runtime).getchannel("A").getextrema()},ensure_ascii=False))

