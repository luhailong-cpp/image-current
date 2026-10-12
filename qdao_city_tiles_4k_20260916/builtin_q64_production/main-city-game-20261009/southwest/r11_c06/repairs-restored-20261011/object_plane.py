from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parent;SW=T.parent
base=D/"G01.proposal.candidate.png";s06=T/"repairs-resume20261011/06-bottom-step-focused/rejected-native.png";s07=T/"repairs-resume20261011/07-bottom-step-width/rejected-native.png"
old=np.array(Image.open(base).convert("RGB"));a=old.copy();n06=np.array(Image.open(s06).convert("RGB"));n07=np.array(Image.open(s07).convert("RGB"))
spec=importlib.util.spec_from_file_location("ass",SW/"assemble.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def meta(p):
 im=Image.open(p);return {"file":str(p),"sha256":sha(p),"pixels":list(im.size)}
def mixroi(box,new,bands):
 l,t,r,b=box;o=a[t:b,l:r].copy();alpha=np.full(o.shape[:2],255,np.uint8);ev={}
 for side,h in bands.items():
  if side=="left":s,z=o[:,:h],new[:,:h]
  elif side=="right":s,z=o[:,-h:][:,::-1],new[:,-h:][:,::-1]
  elif side=="top":s,z=o[:h].transpose(1,0,2),new[:h].transpose(1,0,2)
  else:s,z=o[-h:][::-1].transpose(1,0,2),new[-h:][::-1].transpose(1,0,2)
  seam=m.minimum_seam(s[:,3:-3],z[:,3:-3])+3;w=m.feather_mask(seam,h,2)
  if side=="left":alpha[:,:h]=np.minimum(alpha[:,:h],w)
  elif side=="right":alpha[:,-h:]=np.minimum(alpha[:,-h:],w[:,::-1])
  elif side=="top":alpha[:h]=np.minimum(alpha[:h],w.T)
  else:alpha[-h:]=np.minimum(alpha[-h:],w.T[::-1])
  ev[side]={"band":h,"path":seam.tolist()}
 a[t:b,l:r]=m.blend_exact(o,new,alpha)
 return ev
# Remove old ground-projection paper from vertical riser using genuine clean vertical face.
e1=mixroi([380,1432,488,1501],n07[382:451,500:608],{"left":10,"right":10,"top":8,"bottom":10})
# Preserve one existing paper count: select 06 native where same paper is correctly on horizontal tread.
e2=mixroi([395,1365,490,1424],n06[315:374,395:490],{"left":10,"right":10,"top":10,"bottom":10})
L,T0,R,B=370,1355,500,1510
mix=a[T0:B,L:R].copy();paste=np.uint8(np.any(mix!=old[T0:B,L:R],axis=2))*255
Image.fromarray(mix).save(D/"G01-object-plane.premixed.patch.png",optimize=True);Image.fromarray(paste).save(D/"G01-object-plane.paste-mask.png",optimize=True)
Image.fromarray(a).save(D/"G01-object-plane.proposal.candidate.png",optimize=True)
Image.fromarray(a).crop([100,1200,800,1650]).save(D/"G01-object-plane.qa-after.png",optimize=True)
outside=np.ones((4096,4096),bool);outside[T0:B,L:R]=False;assert np.array_equal(a[outside],old[outside])
j={"schemaVersion":1,"status":"needs-visual-review","tile":"r11_c06","issueId":"G01-object-plane","base":meta(base),"candidateBox":[L,T0,R,B],"worldBox":[20480+L,40960+T0,20480+R,40960+B],"premixed":meta(D/"G01-object-plane.premixed.patch.png"),"pasteMask":meta(D/"G01-object-plane.paste-mask.png"),"proposal":meta(D/"G01-object-plane.proposal.candidate.png"),"sourceRegions":[{"source":meta(s07),"sourceBox":[500,382,608,451],"targetBoxInTile":[380,1432,488,1501],"translation":[-120,1050],"role":"clean existing vertical riser replaces misplaced paper","seams":e1},{"source":meta(s06),"sourceBox":[395,315,490,374],"targetBoxInTile":[395,1365,490,1424],"translation":[0,1050],"role":"existing horizontal-tread paper variant at same original scene coordinate; one red paper remains, none added","seams":e2}],"maximumFeatherRadiusPixels":2,"resampling":False,"painting":False,"colorAdjustment":False,"newImageGenCalls":0,"outsideRoiUnchanged":True,"allTileEdgesUnchanged":True,"newCountOfRedScrapsAdded":0,"nativeReceipts":[str(D/"06-bottom-step-focused.receipt.json"),str(D/"07-bottom-step-width.receipt.json")],"actualModel":None,"actualQuality":None,"networkGenerationRestoredVerified":False}
(D/"G01-object-plane.proposal.json").write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({"proposal":j["proposal"],"box":j["candidateBox"],"changedPixels":int(np.count_nonzero(paste))}))

