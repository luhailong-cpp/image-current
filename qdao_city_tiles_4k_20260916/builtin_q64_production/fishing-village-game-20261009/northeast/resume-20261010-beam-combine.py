from pathlib import Path
from PIL import Image
import json,hashlib,datetime
Z=Path(__file__).resolve().parent
P="resume-20261010-beam"
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {"path":str(p),"sha256":h(p)}
def record(p,img,sources,**extra):
 assert not p.exists(),str(p)
 img.save(p)
 j={"schemaVersion":1,"file":str(p),"sha256":h(p),"pixels":list(img.size),"derivedFrom":sources,"operation":"Opaque integer crop and paste of native pixels; no resizing, painting, feathering, blending, or resampling","formalAccepted":False,**extra}
 Path(str(p)+".derived.json").write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 return ref(p)
base=Z/"tiles/r06_c12.candidate.png"
a=Z/"native"/(P+"-A-v1.png");b=Z/"native"/(P+"-B-v1.png")
assert h(base)=="997d0f2d213d60610c5e92f3314da18efbc93131419ea7dd2167c6c69207ae56"
im=Image.open(base).copy();ia=Image.open(a);ib=Image.open(b)
assert ia.size==ib.size==(1254,1254)
origin=[45056,20480]
ab=[46405,21940,47659,23194];bb=[47179,21940,48433,23194]
sources=[ref(base),ref(a),ref(b)]
im.paste(ia,(ab[0]-origin[0],ab[1]-origin[1]));im.paste(ib,(bb[0]-origin[0],bb[1]-origin[1]))
contributions=[{"source":ref(a),"sourceCropBox":[0,0,774,1254],"globalBox":[46405,21940,47179,23194]},{"source":ref(b),"sourceCropBox":[0,0,1254,1254],"globalBox":bb}]
candidate=record(Z/"qa"/(P+"-AB-combined-candidate.png"),im,sources,globalBox=[45056,20480,49152,24576],nativeContributions=contributions)
x,y=1349,1460;w,hg=2028,1254
qa=[]
for side,box,axis in [
 ("object",(x-128,y-128,x+w+128,y+hg+128),None),
 ("union-left",(x-128,y-128,x+128,y+hg+128),"x"),
 ("union-right",(x+w-128,y-128,x+w+128,y+hg+128),"x"),
 ("union-top",(x-128,y-128,x+w+128,y+128),"y"),
 ("union-bottom",(x-128,y+hg-128,x+w+128,y+hg+128),"y")]:
 q=record(Z/"qa"/(P+"-AB-"+side+".png"),im.crop(box),sources,candidateCropBox=list(box),seamAxis=axis,seamLocalCoordinate=128 if axis else None)
 qa.append({"side":side,**q})
handoff={"schemaVersion":1,"observedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"native_repair_geometry_visually_passed_pending_independent_review","generatedCountThisWorker":2,"candidate":candidate,"baseCandidate":sources[0],"nativeContributions":contributions,"qa":qa,"actualModel":None,"actualQuality":None,"fullImageBordersIdentical":False,"geometryReview":{"A":"Complete lower rail between posts rebuilt; spurious double rectangle removed; lower rail extending into left neighbor preserved.","B":"Complete top rim and lower brace between corner and right post rebuilt. Top step removed, lower brace joined to right post; redundant stump removed.","outerBorders":"A left/top/bottom and B left/right/top/bottom reviewed at native scale: silhouettes and stone boundaries continuous. Minor texture/color differences remain; no blur applied. Final combined perimeter exported for independent root review.","formalAccepted":False},"originalSelectionModified":False,"originalCandidateModified":False}
(Z/"records"/(P+"-AB-handoff.json")).write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"candidate":candidate,"handoff":str(Z/"records"/(P+"-AB-handoff.json"))}))

