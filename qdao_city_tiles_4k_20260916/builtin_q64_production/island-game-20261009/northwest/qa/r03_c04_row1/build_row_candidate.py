"""One explicit native candidate row in QA only; no selection/progress writes."""
from pathlib import Path
import json, hashlib, runpy
from datetime import datetime,timezone
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/"candidate_row_v1"
STEMS=["r03_c04_s01_01_a03","r03_c04_s01_02_a01","r03_c04_s01_03_a02","r03_c04_s01_04_a01"]
M=runpy.run_path(str(Z/"assemble_tile.py"),run_name="candidate_row_qa")
sources=[];arrays=[];paths=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for col,stem in enumerate(STEMS):
    p=Z/"native"/f"{stem}.png"; inp=Z/"guides"/f"{stem}.input.json"
    s,a=M["load_raw_source"](p,Path(str(p)+".generation.json"),"r03_c04",0,col)
    assert s["globalNativeBox"]==json.loads(inp.read_text(encoding="utf-8-sig"))["globalBox"]
    s["input"]={"path":str(inp),"sha256":sha(inp)}
    sources.append(s);arrays.append(a)
row=arrays[0].copy()
owners=np.zeros((1254,1254),dtype=np.uint8)
for col in range(1,4):
    offset=1024*col
    diff=row[:,offset:].astype(np.float64)-arrays[col][:,:230].astype(np.float64)
    path,stats=M["minimum_path"](np.mean(diff*diff,axis=2))
    nxt=np.empty((1254,offset+1254,3),dtype=np.uint8)
    ids=np.empty((1254,offset+1254),dtype=np.uint8)
    for y,cut in enumerate(path):
        split=offset+int(cut)
        nxt[y,:split]=row[y,:split];nxt[y,split:]=arrays[col][y,int(cut):]
        ids[y,:split]=owners[y,:split];ids[y,split:]=col
    row,owners=nxt,ids
    paths.append({"left":STEMS[col-1],"right":STEMS[col],"overlapX":offset,"pathXByY":path.tolist(),"statistics":stats})
assert row.shape==(1254,4326,3)
counts=[]
for col,a in enumerate(arrays):
    region=owners[:,1024*col:1024*col+1254]==col
    assert np.array_equal(row[:,1024*col:1024*col+1254][region],a[region])
    counts.append(int(region.sum()))
assert sum(counts)==4326*1254
OUT.mkdir(exist_ok=False)
full=OUT/"row_native_4326x1254.png"
with full.open("xb") as f:Image.fromarray(row).save(f,format="PNG")
owner=OUT/"source_ids.png"
with owner.open("xb") as f:Image.fromarray(owners).save(f,format="PNG")
preview=OUT/"PREVIEW_row_half_scale.png"
with preview.open("xb") as f:Image.fromarray(row).resize((2163,627),Image.Resampling.LANCZOS).save(f,format="PNG")
record={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"status":"usable_candidate_row_only_pending_bottom_and_external_adjacencies","operation":"original-pixel same-global-coordinate hard minimum-error seams","sourceStems":STEMS,"sources":sources,"paths":paths,"dimensions":[4326,1254],"globalBox":[12173,8077,16499,9331],"allNativeSourcePixelsSameCoordinates":True,"fullNativeCoverage":True,"sourcePixelCounts":counts,"sourceIdMask":{"path":str(owner),"sha256":sha(owner),"ids":"0..3 correspond to explicit sourceStems"},"output":{"path":str(full),"sha256":sha(full)},"preview":{"path":str(preview),"sha256":sha(preview),"previewOnly":True,"scale":0.5,"neverFinalArt":True},"mechanicalArtResizing":False,"registration":False,"feathering":False,"colorCorrection":False,"guidePixelsUsed":False,"formalAcceptedCount":0,"selectionModified":False,"progressModified":False,"pending":["Bottom row adjacency and any four-way seam intersections.","First source upper-halo gold cap y0..55 lies wholly outside tile core and needs recheck only if used for future upper tile context."]}
with (OUT/"row_record.json").open("x",encoding="utf-8") as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps({"output":record["output"],"dimensions":record["dimensions"],"nativePixelCounts":counts,"record":str(OUT/"row_record.json"),"formalAcceptedCount":0}))

