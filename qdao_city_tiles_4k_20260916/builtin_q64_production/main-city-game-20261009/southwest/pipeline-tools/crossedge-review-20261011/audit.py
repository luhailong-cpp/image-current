from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
ROOT=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
OUT=ROOT/"pipeline-tools/crossedge-review-20261011"
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT))
import assemble as assembly
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def res(p):
 p=Path(p);return p if p.is_absolute() else ROOT/p
def save(a,name):
 p=OUT/name;Image.fromarray(a).save(p);return {"file":str(p),"sha256":sha(p),"pixels":[int(a.shape[1]),int(a.shape[0])],"resized":False}
paths={
"r10_c05":ROOT/"r10_c05/repairs/output/r10_c05.repaired.candidate.png",
"r11_c05":ROOT/"r11_c05/refinement-resume20261010/integrated-v2/r11_c05.repaired-v2.candidate.png",
"r10_c06":ROOT/"r10_c06/pipeline/output/5c4d9d81c6fcc1ca/r10_c06.candidate.png",
"r11_c06":ROOT/"r11_c06/pipeline/output/94ddb3ea62a89ee2/r11_c06.candidate.png"}
origins={"r10_c05":[16384,36864],"r10_c06":[20480,36864],"r11_c05":[16384,40960],"r11_c06":[20480,40960]}
cores={k:np.array(Image.open(p).convert("RGB")) for k,p in paths.items()}
ctx={};sources={}
for k,p in paths.items():
 assert cores[k].shape==(4096,4096,3)
 sources[k]={"candidate":{"file":str(p),"sha256":sha(p),"pixels":[4096,4096]},"coreWorldBox":origins[k]+[origins[k][0]+4096,origins[k][1]+4096],"contextWorldBox":[origins[k][0]-115,origins[k][1]-115,origins[k][0]+4211,origins[k][1]+4211]}
 if k=="r10_c05":
  m=read(ROOT/k/"output/assembly.json"); arrays={}
  for item in m["nativeSources"]:
   f=res(item["nativeFile"]);assert sha(f)==item["nativeSha256"]
   arrays[(item["row"],item["column"])]=np.array(Image.open(f).convert("RGB"))
  c,_=assembly.assemble_pixels(arrays,tuple(m["selectedRectangleInclusive"]),m["composition"]["maximumFeatherRadiusPixels"])
  c[115:4211,115:4211]=cores[k]
  sources[k]["context"]={"source":"Replayed selected 16 native images using recorded assembly; existing final repaired core substituted pixel exactly, halos unmodified. QA only.","baseAssembly":str(ROOT/k/"output/assembly.json"),"baseAssemblySha256":sha(ROOT/k/"output/assembly.json"),"pixelHash":hashlib.sha256(c.tobytes()).hexdigest(),"pixels":[4326,4326]}
 else:
  cp=p.with_name(p.stem+".context.png")
  c=np.array(Image.open(cp).convert("RGB"));assert np.array_equal(c[115:4211,115:4211],cores[k])
  sources[k]["context"]={"file":str(cp),"sha256":sha(cp),"pixels":[4326,4326],"coreExact":True}
 ctx[k]=c
montage=np.concatenate([np.concatenate([cores["r10_c05"],cores["r10_c06"]],1),np.concatenate([cores["r11_c05"],cores["r11_c06"]],1)],0)
preview=OUT/"2x2.preview-2048.png"
Image.fromarray(montage).resize((2048,2048),Image.Resampling.LANCZOS).save(preview)
report={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"sources":sources,"preview":{"file":str(preview),"sha256":sha(preview),"pixels":[2048,2048],"sourcePixels":[8192,8192],"resized":True,"purpose":"QA preview only; never final art"},"crossEdges":[],"center":save(montage[3584:4608,3584:4608],"center.actual-1024.png"),"formalAccepted":False}
report["center"]["worldBox"]=[19968,40448,20992,41472]
for ident,a,b,axis in [("north_vertical","r10_c05","r10_c06",1),("south_vertical","r11_c05","r11_c06",1),("west_horizontal","r10_c05","r11_c05",0),("east_horizontal","r10_c06","r11_c06",0)]:
 A,B=cores[a],cores[b]
 if axis==1:
  strip=np.concatenate([A[:,-384:],B[:,:384]],1)
  la,lb=ctx[a][115:4211,4096:4326],ctx[b][115:4211,:230]
  boundary=np.abs(A[:,-1].astype(float)-B[:,0].astype(float))
  box=[origins[b][0]-384,origins[b][1],origins[b][0]+384,origins[b][1]+4096]
  overlap=[origins[b][0]-115,origins[b][1],origins[b][0]+115,origins[b][1]+4096]
  lc=[4096,115,4326,4211];rc=[0,115,230,4211]
 else:
  strip=np.concatenate([A[-384:],B[:384]],0)
  la,lb=ctx[a][4096:4326,115:4211],ctx[b][:230,115:4211]
  boundary=np.abs(A[-1].astype(float)-B[0].astype(float))
  box=[origins[b][0],origins[b][1]-384,origins[b][0]+4096,origins[b][1]+384]
  overlap=[origins[b][0],origins[b][1]-115,origins[b][0]+4096,origins[b][1]+115]
  lc=[115,4096,4211,4326];rc=[115,0,4211,230]
 delta=np.abs(la.astype(float)-lb.astype(float))
 edge={"id":ident,"first":a,"second":b,"axis":axis,"actualCandidateCrop":save(strip,ident+".actual.png"),"worldBox":box,"boundaryAtCropPixel":384,"segments":[],"contextOverlap":{"worldBox":overlap,"firstContextBox":lc,"secondContextBox":rc,"first":save(la,ident+".first-context-overlap.png"),"second":save(lb,ident+".second-context-overlap.png"),"sameWorldPixelMeanAbsDifference":float(delta.mean()),"differentPixelCount":int(np.any(la!=lb,axis=2).sum()),"comparisonPixelCount":int(la.shape[0]*la.shape[1])},"candidateAdjacentPixelMeanAbsDifference":float(boundary.mean()),"visualPassed":None}
 for i in range(4):
  seg=strip[i*1024:(i+1)*1024] if axis==1 else strip[:,i*1024:(i+1)*1024]
  r=save(seg,f"{ident}.actual.segment{i+1}.png");r["sourceLongAxisRange"]=[i*1024,(i+1)*1024];edge["segments"].append(r)
 report["crossEdges"].append(edge)
assigned=read(ROOT.parent.parent/"acceleration-20261010/assignments.json")
excluded=[c for a in assigned["assignments"] if a.get("map")=="main-city-game-20261009" for c in a["coordinates"] if 9<=int(c[1:3])<=16 and 1<=int(c[5:7])<=8]
report["acceleratedSouthwestExclusions"]=excluded
report["notes"]=["Core coordinates are half-open artwork pixels. Context indices include 115px outer halo.","Exact mechanical equality or low differences alone do not constitute visual approval.","Current sources snapshotted by SHA; later repair candidates need renewed edge verification."]
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"manifest":str(OUT/"manifest.json"),"preview":str(preview),"edges":[{k:e[k] for k in ["id","candidateAdjacentPixelMeanAbsDifference"]} for e in report["crossEdges"]],"exclusions":excluded}))

