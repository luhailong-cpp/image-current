"""Explicit raw-native patch seams: both minimum-error and true core cut, no edits."""
import argparse,hashlib,json,runpy
from pathlib import Path
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument("--stem",required=True);a=p.parse_args()
assert a.stem.startswith("r03_c04_")
out=Path(__file__).resolve().parent/a.stem;out.mkdir(exist_ok=False)
M=runpy.run_path(str(Z/"assemble_tile.py"),run_name="raw_patch_qa")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(stem):
    f=Z/"native"/(stem+".png")
    return M["load_raw_source"](f,Path(str(f)+".generation.json"),stem[:7],int(stem[9:11])-1,int(stem[12:14])-1)
s,b=load(a.stem)
inp=Z/"guides"/(a.stem+".input.json");meta=json.loads(inp.read_text(encoding="utf-8-sig"))
assert meta["globalBox"]==s["globalNativeBox"]
results=[]
for n in meta["neighbor"]:
    d=n["direction"]
    assert d in ("left","top")
    ns,na=load(n["stem"]); assert ns["globalNativeBox"]==n["globalBox"]
    aa,bb=(na,b) if d=="left" else (na.transpose(1,0,2),b.transpose(1,0,2))
    diff=aa[:,1024:].astype(float)-bb[:,:230].astype(float)
    path,stats=M["minimum_path"](np.mean(diff*diff,axis=2))
    outputs=[]
    for mode,cuts in (("hardminerror",path),("straight_core",np.full(1254,115,dtype=int))):
        combined=np.empty((1254,2278,3),dtype=np.uint8)
        for y,cut in enumerate(cuts):
            x=1024+int(cut)
            combined[y,:x]=aa[y,:x];combined[y,x:]=bb[y,int(cut):]
        crop=combined[:,850:1420]
        if d=="top":crop=crop.transpose(1,0,2)
        f=out/(d+"_"+mode+"_100pct.png")
        with f.open("xb") as h:Image.fromarray(crop).save(h,format="PNG")
        outputs.append({"mode":mode,"path":str(f),"sha256":sha(f),"dimensions":list(Image.open(f).size),"nativeScale":1,"sourceCoreCut":1139,"targetCoreCut":115})
    results.append({"direction":d,"neighbor":ns,"pathByScanline":path.tolist(),"statistics":stats,"outputs":outputs})
record={"status":"pending_visual_review","target":s,"input":{"path":str(inp),"sha256":sha(inp)},"checks":results,"allPixelsOriginalSameCoordinates":True,"registration":False,"resizing":False,"feathering":False,"colorCorrection":False,"guidePixelsUsed":False,"formalAcceptedCount":0}
with (out/"seams.json").open("x",encoding="utf-8") as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps({"qa":str(out),"seams":[{"direction":x["direction"],"statistics":x["statistics"]} for x in results],"formalAcceptedCount":0}))

