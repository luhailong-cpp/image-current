from pathlib import Path
import json, hashlib, sys
from datetime import datetime, timezone
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def write(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def filemeta(p): return {"file":str(p),"sha256":sha(p)}
def resolve(p): return Path(p) if Path(p).is_absolute() else B/p
def checked(v):
 p=resolve(v["file"] if isinstance(v,dict) else v)
 if isinstance(v,dict) and v.get("sha256"): assert sha(p)==v["sha256"],p
 return p
def source_id(s): return s.get("jointSourceId",s.get("sourceId"))
def normalize_sources(assembly,box):
 out={}
 for s in assembly["sources"]:
  t=dict(s); g=t.get("globalNativeBox")
  if g is None:
   r=read(checked(t["generationRecord"]))
   g=r.get("globalNativeBox")
  if g is None:
   n=t["nativeBox"];g=[n[0]+box[0],n[1]+box[1],n[2]+box[0],n[3]+box[1]]
  t["globalNativeBox"]=g
  out[source_id(s)]=t
 return out
def load_input(spec,tile):
 ap=resolve(spec["assembly"]); assembly=read(ap)
 box=spec.get("globalBox")
 if assembly.get("candidate") and (not spec.get("artifact") or str(assembly["candidate"].get("file","")).endswith(spec["artifact"])):
  art=dict(assembly["candidate"]); art["sourceIdMap"]=assembly["sourceIdMap"]
  box=box or art.get("globalBox") or assembly.get("globalCoreBox")
 else:
  matches=[a for a in assembly["artifacts"] if "sourceIdMap" in a and (spec.get("artifact",tile+".") in Path(a["file"]).name)]
  assert len(matches)==1,(spec,matches)
  art=matches[0];box=box or art.get("globalBox")
 assert box is not None,spec
 img=np.asarray(Image.open(checked(art)).convert("RGB")).copy()
 ids=np.asarray(Image.open(checked(art["sourceIdMap"]))).copy()
 assert img.shape[:2]==ids.shape and img.shape[:2]==(box[3]-box[1],box[2]-box[0])
 return img,ids,normalize_sources(assembly,box),box,{"assembly":filemeta(ap),"candidate":filemeta(checked(art)),"sourceIdMap":filemeta(checked(art["sourceIdMap"]))}
def main():
 recipe_path=Path(sys.argv[1]); recipe=read(recipe_path); out=resolve(recipe["output"]);out.mkdir(parents=True,exist_ok=True)
 all_sources=[];known={}
 def remap(ids,sources):
  mapped=np.zeros(ids.shape,np.uint16)
  for old in np.unique(ids):
   assert int(old)!=0
   s=sources[int(old)];key=(s["sha256"],tuple(s["globalNativeBox"]))
   if key not in known:
    s=dict(s);s.pop("jointSourceId",None);s.pop("tileSourceId",None);s.pop("nativeBox",None)
    s["sourceId"]=len(all_sources)+1;known[key]=s["sourceId"];all_sources.append(s)
   mapped[ids==old]=known[key]
  return mapped
 tile_data={};records=[]
 for tile,spec in recipe["tiles"].items():
  arr,old,sources,box,input_meta=load_input(spec["base"],tile)
  ids=remap(old,sources); inputs=[input_meta];layers=[]
  for overlay in spec.get("overlays",[]):
   inc,oi,os,ob,meta=load_input(overlay,tile)
   assert ob==box
   if overlay.get("mask"):
    mask=np.asarray(Image.open(resolve(overlay["mask"])))>0
    if mask.shape!=ids.shape:
     x,y=overlay["maskTileOffset"];full=np.zeros(ids.shape,bool);full[y:y+mask.shape[0],x:x+mask.shape[1]]=mask;mask=full
   elif overlay.get("against"):
    other=np.asarray(Image.open(resolve(overlay["against"])).convert("RGB"))
    mask=np.any(inc!=other,axis=2)
   else: raise ValueError("overlay needs mask or against")
   if overlay.get("expectedUnchangedBase"):
    expected=np.asarray(Image.open(resolve(overlay["expectedUnchangedBase"])).convert("RGB"))
    assert not np.any(arr[mask]!=expected[mask]), "Overlapping changes; require explicit rebase QA"
   mapped=remap(oi,os);arr[mask]=inc[mask];ids[mask]=mapped[mask]
   inputs.append(meta);layers.append({"input":meta,"selectedPixels":int(mask.sum()),"method":"hard native-pixel ownership"})
  for overlay in spec.get("nativeOverlays",[]):
   dp=resolve(overlay["delivery"]);delivery=read(dp);s=dict(delivery["native"]);s["sourceId"]=1
   nb=s["globalNativeBox"];native=np.asarray(Image.open(checked(s)).convert("RGB"));mask=np.asarray(Image.open(checked(delivery["mask"])))>0
   inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
   if inter[2]<=inter[0] or inter[3]<=inter[1]:continue
   ns=(slice(inter[1]-nb[1],inter[3]-nb[1]),slice(inter[0]-nb[0],inter[2]-nb[0]))
   ts=(slice(inter[1]-box[1],inter[3]-box[1]),slice(inter[0]-box[0],inter[2]-box[0]))
   region=mask[ns];mapped=remap(np.ones(region.shape,np.uint16),{1:s})
   arr[ts][region]=native[ns][region];ids[ts][region]=mapped[region]
   layers.append({"delivery":filemeta(dp),"selectedPixels":int(region.sum()),"method":"hard native-pixel mask in global coordinates"})
  p=out/(tile+".png");ip=out/(tile+".source-id.png")
  Image.fromarray(arr).save(p);Image.fromarray(ids).save(ip)
  used=[s for s in all_sources if s["sourceId"] in np.unique(ids)]
  replay=np.zeros_like(arr);counts={}
  for s in used:
   native=np.asarray(Image.open(checked(s)).convert("RGB"));sx,sy,ex,ey=s["globalNativeBox"]
   assert native.shape[:2]==(ey-sy,ex-sx)
   yy,xx=np.where(ids==s["sourceId"]);ny=yy+box[1]-sy;nx=xx+box[0]-sx
   assert np.min(nx)>=0 and np.min(ny)>=0 and np.max(nx)<native.shape[1] and np.max(ny)<native.shape[0]
   replay[yy,xx]=native[ny,nx];counts[s["sourceId"]]=len(xx)
  differences=int(np.any(replay!=arr,axis=2).sum());assert differences==0
  rec={"schemaVersion":1,"tile":tile,"createdAt":datetime.now(timezone.utc).isoformat(),"candidate":filemeta(p),"sourceIdMap":filemeta(ip),"globalCoreBox":box,"outputSize":[arr.shape[1],arr.shape[0]],"sources":used,"inputs":inputs,"overlays":layers,"proof":{"pixels":int(ids.size),"mismatches":differences,"sourcePixelCounts":counts},"resampled":False,"feathered":False,"painted":False,"formalAccepted":False,"status":"native-composed-pending-visual-review"}
  ap=out/(tile+".assembly.json");write(ap,rec);records.append({"tile":tile,**filemeta(p),"assembly":filemeta(ap),"globalBox":box});tile_data[tile]=(arr,box)
 # Native canvas and scaled review-only overview.
 bounds=[min(v[1][0] for v in tile_data.values()),min(v[1][1] for v in tile_data.values()),max(v[1][2] for v in tile_data.values()),max(v[1][3] for v in tile_data.values())]
 canvas=Image.new("RGB",(bounds[2]-bounds[0],bounds[3]-bounds[1]))
 for a,g in tile_data.values():canvas.paste(Image.fromarray(a),(g[0]-bounds[0],g[1]-bounds[1]))
 canvas.save(out/"neighborhood.native.png")
 preview=canvas.copy();preview.thumbnail((1600,1600));preview.save(out/"neighborhood.preview-only.jpg",quality=93)
 qa=out/"qa";qa.mkdir(exist_ok=True);crops=[]
 for axis,coord,start,end,name in recipe.get("boundaries",[]):
  for i,v in enumerate(range(start,end,512),1):
   g=[coord-320,v,coord+320,min(v+512,end)] if axis=="v" else [v,coord-320,min(v+512,end),coord+320]
   p=qa/(name+f"-segment-{i:02d}.100pct.png");canvas.crop(tuple([g[0]-bounds[0],g[1]-bounds[1],g[2]-bounds[0],g[3]-bounds[1]])).save(p)
   crops.append({**filemeta(p),"globalBox":g,"scale":1})
 for name,g in recipe.get("extraCrops",[]):
  p=qa/(name+".100pct.png");canvas.crop(tuple([g[0]-bounds[0],g[1]-bounds[1],g[2]-bounds[0],g[3]-bounds[1]])).save(p);crops.append({**filemeta(p),"globalBox":g,"scale":1})
 report={"createdAt":datetime.now(timezone.utc).isoformat(),"recipe":filemeta(recipe_path),"artifacts":records,"qaCrops":crops,"sourceCount":len(all_sources),"pixelCount":sum(a.size//3 for a,g in tile_data.values()),"mismatches":0,"formalAccepted":False}
 write(out/"composition-report.json",report);print(json.dumps({k:report[k] for k in ["sourceCount","pixelCount","mismatches"]}))
if __name__=="__main__":main()

