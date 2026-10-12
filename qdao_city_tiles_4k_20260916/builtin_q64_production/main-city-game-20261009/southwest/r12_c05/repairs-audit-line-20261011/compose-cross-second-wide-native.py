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
  def foreground(a):
   z=a.astype("int16")
   return ((z[:,:,0]>z[:,:,2]+35)&(z[:,:,1]>z[:,:,2]+10))|((z[:,:,0]<115)&(z[:,:,1]<160)&(z[:,:,2]<180))
  m=foreground(old)|foreground(new)
  clip=Image.new("L",(1254,1254));ImageDraw.Draw(clip).polygon([(0,530),(280,575),(520,470),(800,300),(1050,120),(1254,0),(1254,1254),(0,1254)],fill=255);m &= np.array(clip)>0
  mi=Image.fromarray(m.astype("uint8")*255).filter(ImageFilter.MaxFilter(7))
  # Fill fully enclosed highlight holes, leaving exterior background excluded.
  padded=Image.new("L",(1256,1256));padded.paste(mi,(1,1));ImageDraw.floodfill(padded,(0,0),128)
  arr=np.array(padded)[1:-1,1:-1];m=arr!=128
  rule={"type":"union of actual old/new foreground silhouettes, filled enclosed highlights, expanded3px; excludes pavement, bounded2px feather","featherPixels":2}
  note="entire internally consistent generated roof surface reused to avoid a new cut inside teal molding; original exterior pavement preserved; crop perimeter joins still pending"
 else:
  points=[(0,500),(820,0),(1254,0),(1254,1254),(0,1254)]
  mi=Image.new("L",(1254,1254));ImageDraw.Draw(mi).polygon(points,fill=255);m=np.array(mi)>0
  def foreground(a):
   z=a.astype("int16");yy,xx=np.indices(z.shape[:2])
   return (((z[:,:,0]>z[:,:,2]+35)&(z[:,:,1]>z[:,:,2]+10))|((z[:,:,0]<115)&(z[:,:,1]<160)&(z[:,:,2]<180)))&(yy>650)&(xx>430)
  obj=foreground(old)|foreground(new)
  oi=Image.fromarray(obj.astype("uint8")*255).filter(ImageFilter.MaxFilter(9))
  padded=Image.new("L",(1256,1256));padded.paste(oi,(1,1));ImageDraw.floodfill(padded,(0,0),128)
  obj=np.array(padded)[1:-1,1:-1]!=128
  m &= ~obj
  rule={"type":"generated continuous cream/blue paving plane; foreground object mask excluded with4px guard; bounded2px feather","polygon":points,"featherPixels":2}
  note="large three stone border notches corrected and central blue plane unified; crop outer color/line continuation still pending"
 mi=Image.fromarray(m.astype("uint8")*255);er1=np.array(mi.filter(ImageFilter.MinFilter(3)))>0;er2=np.array(Image.fromarray(er1.astype("uint8")*255).filter(ImageFilter.MinFilter(3)))>0
 alpha=.25*m+.5*er1+.25*er2
 patch=np.rint(old.astype(float)*(1-alpha[:,:,None])+new.astype(float)*alpha[:,:,None]).clip(0,255).astype("uint8")
 assert np.array_equal(patch[~m],old[~m])
 Image.fromarray(patch).save(f/"applied-crop-v02.png");mi.save(f/"copy-mask-v02.png");Image.fromarray(np.rint(alpha*255).astype("uint8")).save(f/"alpha-v02.png")
 box=q["sourceCrop"];v=base[box[1]:box[3],box[0]:box[2]];assert np.array_equal(v,old)
 u=union[box[1]:box[3],box[0]:box[2]];assert not (u&m).any(),"Unexpected overlap between protected repairs";u|=m
 ctx[box[1]:box[3],box[0]:box[2]][m]=patch[m]
 yy,xx=np.where(m);bb=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
 prop={"attempt":attempt,"input":A["contextOutput"],"sourceCrop":box,"cropWorldBox":q["cropWorldBox"],"maskLocalBox":bb,"maskWorldBox":[bb[0]+q["cropWorldBox"][0],bb[1]+q["cropWorldBox"][1],bb[2]+q["cropWorldBox"][0],bb[3]+q["cropWorldBox"][1]],"maskRule":rule,"request":{"file":str(f/"request.json"),"sha256":sha(f/"request.json")},"receipt":{"file":str(f/"receipt.json"),"sha256":sha(f/"receipt.json")},"native":{"file":str(f/"native.png"),"sha256":sha(f/"native.png")},"patch":{"file":str(f/"applied-crop-v02.png"),"sha256":sha(f/"applied-crop-v02.png")},"copyMask":{"file":str(f/"copy-mask-v02.png"),"sha256":sha(f/"copy-mask-v02.png")},"alpha":{"file":str(f/"alpha-v02.png"),"sha256":sha(f/"alpha-v02.png")},"copyRule":"copy premixed patch where binary mask>0; no second blend","outsideMaskChangedPixels":0,"sourceResampling":False,"actualModel":None,"actualQuality":None,"localVisualAssessment":note,"formalAccepted":False,"internalAccepted":False}
 (f/"proposal-v02.json").write_text(json.dumps(prop,indent=2));props.append(str(f/"proposal-v02.json"))
assert np.array_equal(ctx[~union],base[~union])
out=D/"integrated-local-v06";out.mkdir(exist_ok=False)
Image.fromarray(ctx).save(out/"r12_c05.candidate.context.png");Image.fromarray(ctx[115:4211,115:4211]).save(out/"r12_c05.candidate.png")
preview=Image.fromarray(ctx).resize((1082,1082));preview.save(out/"preview-resized.png")
meta={"sourceAssembly":str(Af),"appliedProposals":props,"contextOutput":{"file":str(out/"r12_c05.candidate.context.png"),"sha256":sha(out/"r12_c05.candidate.context.png")},"output":{"file":str(out/"r12_c05.candidate.png"),"sha256":sha(out/"r12_c05.candidate.png")},"outsideUnionChangedPixels":0,"coreEqualsContextCrop":True,"maximumFeatherPixels":2,"sourceResampling":False,"previewResized":True,"formalAccepted":False,"internalAccepted":False}
(out/"assembly.json").write_text(json.dumps(meta,indent=2));print(json.dumps(meta))

