from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json,hashlib,sys
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";sys.path.insert(0,str(B.parent/"pipeline-tools"));from quilt import minimum_seam
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
Af=D/"integrated-local-v04/assembly.json";A=json.loads(Af.read_text());base=np.array(Image.open(A["contextOutput"]["file"]).convert("RGB"));ctx=base.copy();union=np.zeros(base.shape[:2],bool);props=[]
for attempt in ["roof-vertical-join-v01","blue-border-south-join-v01"]:
 f=D/attempt;q=json.loads((f/"request.json").read_text());rec=json.loads((f/"receipt.json").read_text())
 old=np.array(Image.open(f/"input.png").convert("RGB"));new=np.array(Image.open(f/"native.png").convert("RGB"));m=np.zeros((1254,1254),bool)
 if attempt.startswith("roof"):
  x0,y0,x1,y1=300,430,1000,1220;cx0,cy0,cx1,cy1=480,490,820,1130
  left=minimum_seam(old[y0:y1,x0:cx0],new[y0:y1,x0:cx0])+x0
  right=minimum_seam(old[y0:y1,cx1:x1],new[y0:y1,cx1:x1])+cx1
  top=minimum_seam(old[y0:cy0,x0:x1].transpose(1,0,2),new[y0:cy0,x0:x1].transpose(1,0,2))+y0
  bottom=minimum_seam(old[cy1:y1,x0:x1].transpose(1,0,2),new[cy1:y1,x0:x1].transpose(1,0,2))+cy1
  yy,xx=np.indices((y1-y0,x1-x0));yy+=y0;xx+=x0
  m[y0:y1,x0:x1]=(xx>=left[:,None])&(xx<=right[:,None])&(yy>=top[None,:])&(yy<=bottom[None,:])
  assert m[cy0:cy1,cx0:cx1].all()
  rule={"type":"four minimum-RGB-error cut seams around mandatory repair core; bounded2px feather","outerBox":[x0,y0,x1,y1],"mandatoryCore":[cx0,cy0,cx1,cy1],"featherPixels":2}
  note="gold/teal/red central join locally continuous; mask boundary exact pixels still need visual inspection"
 else:
  points=[(0,530),(850,0),(1254,0),(1254,150),(0,1020)]
  mi=Image.new("L",(1254,1254));ImageDraw.Draw(mi).polygon(points,fill=255);m=np.array(mi)>0
  rule={"type":"explicit corridor containing both original stepped and repaired straight stone borders; excludes roof object","polygon":points,"featherPixels":2}
  note="cream-blue steps removed in corridor; broad blue field tone outside corridor deliberately preserved and pending"
 mi=Image.fromarray(m.astype("uint8")*255);er1=np.array(mi.filter(ImageFilter.MinFilter(3)))>0;er2=np.array(Image.fromarray(er1.astype("uint8")*255).filter(ImageFilter.MinFilter(3)))>0
 alpha=.25*m+.5*er1+.25*er2
 patch=np.rint(old.astype(float)*(1-alpha[:,:,None])+new.astype(float)*alpha[:,:,None]).clip(0,255).astype("uint8")
 assert np.array_equal(patch[~m],old[~m])
 Image.fromarray(patch).save(f/"applied-crop.png");mi.save(f/"copy-mask.png");Image.fromarray(np.rint(alpha*255).astype("uint8")).save(f/"alpha.png")
 box=q["sourceCrop"];v=base[box[1]:box[3],box[0]:box[2]];assert np.array_equal(v,old)
 u=union[box[1]:box[3],box[0]:box[2]];assert not (u&m).any(),"Unexpected overlap between protected repairs";u|=m
 ctx[box[1]:box[3],box[0]:box[2]][m]=patch[m]
 yy,xx=np.where(m);bb=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
 prop={"attempt":attempt,"input":A["contextOutput"],"sourceCrop":box,"cropWorldBox":q["cropWorldBox"],"maskLocalBox":bb,"maskWorldBox":[bb[0]+q["cropWorldBox"][0],bb[1]+q["cropWorldBox"][1],bb[2]+q["cropWorldBox"][0],bb[3]+q["cropWorldBox"][1]],"maskRule":rule,"request":{"file":str(f/"request.json"),"sha256":sha(f/"request.json")},"receipt":{"file":str(f/"receipt.json"),"sha256":sha(f/"receipt.json")},"native":{"file":str(f/"native.png"),"sha256":sha(f/"native.png")},"patch":{"file":str(f/"applied-crop.png"),"sha256":sha(f/"applied-crop.png")},"copyMask":{"file":str(f/"copy-mask.png"),"sha256":sha(f/"copy-mask.png")},"alpha":{"file":str(f/"alpha.png"),"sha256":sha(f/"alpha.png")},"copyRule":"copy premixed patch where binary mask>0; no second blend","outsideMaskChangedPixels":0,"sourceResampling":False,"actualModel":None,"actualQuality":None,"localVisualAssessment":note,"formalAccepted":False,"internalAccepted":False}
 (f/"proposal.json").write_text(json.dumps(prop,indent=2));props.append(str(f/"proposal.json"))
assert np.array_equal(ctx[~union],base[~union])
out=D/"integrated-local-v05";out.mkdir(exist_ok=False)
Image.fromarray(ctx).save(out/"r12_c05.candidate.context.png");Image.fromarray(ctx[115:4211,115:4211]).save(out/"r12_c05.candidate.png")
preview=Image.fromarray(ctx).resize((1082,1082));preview.save(out/"preview-resized.png")
meta={"sourceAssembly":str(Af),"appliedProposals":props,"contextOutput":{"file":str(out/"r12_c05.candidate.context.png"),"sha256":sha(out/"r12_c05.candidate.context.png")},"output":{"file":str(out/"r12_c05.candidate.png"),"sha256":sha(out/"r12_c05.candidate.png")},"outsideUnionChangedPixels":0,"coreEqualsContextCrop":True,"maximumFeatherPixels":2,"sourceResampling":False,"previewResized":True,"formalAccepted":False,"internalAccepted":False}
(out/"assembly.json").write_text(json.dumps(meta,indent=2));print(json.dumps(meta))

