from PIL import Image
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast"); T="r05_c14"; N=1254; H=115; K=1024; O=(53248,16384)
Q=Z/"qa"/f"{T}-v1"; Q.mkdir(exist_ok=True); (Z/"tiles").mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def rec(p,role):return {"path":str(Path(p).resolve()).replace("\\","/"),"sha256":sha(p),"role":role}
sel=json.loads((Z/"records"/f"{T}.working-selection.json").read_text(encoding="utf-8-sig")); assert len(sel)==16
imgs={}; sources=[]; prov=[]
tile=Image.new("RGB",(4096,4096))
for r in range(1,5):
 for c in range(1,5):
  p=f"{T}_p{r}{c}"; path=Z/"native"/sel[p]; im=Image.open(path).convert("RGB"); assert im.size==(N,N); imgs[(r,c)]=(path,im)
  at=[(c-1)*K,(r-1)*K]; crop=[H,H,H+K,H+K]; tile.paste(im.crop(crop),at)
  gen=Path(str(path)+".generation.json"); d=json.loads(gen.read_text(encoding="utf-8-sig")); assert d["sha256"]==sha(path)
  prompt=Path(d["prompt"]["path"]); receipt=Path(d["receipt"]["path"]); rr=json.loads(receipt.read_text(encoding="utf-8-sig")); assert sha(prompt)==d["prompt"]["sha256"]; assert sha(receipt)==d["receipt"]["sha256"]
  actual=rr["request"]["referenced_image_paths"]; assert len(actual)>=3
  reqrefs=d["references"]; assert [v["sha256"] for v in reqrefs[:3]]==["cf450f0afe784b4700f2dfc19b3af35867765403e8f1d81741e78b3116583d42","db47c3d1699c4163734fb4cd155cecc8529ea6adb56f3e7533d375764cf9152c","c1ab2e50b271e5c5590a92fe68bd6cf7d2c64cbd0d369b25b4ff5c6619033b63"]
  for v in reqrefs: assert sha(v["path"])==v["sha256"]
  assert d.get("actualModel") is None and d.get("actualQuality") is None
  source=dict(rec(path,"selected native contribution"),patch=p,cropBox=crop,pasteAt=at,worldCoreBox=[O[0]+at[0],O[1]+at[1],O[0]+at[0]+K,O[1]+at[1]+K],nativeSize=[N,N],generationRecord=rec(gen,"actual native generation provenance"),actualPrompt=rec(prompt,"actual prompt"),actualReceipt=rec(receipt,"actual request and return receipt"),actualRefs=reqrefs)
  sources.append(source); prov.append({"patch":p,"nativeSize":list(im.size),"outputHashVerified":True,"promptHashVerified":True,"receiptHashVerified":True,"actualReferenceHashesVerified":True,"threeRequiredStyleRefsActuallySubmitted":True,"actualModel":None,"actualQuality":None,"nativeResizePerformed":False})
cp=Z/"tiles"/f"{T}.candidate-v1.png"; assert not cp.exists(); tile.save(cp)
write(str(cp)+".derived.json",{"purpose":"4096 candidate, not formal accepted","operation":"only exact integer core crop[115,115,1139,1139] and opaque paste; no resize/paint/feather","sources":sources,"size":[4096,4096],"sha256":sha(cp),"formalAccepted":False})
manifest={"tile":T,"createdAtUtc":datetime.now(timezone.utc).isoformat(),"candidate":rec(cp,"4096 exact core assembled candidate"),"candidateSize":[4096,4096],"selection":sel,"nativeSources":sources,"internalSeams":[],"externalSeams":[],"junctions":[],"quadrants":[],"unreviewedBoundaries":["north neighbor r04_c14 missing"],"eastBoundary":"outermap edge worldX57344; no required east neighbor"}
def seam(a,b,kind,name,external=False):
 pa,ia=a; pb,ib=b
 if kind=="horizontal":
  ca=[H,H+K-128,H+K,H+K]; cb=[H,H,H+K,H+128]; at1=[0,0];at2=[0,128]; out=Image.new("RGB",(K,256))
 else:
  ca=[H+K-128,H,H+K,H+K]; cb=[H,H,H+128,H+K]; at1=[0,0];at2=[128,0]; out=Image.new("RGB",(256,K))
 out.paste(ia.crop(ca),at1); out.paste(ib.crop(cb),at2); p=Q/(name+".png");out.save(p)
 data={"purpose":"native1:1 core seam QA only","orientation":kind,"size":list(out.size),"seamCoordinate":128,"resized":False,"sources":[dict(rec(pa,"north or west native"),cropBox=ca,pasteAt=at1),dict(rec(pb,"south or east native"),cropBox=cb,pasteAt=at2)]};write(str(p)+".derived.json",data)
 entry=dict(rec(p,"native1:1 core seam QA"),**data);manifest["externalSeams" if external else "internalSeams"].append(entry)
for r in range(1,5):
 for c in range(1,4):seam(imgs[(r,c)],imgs[(r,c+1)],"vertical",f"internal-p{r}{c}-p{r}{c+1}")
for r in range(1,4):
 for c in range(1,5):seam(imgs[(r,c)],imgs[(r+1,c)],"horizontal",f"internal-p{r}{c}-p{r+1}{c}")
for c in range(1,5):
 path=Z/"native"/f"r06_c14_p1{c}-v1.png"; seam(imgs[(4,c)],(path,Image.open(path).convert("RGB")),"horizontal",f"external-south-p4{c}-r06-c14-p1{c}",True)
for r in range(1,5):
 path=Z/"native"/f"r05_c13_p{r}4-v1.png"; seam((path,Image.open(path).convert("RGB")),imgs[(r,1)],"vertical",f"external-west-r05-c13-p{r}4-p{r}1",True)
for r in range(1,4):
 for c in range(1,4):
  x,y=c*K,r*K; box=[x-256,y-256,x+256,y+256]; p=Q/f"junction-r{r+1}c{c+1}.png";tile.crop(box).save(p);e=dict(rec(p,"native1:1 assembled four-core junction"),cropBox=box,size=[512,512],resized=False,source=rec(cp,"assembled candidate"));write(str(p)+".derived.json",e);manifest["junctions"].append(e)
for r in range(2):
 for c in range(2):
  box=[c*2048,r*2048,(c+1)*2048,(r+1)*2048];p=Q/f"quadrant-{r+1}{c+1}-native.png";tile.crop(box).save(p);e=dict(rec(p,"native quadrant crop"),cropBox=box,size=[2048,2048],resized=False,source=rec(cp,"candidate"));write(str(p)+".derived.json",e);manifest["quadrants"].append(e)
preview=Z/"tiles"/f"{T}.candidate-v1.preview-1024.png";tile.resize((1024,1024),Image.Resampling.LANCZOS).save(preview);write(str(preview)+".derived.json",{"purpose":"preview ONLY; never final art","operation":"downscale4096 to1024 for overview","source":rec(cp,"candidate"),"resized":True})
write(Q/"manifest.json",manifest);write(Q/"provenance-validation.json",{"status":"mechanical_provenance_passed","formalAccepted":False,"tile":T,"all16CoreCoordinates":True,"noResizeFinalArt":True,"requiredRefsActuallySubmittedEachPatch":True,"patches":prov})
write(Z/"records"/f"{T}.selection-proposed-v1.json",{"tile":T,"status":"complete_candidate_for_independent_review","formalAccepted":False,"candidate":rec(cp,"complete candidate"),"patches":sel,"sources":sources,"qaManifest":rec(Q/"manifest.json","native QA manifest")})
print(json.dumps({"candidate":rec(cp,"candidate"),"preview":str(preview),"qa":str(Q),"internalSeams":len(manifest["internalSeams"]),"externalSeams":len(manifest["externalSeams"]),"junctions":len(manifest["junctions"]),"coreCount":16},ensure_ascii=False))

