from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,uuid,os
from PIL import Image
T=Path(__file__).resolve().parent;R=T/"repairs-resume-20261012";R.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 p=Path(p);assert not p.exists(),p;p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8")
auth=Path("D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json")
a=read(auth);assert a["newArtworkGenerationAllowed"] and a["builtinOnly"] and not a["paidApiAllowed"]
idx=read(T/"candidate/latest-assembly.json");f=Path(idx["candidate"]["path"]);assert sha(f)==idx["candidate"]["sha256"]
north=T.parent/"r14_c13/candidate/r14_c13-4k-north-v6.png"
assert sha(north)=="f1d683133fa23f466621f492375b55848d2a8c5775e039f10c2c86bc3860fda5"
cur=Image.open(f).convert("RGB");old=Image.open(north).convert("RGB")
c=read(T.parent.parent/"production-contract.json")
refs=[{"path":c[k],"sha256":sha(c[k]),"size":list(Image.open(c[k]).size),"role":k} for k in ["layoutReference","detailStyleReference","primaryStyleReference"]]
items=[]
for name,x in [("north-wood-left-v1",0),("north-roof-mid-v1",1000),("north-roof-right-v1",2000)]:
 target=Image.new("RGB",(1254,1254));target.paste(old.crop((x,3696,x+1254,4096)),(0,0));target.paste(cur.crop((x,0,x+1254,854)),(0,400))
 tp=R/(name+"-target.png");assert not tp.exists();target.save(tp)
 prompt=f"""Edit only input 4, the LAST IMAGE, an exact native 1254x1254 crop across two already painted adjacent tiles. Inputs 1..3 are style references only. Preserve precise framing, close-up scale and every existing object geometry.
The top400 rows y0..399 are immutable northern reference artwork. The seam is at y400. Repair ONLY the new southern side around y400..640, keeping upper400 rows and lower rows y760..1253 unchanged. This is a MATERIAL CONTINUITY repair: remove the flat horizontal shift of wood/gold-cream tile shading, brightness and fine texture at y400 by continuing the exact upper material naturally into the lower region. The wood beams, cream plaster, roof tile ribs, tile overlaps and dark grooves already have correct geometry. Preserve their exact outlines and endpoints; do not redraw, move, widen, duplicate or add roof tiles. No blur strip, no horizontal border, no noise layer and no gradient wash that destroys material detail. Repaint continuous native material with gentle daylight hand-painted finish. Retain a quiet transition back to the original lower painted texture by y720. Only partial roof/facade remains in frame; never a whole building. No new signs, ornaments, foliage, characters or text. Opaque native1254x1254 PNG; no scaling.
This crop corresponds to r15_c13 x{x}..{x+1254}, new-side y0..854. Immutable r14_c13 v6 is present directly above. The straight horizontal edge of this source join is not an object boundary."""
 pp=R/(name+".prompt.txt");assert not pp.exists();pp.write_text(prompt,encoding="utf-8")
 req={"prompt":prompt,"referenced_image_paths":[r["path"] for r in refs]+[str(tp)],"transparent_background":False}
 rq=R/(name+".request.json");write(rq,req)
 meta={"id":name,"tile":"r15_c13","preparedAt":datetime.now(timezone.utc).isoformat(),"authorization":{"path":str(auth),"sha256":sha(auth)},"source":idx["candidate"],"northSource":{"path":str(north),"sha256":sha(north)},"northCrop":[x,3696,x+1254,4096],"southCrop":[x,0,x+1254,854],"target":{"path":str(tp),"sha256":sha(tp),"size":[1254,1254]},"request":{"path":str(rq),"sha256":sha(rq)},"prompt":{"path":str(pp),"sha256":sha(pp)},"references":refs,"resampled":False,"status":"prepared_only_no_generation","actualModel":None,"actualQuality":None}
 write(R/(name+".preparation.json"),meta);items.append(meta)
name="stone-relief-v1";box=[1400,2630,2654,3884];tp=R/(name+"-target.png");assert not tp.exists();cur.crop(box).save(tp)
prompt="""Edit only LAST IMAGE input4, a native1254x1254 close-up of existing stone balustrade. Inputs1..3 style references only. Minimal local restoration: at local x approximately555,y545 (r15_c13 x1955,y3175), the shallow double-line upper recessed ornamental border of the large stone panel fades out in mid-panel. Complete its natural thin relief line continuously across the same panel, or end it cleanly at an existing structural post/corner. Preserve handrail cap, vertical post, bevel, wood/red pillar above and paving below exactly. Keep the original subdued pale-grey hand-painted stone texture and gentle daylight. Only the small relief fragment region local x400..740,y470..640 may change. Everything else unchanged. No new motifs, objects, borders, text or geometry rearrangement. Output opaque native1254x1254 PNG with same crop; do not upscale."""
pp=R/(name+".prompt.txt");pp.write_text(prompt,encoding="utf-8");rq=R/(name+".request.json");write(rq,{"prompt":prompt,"referenced_image_paths":[r["path"] for r in refs]+[str(tp)],"transparent_background":False})
meta={"id":name,"tile":"r15_c13","source":idx["candidate"],"sourceCrop":box,"target":{"path":str(tp),"sha256":sha(tp),"size":[1254,1254]},"request":{"path":str(rq),"sha256":sha(rq)},"prompt":{"path":str(pp),"sha256":sha(pp)},"references":refs,"resampled":False,"status":"prepared_only_no_generation","actualModel":None,"actualQuality":None,"authorization":{"path":str(auth),"sha256":sha(auth)}}
write(R/(name+".preparation.json"),meta);items.append(meta)
record={"tile":"r15_c13","resumedAt":datetime.now(timezone.utc).isoformat(),"authorization":{"path":str(auth),"sha256":sha(auth)},"status":"offline_targets_ready_pending_one_normal_builtin_call","baseline":idx,"actualNativeCountBefore":len(list((T/"native").glob("*.png"))),"firstNewOutput":None,"preparedRequests":[{"id":v["id"],"request":v["request"],"target":v["target"]} for v in items],"historicalFreezeModified":False,"structuralInternalQAReaudited":False,"newCalls":0,"remainingQA":read(T/"progress.json")["remainingQA"]}
write(T/"production-resume-20261012.json",record)
print(json.dumps({"resumeRecord":str(T/"production-resume-20261012.json"),"requests":record["preparedRequests"]},indent=2))

