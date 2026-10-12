from PIL import Image
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast");T="r05_c14";V="v4";N=1254;H=115;K=1024;O=(53248,16384)
Q=Z/"qa"/(T+"-"+V);Q.mkdir(exist_ok=True);D=Z/"native-derived";D.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p,role):return {"path":str(Path(p).resolve()).replace("\\","/"),"sha256":sha(p),"role":role}
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
S=["cf450f0afe784b4700f2dfc19b3af35867765403e8f1d81741e78b3116583d42","db47c3d1699c4163734fb4cd155cecc8529ea6adb56f3e7533d375764cf9152c","c1ab2e50b271e5c5590a92fe68bd6cf7d2c64cbd0d369b25b4ff5c6619033b63"]
actuals={}
def validate_actual(path):
 path=Path(path);gp=Path(str(path)+".generation.json");g=read(gp);assert sha(path)==g["sha256"];im=Image.open(path);assert im.size==(N,N)
 pr=Path(g["prompt"]["path"]);rr=Path(g["receipt"]["path"]);assert sha(pr)==g["prompt"]["sha256"];assert sha(rr)==g["receipt"]["sha256"]
 rq=read(rr)["request"];refs=g["references"];assert [v["path"] for v in refs]==rq["referenced_image_paths"]
 assert all(sum(v["sha256"]==h for v in refs)==1 for h in S)
 for ref in refs:assert sha(ref["path"])==ref["sha256"]
 assert g.get("actualModel") is None and g.get("actualQuality") is None and not g.get("nativeResizePerformed")
 a=dict(rec(path,"actual native generated source"),nativeSize=[N,N],generationRecord=rec(gp,"actual generation evidence"),actualPrompt=rec(pr,"actual submitted prompt"),actualReceipt=rec(rr,"actual request/return receipt"),actualRefs=refs,actualModel=None,actualQuality=None)
 actuals[str(path.resolve())]=a;return a
sel=read(Z/"records"/"r05_c14.selection-proposed-v1.json")["patches"];assert len(sel)==16
baseSel=dict(sel);base={p:Z/"native"/fn for p,fn in sel.items()}
for path in base.values():validate_actual(path)
bridge=Z/"native/r05_c14_bridge01-v1.png";br=validate_actual(bridge);bi=Image.open(bridge).convert("RGB")
B=[55808,18714,57062,19968];R=[56179,19085,56691,19597];repairs=[];derived={}
for p in ["r05_c14_p33","r05_c14_p34","r05_c14_p43","r05_c14_p44"]:
 r,c=int(p[-2]),int(p[-1]);x=O[0]+(c-1)*K-H;y=O[1]+(r-1)*K-H;nb=[x,y,x+N,y+N]
 inter=[max(x,R[0]),max(y,R[1]),min(x+N,R[2]),min(y+N,R[3])]
 assert inter[0]<inter[2] and inter[1]<inter[3]
 crop=[inter[0]-B[0],inter[1]-B[1],inter[2]-B[0],inter[3]-B[1]];dst=[inter[0]-x,inter[1]-y,inter[2]-x,inter[3]-y]
 out=D/(base[p].stem+".bridge01-v1.png");assert not out.exists()
 im=Image.open(base[p]).convert("RGB");im.paste(bi.crop(crop),(dst[0],dst[1]));im.save(out)
 d=dict(rec(out,"native1:1 exact composition; NOT a new generated output"),patch=p,size=[N,N],nativeGlobalBox=nb,formalAccepted=False,operation="only original native full-copy plus opaque integer bridge crop/paste; no resize/paint/feather",base=actuals[str(base[p].resolve())],bridge=br,bridgeWorldBox=B,repairWindowWorldBox=R,contributionGlobalBox=inter,bridgeSourceCropBox=crop,patchDestinationBox=dst,nativeResizePerformed=False)
 write(str(out)+".derived.json",d);derived[p]=d;repairs.append(d);sel[p]="../native-derived/"+out.name
imgs={};sources=[];tile=Image.new("RGB",(4096,4096))
for r in range(1,5):
 for c in range(1,5):
  p=f"{T}_p{r}{c}";path=(Z/"native"/sel[p]).resolve();im=Image.open(path).convert("RGB");assert im.size==(N,N);imgs[(r,c)]=(path,im)
  at=[(c-1)*K,(r-1)*K];crop=[H,H,H+K,H+K];tile.paste(im.crop(crop),at)
  s=dict(rec(path,"selected exact native core contribution"),patch=p,cropBox=crop,pasteAt=at,worldCoreBox=[O[0]+at[0],O[1]+at[1],O[0]+at[0]+K,O[1]+at[1]+K],nativeSize=[N,N])
  if p in derived:s.update(sourceType="exact_native_composition",compositionRecord=rec(str(path)+".derived.json","source/destination/global crop provenance"),actualNativeGenerationSources=[derived[p]["base"],br])
  else:s.update(sourceType="native_generated",actualNativeGenerationSources=[actuals[str(path)]])
  sources.append(s)
cp=Z/"tiles"/(T+".candidate-"+V+".png");assert not cp.exists();tile.save(cp)
write(str(cp)+".derived.json",{"purpose":"complete4096 candidate pending independent root review","operation":"16 exact integer1024 core crop/paste,4 native1:1 source compositions from one returned native1254 bridge; no resize/paint/feather","size":[4096,4096],"sha256":sha(cp),"formalAccepted":False,"sources":sources,"actualNativeGenerationSources":list(actuals.values()),"repairContributions":repairs})
manifest={"tile":T,"version":V,"createdAtUtc":datetime.now(timezone.utc).isoformat(),"candidate":rec(cp,"exact assembled4096 candidate"),"candidateSize":[4096,4096],"selection":sel,"baselineSelection":baseSel,"nativeSources":sources,"internalSeams":[],"externalSeams":[],"junctions":[],"externalJunctions":[],"repairCutBoundaries":[],"quadrants":[],"unreviewedBoundaries":["north neighbor r04_c14 absent"],"eastBoundary":"full-map outer edge; no east neighbor"}
def seam(a,b,kind,name,external=False):
 pa,ia=a;pb,ib=b
 if kind=="horizontal":ca=[H,H+K-128,H+K,H+K];cb=[H,H,H+K,H+128];at1=[0,0];at2=[0,128];out=Image.new("RGB",(K,256))
 else:ca=[H+K-128,H,H+K,H+K];cb=[H,H,H+128,H+K];at1=[0,0];at2=[128,0];out=Image.new("RGB",(256,K))
 out.paste(ia.crop(ca),at1);out.paste(ib.crop(cb),at2);p=Q/(name+".png");out.save(p)
 data={"purpose":"native1:1 true core seam QA","orientation":kind,"size":list(out.size),"seamCoordinate":128,"resized":False,"sources":[dict(rec(pa,"north/west source"),cropBox=ca,pasteAt=at1),dict(rec(pb,"south/east source"),cropBox=cb,pasteAt=at2)]};write(str(p)+".derived.json",data);manifest["externalSeams" if external else "internalSeams"].append(dict(rec(p,"native core seam QA"),**data))
for r in range(1,5):
 for c in range(1,4):seam(imgs[(r,c)],imgs[(r,c+1)],"vertical",f"internal-p{r}{c}-p{r}{c+1}")
for r in range(1,4):
 for c in range(1,5):seam(imgs[(r,c)],imgs[(r+1,c)],"horizontal",f"internal-p{r}{c}-p{r+1}{c}")
south={};west={}
for c in range(1,5):
 path=Z/"native"/f"r06_c14_p1{c}-v1.png";south[c]=(path,Image.open(path).convert("RGB"));seam(imgs[(4,c)],south[c],"horizontal",f"external-south-p4{c}-r06-c14-p1{c}",True)
for r in range(1,5):
 path=Z/"native"/f"r05_c13_p{r}4-v1.png";west[r]=(path,Image.open(path).convert("RGB"));seam(west[r],imgs[(r,1)],"vertical",f"external-west-r05-c13-p{r}4-p{r}1",True)
def tile_crop(name,box,key,role):
 p=Q/(name+".png");tile.crop(box).save(p);d=dict(rec(p,role),source=rec(cp,"candidate"),cropBox=box,size=[box[2]-box[0],box[3]-box[1]],resized=False);write(str(p)+".derived.json",d);manifest[key].append(d)
for r in range(1,4):
 for c in range(1,4):
  x,y=c*K,r*K;tile_crop(f"junction-r{r+1}c{c+1}",[x-256,y-256,x+256,y+256],"junctions","native four-core junction")
for r in range(2):
 for c in range(2):tile_crop(f"quadrant-{r+1}{c+1}-native",[c*2048,r*2048,(c+1)*2048,(r+1)*2048],"quadrants","native quadrant crop")
rb=[R[0]-O[0],R[1]-O[1],R[2]-O[0],R[3]-O[1]]
for side,box in [("top",[rb[0],rb[1]-128,rb[2],rb[1]+128]),("bottom",[rb[0],rb[3]-128,rb[2],rb[3]+128]),("left",[rb[0]-128,rb[1],rb[0]+128,rb[3]]),("right",[rb[2]-128,rb[1],rb[2]+128,rb[3]])]:
 tile_crop("repair-cut-"+side,box,"repairCutBoundaries","native1:1 bridge crop boundary QA")
 p=Q/("repair-cut-"+side+"-baseline-v1.png");Image.open(Z/"tiles/r05_c14.candidate-v1.png").crop(box).save(p);write(str(p)+".derived.json",{"purpose":"native1:1 baseline comparison ONLY","source":rec(Z/"tiles/r05_c14.candidate-v1.png","baseline"),"cropBox":box,"resized":False})
def four_junction(name,entries):
 out=Image.new("RGB",(512,512));rs=[]
 for path,im,box,at in entries:out.paste(im.crop(box),at);rs.append(dict(rec(path,"native neighboring core"),cropBox=box,pasteAt=list(at)))
 p=Q/(name+".png");out.save(p);d=dict(rec(p,"native1:1 external four-core junction"),size=[512,512],resized=False,sources=rs);write(str(p)+".derived.json",d);manifest["externalJunctions"].append(d)
tl=[883,883,1139,1139];tr=[115,883,371,1139];bl=[883,115,1139,371];brbox=[115,115,371,371]
for c in range(1,4):four_junction(f"external-junction-south-c{c+1}",[( *imgs[(4,c)],tl,(0,0)),(*imgs[(4,c+1)],tr,(256,0)),(*south[c],bl,(0,256)),(*south[c+1],brbox,(256,256))])
for r in range(1,4):four_junction(f"external-junction-west-r{r+1}",[(*west[r],tl,(0,0)),(*imgs[(r,1)],tr,(256,0)),(*west[r+1],bl,(0,256)),(*imgs[(r+1,1)],brbox,(256,256))])
swp=Z/"native/r06_c13_p14-v1.png";swi=Image.open(swp).convert("RGB")
four_junction("external-junction-southwest",[(*west[4],tl,(0,0)),(*imgs[(4,1)],tr,(256,0)),(swp,swi,bl,(0,256)),(*south[1],brbox,(256,256))])
preview=Z/"tiles"/(T+".candidate-"+V+".preview-1024.png");tile.resize((1024,1024),Image.Resampling.LANCZOS).save(preview);write(str(preview)+".derived.json",{"purpose":"preview ONLY, never final artwork","source":rec(cp,"candidate"),"operation":"downscale4096 to1024","resized":True})
prior=read(Z/"qa/r05_c14-v1/manifest.json");unchanged=[];changed=[]
for key in ["internalSeams","externalSeams","junctions"]:
 old={Path(e["path"]).name:e["sha256"] for e in prior[key]}
 for e in manifest[key]:(unchanged if old.get(Path(e["path"]).name)==e["sha256"] else changed).append(e["path"])
manifest["unchangedQAFromV1"]=unchanged;manifest["changedQAFromV1"]=changed
write(Q/"manifest.json",manifest);write(Q/"provenance-validation.json",{"status":"mechanical_provenance_passed","formalAccepted":False,"all16CoreCoordinates":True,"actualNativeGeneratedSources":len(actuals),"sourceCompositionCount":4,"requiredStyleRefsActuallySubmittedEachActualGeneration":True,"allImagePromptReceiptReferenceHashesVerified":True,"noResizePaintFeatherFinal":True,"actualModel":None,"actualQuality":None,"nativeGenerationEvidence":list(actuals.values())})
write(Z/"records"/"r05_c14.selection-proposed-v4.json",{"tile":T,"status":"complete_candidate_for_independent_review","formalAccepted":False,"candidate":rec(cp,"bridge repaired candidate"),"patches":sel,"baselinePatches":baseSel,"sources":sources,"bridge":br,"repairContributions":repairs,"qaManifest":rec(Q/"manifest.json","native QA manifest")})
print(json.dumps({"candidate":rec(cp,"candidate"),"selectedCoreCoordinates":16,"actualNativeGenerationSources":len(actuals),"nativeCompositions":4,"internalSeams":len(manifest["internalSeams"]),"externalSeams":len(manifest["externalSeams"]),"externalJunctions":len(manifest["externalJunctions"]),"repairCutBoundaries":len(manifest["repairCutBoundaries"]),"unchangedQA":len(unchanged),"changedQA":changed},ensure_ascii=False))

