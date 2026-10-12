from pathlib import Path
import json,hashlib,sys
from PIL import Image
ROOT=Path(r"D:/work/image/designs/creature-combat-20261005/pets/02-jiangling")
a,f,source=sys.argv[1:4]
suffix=sys.argv[4] if len(sys.argv)>4 else ''
source=Path(source); dest=ROOT/"runtime"/a/"W"/(f+".png")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw_sha=sha(source)
im=Image.open(source); native={"width":im.width,"height":im.height,"format":im.format,"mode":im.mode,"sha256":raw_sha}
if im.width!=im.height: raise RuntimeError("Unexpected non-square native dimensions")
if im.mode!="RGBA": raise RuntimeError("No native RGBA")
if im.getchannel("A").getextrema()[0]!=0: raise RuntimeError("No genuine transparency")
im.resize((1024,1024),Image.Resampling.LANCZOS).save(dest)
receipt=ROOT/"receipts"/(a+"-W-"+f+suffix+".json")
r=json.loads(receipt.read_text(encoding="utf-8"))
rec={"file":dest.relative_to(ROOT).as_posix(),"sha256":sha(dest),"generatedAt":r["completedAt"],"native":native,"width":1024,"height":1024,"format":"PNG","mode":"RGBA","route":"builtin","tool":"image_gen.imagegen","configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":r["refs"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露 model/quality，无可核实模型元数据。","prompt":"prompts/"+a+"-W-"+f+".txt","references":[{"path":p,"role":("primary W identity camera scale" if i==0 else "E identity detail only" if i==1 else "approved style and material" if i==2 else "previous approved W animation frame")} for i,p in enumerate(r["refs"])],"evidence":{"receipt":receipt.relative_to(ROOT).as_posix(),"toolFields":["image_url","output_hint"]},"derivedFrom":{"path":str(source),"sha256":raw_sha,"retainedAsFinal":False},"operation":{"kind":"uniform_full_canvas_resize","input":[im.width,im.height],"output":[1024,1024],"scale":[1024/im.width,1024/im.height],"resampler":"Lanczos","translation":[0,0],"perFrameFootAlignment":False},"visualStatus":"viewed_native; exported review pending","direction":"W","action":a,"frame":int(f),"durationMs":{"hit":40,"attack":30,"cast":45}[a],"pivot":[0.5,0.08],"event":({"hit":3,"attack":7,"cast":10}[a]==int(f) and {"hit":"impact","attack":"attack","cast":"cast"}[a]) or None}
rec['prompt']='prompts/'+a+'-W-'+f+suffix+'.txt'
(ROOT/"records"/(a+"-W-"+f+".json")).write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
Path(str(dest)+".generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(dest),"native":native,"sha256":rec["sha256"],"alpha":im.getchannel("A").getextrema()}))
