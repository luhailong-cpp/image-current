from pathlib import Path
import argparse,hashlib,json,shutil,sys,importlib.util
from datetime import datetime,timezone
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parents[1]
D=Path(__file__).resolve().parent
SW=T.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf8")
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def meta(p):
 im=Image.open(p);return {"file":str(p),"sha256":sha(p),"pixels":list(im.size),"mode":im.mode}
a=argparse.ArgumentParser();a.add_argument("mode",choices=["prepare","ingest"]);a.add_argument("--spec");a.add_argument("--id");a.add_argument("--source");a.add_argument("--receipt");v=a.parse_args()
if v.mode=="prepare":
 s=read(v.spec);d=D/s["id"];d.mkdir(parents=True,exist_ok=True);p=Path(s["input"]);im=Image.open(p).convert("RGB");assert im.size==(4096,4096)
 box=s["box"];assert box[2]-box[0]==box[3]-box[1]==1254
 target=d/"input.png";im.crop(box).save(target,optimize=True)
 c=read(SW.parent/"production-contract.json")
 refs=[target]+[Path(c[k]) for k in ["layoutReference","detailStyleReference","primaryStyleReference"]]
 prompt=s["instruction"]+"\n\nUse case: precise-object-edit. EDIT IMAGE 1 ONLY. Output exactly one opaque 1254x1254 PNG at the same native pixels and crop. Image 1 is an exact unscaled crop from the assembled native 4096 map tile r11_c06. Preserve its camera, scale, all object locations and clipping. Make only the localized repair described above. Especially preserve all outer 115-pixel border strips, every intersecting line at those borders, colors and texture there unchanged. No full scene or zoom out. Image 2 is approved whole-city layout only, never output the city. Image 3 is approved daylight polished quiet grey stone material. Image 4 is current primary Daoist chibi style; never copy UI or characters. Do not introduce props, people, trees, extra architecture, new paving seams or text. No red pavement, dense marble veins, heavy cellular texture or blur. Preserve all unmentioned parts exactly."
 pp=d/"prompt.txt";pp.write_text(prompt,encoding="utf8")
 roles=["exact native crop edit target","approved layout only","approved stone/daylight","approved primary chibi style"]
 q={"id":s["id"],"prompt":prompt,"promptFile":str(pp),"promptSha256":sha(pp),"referenced_image_paths":[str(p) for p in refs],"references":[dict(meta(p),role=r) for p,r in zip(refs,roles)],"inputCandidate":meta(p),"candidateBox":box,"contextWorldBox":[box[0]+20480,box[1]+40960,box[2]+20480,box[3]+40960],"nativeCoreBox":[115,115,1139,1139],"transparent_background":False,"actualModel":None,"actualQuality":None,"route":"builtin_image_gen","requestedNativePixels":[1254,1254],"preparedAtUtc":datetime.now(timezone.utc).isoformat(),"issueIds":s["issueIds"]}
 # p overwritten in comprehension does not leak in Python; explicit source
 q["inputCandidate"]=meta(Path(s["input"]))
 write(d/"request.json",q);print(d/"request.json")
elif v.mode=="ingest":
 d=D/v.id;q=read(d/"request.json");src=Path(v.source);assert all(sha(r["file"])==r["sha256"] for r in q["references"]);assert sha(q["inputCandidate"]["file"])==q["inputCandidate"]["sha256"]
 im=Image.open(src);assert im.size==(1254,1254) and im.mode in ("RGB","RGBA")
 if im.mode=="RGBA":assert im.getextrema()[3]==(255,255)
 out=d/"native.png";assert not out.exists();shutil.copyfile(src,out)
 receipt=read(v.receipt);write(d/"receipt.json",receipt)
 r=dict(q,output=meta(out),sourceOutput=meta(src),receiptFile=str(d/"receipt.json"),receiptSha256=sha(d/"receipt.json"),resizedAfterGeneration=False,ingestedAtUtc=datetime.now(timezone.utc).isoformat())
 write(d/"generation.json",r)
 spec=importlib.util.spec_from_file_location("local_repairs",SW/"local_repairs.py");lr=importlib.util.module_from_spec(spec);spec.loader.exec_module(lr)
 current=np.array(Image.open(q["inputCandidate"]["file"]).convert("RGB"));box=q["candidateBox"];l,t,rr,bb=box
 before=current[t:bb,l:rr].copy();new=np.array(im.convert("RGB"));patched,ev=lr.quilt(before,new,2);current[t:bb,l:rr]=patched
 dest=d/"r11_c06.repaired.candidate.png";Image.fromarray(current).save(dest,optimize=True)
 old=np.array(Image.open(q["inputCandidate"]["file"]).convert("RGB"))
 outside=np.ones((4096,4096),bool);outside[t:bb,l:rr]=False
 assert np.array_equal(current[outside],old[outside])
 for axis in [current[0],current[-1],current[:,0],current[:,-1]]:pass
 edges=np.concatenate([current[0],current[-1],current[:,0],current[:,-1]])
 oldedges=np.concatenate([old[0],old[-1],old[:,0],old[:,-1]])
 assert np.array_equal(edges,oldedges)
 Image.fromarray(patched).save(d/"applied-crop.png",optimize=True)
 write(d/"assembly.json",{"input":q["inputCandidate"],"output":meta(dest),"source":meta(out),"candidateBox":box,"contextWorldBox":q["contextWorldBox"],"quilt":ev,"outsideCropUnchanged":True,"allFourTileOuterEdgesUnchanged":True,"visualQa":"pending","formalAccepted":False})
 print(json.dumps(meta(dest)))

