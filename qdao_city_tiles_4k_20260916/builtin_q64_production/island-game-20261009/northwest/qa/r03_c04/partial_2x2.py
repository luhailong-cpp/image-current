"""Mechanical QA of existing upper-left 2x2 only; never invent missing tiles."""
from pathlib import Path
import hashlib,json,runpy
from datetime import datetime,timezone
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent/"partial_2x2_v1"
STEMS=["r03_c04_s01_01_a03","r03_c04_s01_02_a01","r03_c04_s02_01_a02","r03_c04_s02_02_a02"]
M=runpy.run_path(str(Z/"assemble_tile.py"),run_name="partial_qa")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=[];sources=[]
for i,s in enumerate(STEMS):
    f=Z/"native"/(s+".png");r,c=divmod(i,2)
    source,array=M["load_raw_source"](f,Path(str(f)+".generation.json"),"r03_c04",r,c)
    raw.append(array);sources.append(source)
def join(a,b,ai,bi):
    delta=a[:,1024:].astype(float)-b[:,:230].astype(float)
    path,stats=M["minimum_path"](np.mean(delta*delta,axis=2))
    joined=np.empty((a.shape[0],2278,3),dtype=np.uint8)
    ids=np.empty((a.shape[0],2278),dtype=np.uint8)
    for y,k in enumerate(path):
        cut=1024+int(k)
        joined[y,:cut]=a[y,:cut];joined[y,cut:]=b[y,int(k):]
        ids[y,:cut]=ai[y,:cut];ids[y,cut:]=bi[y,int(k):]
    return joined,ids,{"pathByScanline":path.tolist(),"statistics":stats}
rows=[];owners=[];seams=[]
for r in range(2):
    row,ids,seam=join(raw[r*2],raw[r*2+1],np.full((1254,1254),r*2,dtype=np.uint8),np.full((1254,1254),r*2+1,dtype=np.uint8))
    rows.append(row);owners.append(ids);seams.append({"direction":"horizontal row assembly","row":r+1,**seam})
full,ids,seam=join(rows[0].transpose(1,0,2),rows[1].transpose(1,0,2),owners[0].T,owners[1].T)
full=full.transpose(1,0,2);ids=ids.T
seams.append({"direction":"vertical row assembly","transposed":True,**seam})
assert full.shape==(2278,2278,3)
counts=[]
for i,a in enumerate(raw):
    y,x=divmod(i,2);ys,xs=np.nonzero(ids==i)
    assert np.array_equal(full[ys,xs],a[ys-y*1024,xs-x*1024])
    counts.append(int(xs.size))
assert sum(counts)==2278**2
OUT.mkdir(exist_ok=False)
files=[]
def save(name,array,box,preview=False):
    p=OUT/name
    im=Image.fromarray(array)
    with p.open("xb") as f:im.save(f,format="PNG")
    files.append({"path":str(p),"sha256":sha(p),"size":list(im.size),"boxInPadded":box,"previewOnly":preview})
save("native_2278x2278.png",full,[0,0,2278,2278])
save("source_ids.png",ids,[0,0,2278,2278])
save("core_2048x2048_PARTIAL.png",full[115:2163,115:2163],[115,115,2163,2163])
save("four_way_100pct.png",full[884:1394,884:1394],[884,884,1394,1394])
for a,b in [(0,1139),(1139,2278)]:
    save(f"horizontal_seam_{a}_{b}_100pct.png",full[880:1400,a:b],[a,880,b,1400])
preview=Image.fromarray(full).resize((1139,1139),Image.Resampling.LANCZOS)
save("PREVIEW_half_scale.png",np.asarray(preview),[0,0,2278,2278],True)
record={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"status":"partial_existing_2x2_diagnostic_only","sourceStems":STEMS,"sources":sources,"seams":seams,"sourceCounts":counts,"fullNativeCoverageOfDeclaredRectangle":True,"declaredRectangleDimensions":[2278,2278],"formalTile4096Complete":False,"missingCells":12,"allPixelsOriginalSameGlobalCoordinates":True,"files":files,"globalBox":[12173,8077,14451,10355],"guidePixelsUsed":False,"registration":False,"resizingArt":False,"feathering":False,"colorCorrection":False,"formalAcceptedCount":0}
with (OUT/"record.json").open("x",encoding="utf-8") as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps({"out":str(OUT),"counts":counts,"fullNativeCoverageOfDeclaredRectangle":True,"formalTile4096Complete":False}))

