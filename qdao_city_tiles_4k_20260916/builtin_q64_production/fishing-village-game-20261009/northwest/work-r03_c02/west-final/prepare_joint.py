from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");D=R/"work-r03_c02/west-final";W=R/"work-r03_c02"
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ns={"__file__":str(W/"east_gate_qa.py")}
exec(compile((W/"east_gate_qa.py").read_text().split("prefix=W/'qa/east-full-height-gate'")[0],str(W/"east_gate_qa.py"),"exec"),ns)
pair=ns["pair"].copy(); ids=ns["ids"].astype(np.uint16)
sources={}
for key,s in ns["allsource"].items():
 gp=s["file"]+".generation.json";g=read(gp)
 sources[int(key)]={"sourceId":int(key),"file":s["file"],"sha256":s["sha256"],"globalNativeBox":s["box"],"generationRecord":gp,"generationRecordSha256":sha(gp)}
em=read(R/"work-r03_c03/joint-final/joint-assembly.json")
ep=np.asarray(Image.open(em["candidate"]["file"])); ei=np.asarray(Image.open(em["sourceIdMap"]["file"]))
base=np.asarray(Image.open(R/"tiles/r03_c03.candidate-repair-v5.png"))
changed=np.any(ep!=base,axis=2)
pair[:,4096:][changed]=ep[changed];ids[:,4096:][changed]=ei[changed]+500
for s in em["sources"]:
 key=int(s["jointSourceId"])+500
 if key in np.unique(ids):
  sources[key]={**s,"sourceId":key};sources[key].pop("jointSourceId",None)
review=read(W/"qa/e3-repair/e3-repair-review.json")
west=review["optionalWestContribution"];arr=np.asarray(Image.open(west["rgbFile"]));im=np.asarray(Image.open(west["sourceIdFile"]))
box=west["globalBox"]; yy,xx=np.nonzero((im>0)&(np.indices(im.shape)[1]+box[0]<8192))
gy=yy+box[1]-8192;gx=xx+box[0]-4096
pair[gy,gx]=arr[yy,xx];ids[gy,gx]=im[yy,xx].astype(np.uint16)+500
assert len(yy)==105775
checks=[]
for key in np.unique(ids):
 s=sources[int(key)];a=np.asarray(Image.open(s["file"]));yy,xx=np.nonzero(ids==key);bx,by,ex,ey=s["globalNativeBox"];sx=xx+4096-bx;sy=yy+8192-by
 assert np.array_equal(pair[yy,xx],a[sy,sx]),key
 checks.append({"sourceId":int(key),"pixels":int(len(yy))})
Image.fromarray(pair).save(D/"joint0-pair.png");Image.fromarray(ids).save(D/"joint0-source-id.png")
meta={"globalBox":[4096,8192,12288,12288],"candidate":str(D/"joint0-pair.png"),"candidateSHA256":sha(D/"joint0-pair.png"),"sourceIdFile":str(D/"joint0-source-id.png"),"sourceIdSHA256":sha(D/"joint0-source-id.png"),"sources":sources,"sourceCoordinates":"global x/y offset with original1254 native size; no translation/resizing","proofPixels":sum(c["pixels"] for c in checks),"mismatches":0,"counts":checks,"E3WestPixelsAdded":105775,"E3AndSouthExistingChangedPixelsPreserved":int(changed.sum()),"baselineEast":em["candidate"],"baselineEastID":em["sourceIdMap"],"trueOverlapWidth":230,"roofBridgeNative":"r03_c02_c03_roof_bridge_v01","visualQA":"pending"}
(D/"joint0-assembly.json").write_text(json.dumps(meta,indent=2),encoding="utf8")
for i in range(4):
 Image.fromarray(pair[1024*i:1024*(i+1),3696:4496]).save(D/f"joint0-seam-{i+1}.png")
print(json.dumps({"proofPixels":meta["proofPixels"],"sources":len(checks),"changedFromInitial":int(np.any(pair!=np.asarray(Image.open(D/"initial-pair.png")),axis=2).sum())}))

