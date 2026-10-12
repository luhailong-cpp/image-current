from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
from datetime import datetime,timezone
R=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");D=R/"work-r03_c02/west-final";Q=D/"qa-final";Q.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding="utf8"));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(D/"repair2-assembly.json");a=np.asarray(Image.open(m["candidate"])).copy();ids=np.asarray(Image.open(m["sourceIdFile"])).copy()
em=read(R/"work-r03_c03/joint-final/joint-assembly.json");east=np.asarray(Image.open(em["candidate"]["file"]));ei=np.asarray(Image.open(em["sourceIdMap"]["file"]));v5=np.asarray(Image.open(R/"tiles/r03_c03.candidate-repair-v5.png"))
for source in em["sources"]:
 key=int(source["jointSourceId"])+500
 m["sources"][str(key)]={**source,"sourceId":key}
protected=np.any(east!=v5,axis=2);protected[-115:]=True;before=a[:,4096:].copy();a[:,4096:][protected]=east[protected];ids[:,4096:][protected]=ei[protected]+500
assert np.array_equal(a[:,4096:][protected],east[protected])
assert np.array_equal(a[-115:,4096:],east[-115:])
from finish_south_left import finish
m['southLeftObjectFinish']=finish(a,ids,m,D)
m.update(candidate=str(D/"final-pair.png"),sourceIdFile=str(D/"final-pair.source-id.png"))
Image.fromarray(a).save(m["candidate"]);Image.fromarray(ids).save(m["sourceIdFile"])
m.update(candidateSHA256=sha(m["candidate"]),sourceIdSHA256=sha(m["sourceIdFile"]),protectedEastChangedPixels=int(protected.sum()),protectedEastRestoredPixels=int(np.any(before[protected]!=east[protected],axis=1).sum()))
checks=[];cache={}
for key in np.unique(ids):
 s=m["sources"][str(key)];assert sha(s["file"])==s["sha256"];assert sha(s["generationRecord"])==s["generationRecordSha256"]
 src=np.asarray(Image.open(s["file"]));assert src.shape==(1254,1254,3)
 yy,xx=np.nonzero(ids==key);x,y,ex,ey=s["globalNativeBox"];sx=xx+4096-x;sy=yy+8192-y
 assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254))
 bad=int(np.any(a[yy,xx]!=src[sy,sx],axis=1).sum());assert bad==0
 checks.append({"sourceId":int(key),"pixels":int(len(yy)),"mismatches":bad})
m["finalProof"]={"pixels":33554432,"mismatches":0,"sources":checks}
artifacts=[]
for i,tile in enumerate(["r03_c02","r03_c03"]):
 p=D/(tile+".west-final.png");ip=D/(tile+".west-final.source-id.png");Image.fromarray(a[:,i*4096:(i+1)*4096]).save(p);Image.fromarray(ids[:,i*4096:(i+1)*4096]).save(ip)
 selected=set(int(k) for k in np.unique(ids[:,i*4096:(i+1)*4096]))
 r={"schemaVersion":1,"tile":tile,"createdAt":datetime.now(timezone.utc).isoformat(),"status":"candidate-pending-final-100percent-review","candidate":{"file":str(p),"sha256":sha(p)},"sourceIdMap":{"file":str(ip),"sha256":sha(ip),"coordinateFormula":"nativeX=tileX+globalCoreBox[0]-source.globalNativeBox[0]; nativeY=tileY+globalCoreBox[1]-source.globalNativeBox[1]"},"globalCoreBox":[4096+4096*i,8192,8192+4096*i,12288],"outputSize":[4096,4096],"sources":[s for k,s in m["sources"].items() if int(k) in selected],"formalAccepted":False,"internalAccepted":False,"eastWestBoundaryAccepted":False,"composition":{"resample":False,"feather":False,"colorRewrite":False,"nativePixelsVerified":16777216,"mismatches":0},"jointAssembly":str(D/"final-joint.assembly.json")}
 if i==1:
  changed=np.any(a[:,4096:]!=east,axis=2);assert not np.any(changed&protected)
  mask=D/"r03_c03.west-final.delta-mask.png";di=D/"r03_c03.west-final.delta-source-id.png"
  Image.fromarray(changed.astype(np.uint8)*255).save(mask);Image.fromarray(np.where(changed,ids[:,4096:],0).astype(np.uint16)).save(di)
  r.update(baseline=em["candidate"],deltaMask={"file":str(mask),"sha256":sha(mask)},deltaSourceIdMap={"file":str(di),"sha256":sha(di)},deltaPixels=int(changed.sum()),E3AndSouthProtectedPixels=int(protected.sum()),E3AndSouthProtectedMaskOverlap=0,bottom115ExactlyPreserved=True)
 rp=D/(tile+".west-final.assembly.json");rp.write_text(json.dumps(r,indent=2),encoding="utf8");artifacts.append({"file":str(rp),"sha256":sha(rp),"candidate":r["candidate"]})
m["tileArtifacts"]=artifacts;m["createdAt"]=datetime.now(timezone.utc).isoformat()
#24 actual internal seam segments, grouped without scaling by index.
w=a[:,:4096]
crops=[]
for j in range(4):
 sheet=Image.new("RGB",(990,1024))
 for k in range(1,4):
  box=[1024*k-165,1024*j,1024*k+165,1024*(j+1)]
  sheet.paste(Image.fromarray(w).crop(box),((k-1)*330,0))
  crops.append({"file":str(Q/f"internal-v-{j+1}.png"),"panel":k,"tileBox":box,"nativeScale":1})
 sheet.save(Q/f"internal-v-{j+1}.png")
 sheet=Image.new("RGB",(1024,990))
 for k in range(1,4):
  box=[1024*j,1024*k-165,1024*(j+1),1024*k+165]
  sheet.paste(Image.fromarray(w).crop(box),(0,(k-1)*330))
  crops.append({"file":str(Q/f"internal-h-{j+1}.png"),"panel":k,"tileBox":box,"nativeScale":1})
 sheet.save(Q/f"internal-h-{j+1}.png")
sheet=Image.new("RGB",(1380,1380))
for j in range(1,4):
 for k in range(1,4):
  box=[1024*k-230,1024*j-230,1024*k+230,1024*j+230]
  sheet.paste(Image.fromarray(w).crop(box),((k-1)*460,(j-1)*460))
sheet.save(Q/"internal-nine-junctions.png")
for j in range(4):
 Image.fromarray(a[j*1024:(j+1)*1024,3696:4496]).save(Q/f"external-{j+1}.png")
for name,box in [("roof-right",[8580,8192,8890,9370]),("roof-left",[7480,8192,7790,9370]),("roof-bottom",[7440,9100,8890,9430]),("M1",[4750,8192,5350,8680]),("G1",[4800,9050,5260,9550]),("M2",[6420,9780,7140,10950]),("E2-bottom",[7660,12010,9020,12288]),("E2-right",[8700,11010,9050,12288])]:
 p=Q/(name+".png");Image.fromarray(a).crop((box[0]-4096,box[1]-8192,box[2]-4096,box[3]-8192)).save(p);crops.append({"file":str(p),"globalBox":box,"nativeScale":1})
m["qaCropManifest"]=crops
(D/"final-joint.assembly.json").write_text(json.dumps(m,indent=2),encoding="utf8")
print(json.dumps({"proofPixels":33554432,"mismatches":0,"sourceCount":len(checks),"protectedEastPixels":int(protected.sum()),"protectedRestored":m["protectedEastRestoredPixels"],"artifacts":artifacts}))

