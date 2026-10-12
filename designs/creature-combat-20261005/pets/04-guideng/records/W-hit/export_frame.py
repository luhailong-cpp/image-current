import json,sys,hashlib,os
from pathlib import Path
from PIL import Image
p=Path(sys.argv[1])
r=json.loads(p.read_text(encoding="utf-8"))
src=Path(r["sourceNativePath"])
dst=Path(r["file"])
dst.parent.mkdir(parents=True,exist_ok=True)
im=Image.open(src)
r["native"]={"width":im.width,"height":im.height,"mode":im.mode,"format":im.format,"sha256":hashlib.sha256(src.read_bytes()).hexdigest()}
if im.mode!="RGBA": raise RuntimeError("Native lacks RGBA")
a=im.getchannel("A")
if a.getextrema()!=(0,255): raise RuntimeError("Unexpected native alpha")
if im.size!=(1024,1024):
    im=im.resize((1024,1024),Image.Resampling.LANCZOS)
    r["operation"]={"type":"uniform-full-canvas-resize","sourceSize":[r["native"]["width"],r["native"]["height"]],"outputSize":[1024,1024],"resampling":"Lanczos","crop":None,"translation":None}
else:r["operation"]={"type":"native-copy"}
im.save(dst)
r["sha256"]=hashlib.sha256(dst.read_bytes()).hexdigest()
r["width"]=im.width
r["height"]=im.height
r["alphaExtrema"]=im.getchannel("A").getextrema()
r["alphaBounds"]=im.getchannel("A").getbbox()
r["format"]="PNG"
r["visualReview"]={"status":"inspected-single-frame","notes":"W rear view, rear waist bow, two rear soles, right lantern and left osmanthus visible; no cropping."}
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"file":str(dst),"native":r["native"],"sha256":r["sha256"],"alphaBounds":r["alphaBounds"]},ensure_ascii=False))

