from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
from datetime import datetime,timezone
T=Path(__file__).resolve().parents[1];D=Path(__file__).resolve().parent;O=D/"delivery";O.mkdir(exist_ok=True);Q=O/"qa";Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):
 im=Image.open(p);return {"file":str(p),"sha256":sha(p),"pixels":list(im.size),"mode":im.mode}
def read(p):return json.loads(p.read_text(encoding="utf8"))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf8")
base=T/"pipeline/output/94ddb3ea62a89ee2/r11_c06.candidate.png";context=T/"pipeline/output/94ddb3ea62a89ee2/r11_c06.candidate.context.png";current=D/"09-top-right-tone/r11_c06.repaired.candidate.png"
native=Image.open(current).convert("RGB");assert native.size==(4096,4096)
candidate=O/"r11_c06.internal-repaired.candidate.png";shutil.copyfile(current,candidate)
c=Image.open(context).convert("RGB");assert c.size==(4326,4326);c.paste(native,(115,115));cp=O/"r11_c06.internal-repaired.context.png";c.save(cp,optimize=True)
a=np.array(native);old=np.array(Image.open(base).convert("RGB"));ctx=np.array(c);oldctx=np.array(Image.open(context).convert("RGB"))
ed=np.zeros((4096,4096),bool);ed[0]=True;ed[-1]=True;ed[:,0]=True;ed[:,-1]=True
assert np.array_equal(a[ed],old[ed]);outer=np.ones((4326,4326),bool);outer[115:4211,115:4211]=False;assert np.array_equal(ctx[outer],oldctx[outer]);assert np.array_equal(ctx[115:4211,115:4211],a)
selected=["03-center-joints","04-left-joints","05-bottom-stub","08-stone-foot-tone","09-top-right-tone"];rejected=["01-step-terminal","02-step-terminal-retry","06-bottom-step-focused","07-bottom-step-width"]
chain=[];prior=sha(base)
for id in selected:
 p=D/id/"assembly.json";d=read(p);assert d["input"]["sha256"]==prior;prior=d["output"]["sha256"];chain.append({"id":id,"assembly":str(p),"assemblySha256":sha(p),"generation":str(D/id/"generation.json"),"generationSha256":sha(D/id/"generation.json"),"candidateBox":d["candidateBox"]})
assert prior==sha(candidate)
rejects=[]
for id in rejected:
 d=D/id;n=d/"rejected-native.png";q=read(d/"request.json");r=read(d/"receipt.json");rec={"id":id,"output":meta(n),"request":str(d/"request.json"),"requestSha256":sha(d/"request.json"),"receipt":str(d/"receipt.json"),"receiptSha256":sha(d/"receipt.json"),"status":"rejected","reason":r["reason"],"actualModel":None,"actualQuality":None,"route":"builtin_image_gen","resizedAfterGeneration":False};write(d/"generation.json",rec);rejects.append(rec)
qa=[]
def crop(name,box):
 p=Q/name;native.crop(box).save(p,optimize=True);qa.append(dict(meta(p),box=box));return p
for x in [1024,2048,3072]:crop(f"vertical_x{x}.png",[x-119,0,x+119,4096])
for y in [1024,2048,3072]:crop(f"horizontal_y{y}.png",[0,y-119,4096,y+119])
atlas=Image.new("RGB",(1536,1536))
for j,y in enumerate([1024,2048,3072]):
 for i,x in enumerate([1024,2048,3072]):
  im=native.crop([x-256,y-256,x+256,y+256]);im.save(Q/f"intersection_x{x}_y{y}.png",optimize=True);atlas.paste(im,(i*512,j*512))
atlas.save(Q/"nine-intersections-native-atlas.png",optimize=True)
for name,box in {"step-terminal-pending.png":[100,1200,750,1650],"stone-foot-repaired.png":[750,850,1300,1300],"top-wall-repaired.png":[2750,0,3500,450],"left-joints-repaired.png":[900,2780,1450,3754],"central-joints-repaired.png":[1700,2800,2500,3980]}.items():crop(name,box)
assembly={"schemaVersion":1,"tile":"r11_c06","createdAtUtc":datetime.now(timezone.utc).isoformat(),"candidate":meta(candidate),"context":meta(cp),"baseline":meta(base),"baselineContext":meta(context),"selectedRepairChain":chain,"newSuccessfulBuiltinImages":9,"newSelectedLocalRepairs":5,"newRejectedImages":4,"rejectedRepairs":rejects,"allFourTileOuterEdgesByteIdentical":True,"outer115ContextHaloByteIdentical":True,"contextCoreEqualsCandidate":True,"noSourceResampling":True,"maximumFeatherRadiusPixels":2,"actualModel":None,"actualQuality":None,"internalPassed":False,"externalPassed":False,"formalAccepted":False,"qaCrops":qa,"next":"Parent merges separate cross-edge proposals; G01 and remaining style/layout issues are open."}
write(O/"assembly.json",assembly);print(json.dumps({k:assembly[k] for k in ["candidate","context","newSuccessfulBuiltinImages","newSelectedLocalRepairs","newRejectedImages"]}))

