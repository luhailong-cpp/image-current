"""Export r07_c13 north/west full4096 boundaries as native1024 segments."""
from pathlib import Path
import json,hashlib,datetime
from PIL import Image
Z=Path(__file__).resolve().parent;T="r07_c13"
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {"path":str(Path(p).resolve()),"sha256":sha(p)}
def write(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
s=read(Z/"records"/f"{T}.working-selection.json")
assert len(s)==16
outdir=Z/"qa"/T;outdir.mkdir(exist_ok=True)
manifest={"tile":T,"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"method":"Native integer crop/paste only;1024px segments cover each entire4096 shared edge","formalAccepted":False,"visualReview":"pending","edges":[]}
for side in ["top","left"]:
 full=Image.new("RGB",(4096,256)if side=="top"else(256,4096))
 for i in range(1,5):
  p=f"{T}_p1{i}"if side=="top"else f"{T}_p{i}1"
  own=Z/"native"/s[p];rec=read(str(own)+".generation.json")
  if side=="left":
   anchor=Z/"native"/f"r07_c12_p{i}4-{'v2' if i in [2,4] else 'v1'}.png"
  else:
   anchors=[x for x in rec["nativeEdgeSources"]if x["side"]==side];assert len(anchors)==1
   anchor=Path(anchors[0]["path"]);assert sha(anchor)==anchors[0]["sha256"]
  a,b=Image.open(anchor),Image.open(own);assert a.size==b.size==(1254,1254)
  seg=Image.new("RGB",(1024,256)if side=="top"else(256,1024))
  if side=="top":
   seg.paste(a.crop((115,1011,1139,1139)),(0,0));seg.paste(b.crop((115,115,1139,243)),(0,128));full.paste(seg,((i-1)*1024,0))
  else:
   seg.paste(a.crop((1011,115,1139,1139)),(0,0));seg.paste(b.crop((115,115,243,1139)),(128,0));full.paste(seg,(0,(i-1)*1024))
  sp=outdir/f"external-{side}-segment{i}.native-1to1.png";assert not sp.exists();seg.save(sp)
  manifest["edges"].append({"side":side,"segment":i,"sources":[ref(anchor),ref(own)],"output":ref(sp),"pixels":list(seg.size),"completeSharedEdgePixels":1024,"seamLocalCoordinate":128,"visualReview":"pending"})
 fp=outdir/f"external-{side}-full4096.native-1to1.png";assert not fp.exists();full.save(fp)
 manifest.setdefault("fullEdges",[]).append({"side":side,"output":ref(fp),"pixels":list(full.size),"completeSharedEdgePixels":4096,"reviewSegments":4})
write(outdir/"external-boundaries.manifest.json",manifest)
print(json.dumps({"manifest":str(outdir/"external-boundaries.manifest.json"),"nativeSegments":8,"fullBoundaryPixelsEach":4096}))

