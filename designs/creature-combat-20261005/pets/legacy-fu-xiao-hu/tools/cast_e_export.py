import sys,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
n=int(sys.argv[1]); tag=f"cast-E-{n:02d}"
req=json.loads((BASE/"records"/f"{tag}.request.json").read_text(encoding="utf-8-sig"))
receipt=json.loads((BASE/"records"/f"{tag}.receipt.json").read_text(encoding="utf-8-sig"))
src=Path(receipt["sourcePath"])
reference_sha_before={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in req["request"]["referenced_image_paths"]}
native=BASE/"runtime"/"cast"/"E"/".native"/f"{n:02d}.png"; native.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(src,native)
im=Image.open(native); orig_size=list(im.size); orig_mode=im.mode
out=BASE/"runtime"/"cast"/"E"/f"{n:02d}.png"
im.convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS).save(out)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
final=Image.open(out);alpha=final.getchannel("A")
references=[]
for i,p in enumerate(req["request"]["referenced_image_paths"]):
    references.append({"path":p,"role":["original identity","approved painted style","locked E-facing camera and seated support","previous animation frame or targeted edit source","matched-pose seated support reference"][i],"sha256":reference_sha_before[p]})
record={
"file":out.relative_to(BASE).as_posix(),"sha256":sha(out),"generatedAt":receipt["receivedAt"],"action":"cast","direction":"E","frame":n,"durationMs":45,
"tool":"image_gen.imagegen","route":"builtin","configSnapshot":req["configSnapshot"],
"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":req["request"]["referenced_image_paths"]},
"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未开放 model/quality 参数，结果未披露且无可核实型号/质量元数据。",
"native":{"path":native.relative_to(BASE).as_posix(),"originalHostPath":str(src),"sha256":sha(native),"width":orig_size[0],"height":orig_size[1],"format":"PNG","mode":orig_mode},
"evidence":{"receipt":f"records/{tag}.receipt.json","returnedFields":["image_url","output_hint"],"modelDisclosed":False,"qualityDisclosed":False},
"prompt":f"records/{tag}.request.json","references":references,
"derivedFrom":{"path":native.relative_to(BASE).as_posix(),"sha256":sha(native)},
"operation":{"type":"uniform-full-canvas-resize","sourceSize":orig_size,"targetSize":[1024,1024],"filter":"Pillow LANCZOS","translation":[0,0],"crop":None,"perFrameFootAlignment":False},
"technical":{"width":1024,"height":1024,"mode":final.mode,"alphaExtrema":list(alpha.getextrema()),"alphaBBox":list(alpha.getbbox()),"uniquePixelSHA256":hashlib.sha256(final.tobytes()).hexdigest()},
"visualStatus":"generated frame individually inspected; sequence review pending","sourceRetention":"native kept temporarily until sequence final references verified"
}
(BASE/"records"/f"{tag}.generation.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"frame":n,"output":str(out),"nativeSize":orig_size,"sha256":record["sha256"],"alpha":record["technical"]},ensure_ascii=False))
