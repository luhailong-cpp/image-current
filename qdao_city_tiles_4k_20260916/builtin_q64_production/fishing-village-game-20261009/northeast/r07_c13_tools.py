"""r07_c13 native generation helpers; never writes shared or other-tile state."""
import argparse,datetime,hashlib,json,re,shutil
from pathlib import Path
from PIL import Image
Z=Path(__file__).resolve().parent;T="r07_c13";N=1254;H=115;CORE=1024
ORIGIN=[49152,24576]
CONTRACT=Z.parent/"production-contract.json";CONFIG=Path("D:/work/image/config/image-generation.json")
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
C=read(CONTRACT)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role=None):
 r={"path":str(Path(p).resolve()).replace("\\","/"),"sha256":sha(p)}
 if role:r["role"]=role
 return r
def write(p,d,immutable=False):
 p=Path(p);data=json.dumps(d,ensure_ascii=False,indent=2)+"\n"
 if immutable and p.exists():
  assert read(p)==d,("Refuse overwrite",str(p))
  return
 p.write_text(data,encoding="utf-8")
def co(p):
 assert re.fullmatch(T+r"_p[1-4][1-4]",p)
 r,c=int(p[-2]),int(p[-1]);x=ORIGIN[0]+(c-1)*CORE;y=ORIGIN[1]+(r-1)*CORE
 b=[x-H,y-H,x+CORE+H,y+CORE+H]
 return {"id":p,"coreGlobalBox":[x,y,x+CORE,y+CORE],"nativeGlobalBox":b,"overviewBox":[v*1254/57344 for v in b],"expectedSize":[N,N],"nativeCoreBox":[H,H,1139,1139]}
def mandatory():
 return [ref(C[k],r) for k,r in [("layoutReference","wholemap layout only"),("detailStyleReference","daylight materials only"),("primaryStyleReference","Q Daoist user style only")]]
def init():
 doc={"tile":T,"tileOrigin":ORIGIN,"tileCoreBox":[49152,24576,53248,28672],"references":mandatory(),"patches":[co(f"{T}_p{r}{c}") for r in range(1,5) for c in range(1,5)]}
 write(Z/"records"/f"{T}.coordinates.json",doc,True)
 layout=Image.open(C["layoutReference"]).convert("RGB")
 context=Z/"guides"/f"{T}.context-layout-only.png";box=[1010,475,1205,675]
 if not context.exists():
  layout.crop(box).resize((1170,1200),Image.Resampling.NEAREST).save(context)
  write(str(context)+".derived.json",{"file":str(context),"sha256":sha(context),"source":ref(C["layoutReference"]),"sourceBox":box,"operation":"Layout-only crop enlarged 6x for readability; NEVER final game pixels","pixels":[1170,1200]},True)
 pure=Z/"guides"/f"{T}.tile-layout-only.png"
 if not pure.exists():
  layout.transform((1254,1254),Image.Transform.EXTENT,[v*1254/57344 for v in [49152,24576,53248,28672]],Image.Resampling.NEAREST).save(pure)
  write(str(pure)+".derived.json",{"file":str(pure),"sha256":sha(pure),"source":ref(C["layoutReference"]),"nativeGlobalBox":[49152,24576,53248,28672],"operation":"Layout-only coordinate crop, resampled to readable1254; NEVER final game pixels"},True)
 print(json.dumps({"coordinates":str(Z/"records"/f"{T}.coordinates.json"),"context":str(context),"tileGuide":str(pure)}))
def prep(p,top=None,left=None,bottom=None,base=None):
 coords=co(p);im=Image.open(C["layoutReference"]).convert("RGB").transform((N,N),Image.Transform.EXTENT,coords["overviewBox"],Image.Resampling.BICUBIC)
 baseRef=None
 if base:
  bp=Path(base);bp=bp if bp.is_absolute() else Z/"native"/bp
  im=Image.open(bp).convert("RGB");assert im.size==(N,N);baseRef=ref(bp,"existing native edit target at same coordinates")
 sources=[]
 for val,side in [(left,"left"),(bottom,"bottom"),(top,"top")]:
  if not val:continue
  path=Path(val);path=path if path.is_absolute() else Z/"native"/path
  q=Image.open(path);assert q.size==(N,N)
  m=re.match(r"r(\d{2})_c(\d{2})_p([1-4])([1-4])",path.name);assert m,("Neighbor filename needs explicit coordinate",str(path))
  tr,tc,sr,sc=map(int,m.groups());ng=[(tc-1)*4096+(sc-1)*1024-115,(tr-1)*4096+(sr-1)*1024-115]
  delta=[ng[i]-coords["nativeGlobalBox"][i] for i in [0,1]]
  assert delta=={"left":[-1024,0],"top":[0,-1024],"bottom":[0,1024]}[side],("Nonadjacent source",delta)
  crop={"left":[1024,0,N,N],"top":[0,1024,N,N],"bottom":[0,0,N,230]}[side]
  pasteAt=[0,1024] if side=="bottom" else [0,0]
  im.paste(q.convert("RGB").crop(crop),pasteAt)
  item={**ref(path,f"exact native {side}230px anchor"),"side":side,"sourceCropBox":crop,"targetPasteAt":pasteAt,"nativeGlobalOrigin":ng}
  sidecar=Path(str(path)+".generation.json")
  if sidecar.exists():item["provenanceRecord"]=ref(sidecar)
  sources.append(item)
 stamp=hashlib.sha256(im.tobytes()).hexdigest()[:16];gp=Z/"guides"/f"{p}.native-edge-layout-{stamp}.png"
 if not gp.exists():im.save(gp)
 plan={"schemaVersion":1,"patchId":p,"preparedAtUtc":now(),"coordinates":coords,"references":mandatory()+[ref(gp,"exact layout guide with 1:1 native edge anchors")],"nativeEdgeSources":sources,"baseNativeEditTarget":baseRef,"configSnapshot":read(CONFIG),"configSource":ref(CONFIG),"contract":ref(CONTRACT),"nativeSize":[N,N],"tool":"image_gen.imagegen","route":"builtin","actualModel":None,"actualQuality":None,"nativeResizePerformed":False}
 sidecar=Path(str(gp)+".derived.json")
 if not sidecar.exists():write(sidecar,{"file":str(gp),"sha256":sha(gp),"purpose":"layout guide only, NOT final pixels","operation":"Overview EXTENT bicubic crop OR existing native base, then opaque1:1 native230 strips; top owns corner","coordinates":coords,"sourceLayout":plan["references"][0],"baseNativeEditTarget":baseRef,"nativeEdgeSources":sources},True)
 plan["references"][3]["provenanceRecord"]=ref(sidecar)
 write(Z/"records"/f"{p}.plan.json",plan)
 print(json.dumps(plan,ensure_ascii=False))
def ingest(p,src,v):
 plan=read(Z/"records"/f"{p}.plan.json");dst=Z/"native"/f"{p}-{v}.png"
 pp=Z/"records"/f"{p}-{v}.prompt.txt";rp=Z/"records"/f"{p}-{v}.receipt.json";receipt=read(rp)
 assert receipt["tool"]=="image_gen.imagegen"
 assert pp.read_text(encoding="utf-8-sig")==receipt["request"]["prompt"]
 actual=receipt["request"]["referenced_image_paths"]
 assert actual==[a["path"] for a in plan["references"]],("Actual refs differ",actual)
 assert not dst.exists();shutil.copy2(src,dst);im=Image.open(dst)
 rec={**plan,"file":str(dst),"sha256":sha(dst),"width":im.width,"height":im.height,"format":im.format,"nativeSize":list(im.size),"generatedAt":None,"observedAtUtc":receipt["observedAtUtc"],"timeEvidence":"Observed tool return only; exact generation time undisclosed","submittedParameters":{"model":None,"quality":None},"submittedModel":None,"submittedQuality":None,"unverifiedReason":"Host-managed builtin exposes no model/quality selectors or returned version; actual values null","prompt":ref(pp),"receipt":ref(rp),"source":ref(src,"byte-for-byte host output copy"),"metadataKeys":list(im.info),"status":"candidate_pending_review","usable":False,"formalAccepted":False}
 write(str(dst)+".generation.json",rec,True)
 assert im.size==(N,N),("Native size mismatch, no resampling",im.size)
 qa=[]
 for e in plan["nativeEdgeSources"]:
  q=Image.open(e["path"]).convert("RGB");top=e["side"]=="top";bottom=e["side"]=="bottom"
  out=Image.new("RGB",(N,256) if top or bottom else (256,N))
  if bottom:out.paste(im.crop((0,1011,N,1139)),(0,0));out.paste(q.crop((0,115,N,243)),(0,128))
  elif top:out.paste(q.crop((0,1011,N,1139)),(0,0));out.paste(im.crop((0,115,N,243)),(0,128))
  else:out.paste(q.crop((1011,0,1139,N)),(0,0));out.paste(im.crop((115,0,243,N)),(128,0))
  qp=Z/"qa"/f"{p}-{v}-{e['side']}-native-seam.png";out.save(qp)
  write(str(qp)+".derived.json",{"file":str(qp),"sha256":sha(qp),"sources":[e,ref(dst)],"operation":"Exact native crop/paste QA no resizing","seamAxis":"y" if top or bottom else "x","seamLocalCoordinate":128},True)
  qa.append(str(qp))
 print(json.dumps({"native":str(dst),"sha256":sha(dst),"size":list(im.size),"qa":qa}))
def select(p,v,review):
 path=Z/"records"/f"{T}.working-selection.json";s=read(path)if path.exists()else{}
 np=Z/"native"/f"{p}-{v}.png";assert np.exists();s[p]=np.name;write(path,s)
 rp=Z/"records"/f"{p}-{v}.visual-review.json";write(rp,{"patchId":p,"native":ref(np),"reviewedAtUtc":now(),"review":review,"candidateSelected":True,"formalAccepted":False})
 write(Z/"records"/f"{T}.status.json",{"updatedAtUtc":now(),"generatedNativeCount":len(list((Z/"native").glob(T+"_p*.png.generation.json"))),"coveredCoreCount":len(s),"missingCoreCount":16-len(s),"selected":s,"candidate4kCount":0,"formalAcceptedCount":0,"lastReview":ref(rp)})
 print(json.dumps({"selected":p,"file":np.name,"coveredCoreCount":len(s)}))
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("op");a.add_argument("patch",nargs="?");a.add_argument("--top");a.add_argument("--left");a.add_argument("--bottom");a.add_argument("--base");a.add_argument("--source");a.add_argument("--version",default="v1");a.add_argument("--review");x=a.parse_args()
 if x.op=="init":init()
 elif x.op=="prepare":prep(x.patch,x.top,x.left,x.bottom,x.base)
 elif x.op=="ingest":ingest(x.patch,x.source,x.version)
 elif x.op=="select":select(x.patch,x.version,x.review)

