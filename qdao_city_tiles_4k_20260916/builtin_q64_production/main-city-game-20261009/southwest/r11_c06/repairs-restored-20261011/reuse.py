from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;SW=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest");T=SW/"r11_c06"
base=SW/"integrated-20261011/v2/r11_c06.candidate.png";src=T/"repairs-resume20261011/07-bottom-step-width/rejected-native.png"
old=np.array(Image.open(base).convert("RGB"));native=np.array(Image.open(src).convert("RGB"));assert old.shape==(4096,4096,3) and native.shape==(1254,1254,3)
spec=importlib.util.spec_from_file_location("ass",SW/"assemble.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def minseam(a,b):
 # Restrict feather to interior of each strip.
 margin=3
 s=m.minimum_seam(a[:,margin:-margin],b[:,margin:-margin])+margin
 return s
def wt(a,b):
 s=minseam(a,b);return m.feather_mask(s,a.shape[1],2),s
l,t,r,b=170,1315,560,1522
o=old[t:b,l:r].copy()
n=native[t-1050:b-1050,l:r].copy()
# Right endpoint source x670 relocates to 505, dx=-168. No resize or vertical shift.
start,end=455,485
overold=native[t-1050:b-1050,start:end].copy()
overnew=native[t-1050:b-1050,start+168:end+168].copy()
aw,seam=wt(overold,overnew)
n[:,start-l:end-l]=m.blend_exact(overold,overnew,aw)
n[:,end-l:]=native[t-1050:b-1050,end+168:r+168]
bands={"left":40,"right":35,"top":15,"bottom":8}
alpha=np.full(o.shape[:2],255,np.uint8);ev={}
for side,h in bands.items():
 if side=="left":a,z=o[:,:h],n[:,:h]
 elif side=="right":a,z=o[:,-h:][:,::-1],n[:,-h:][:,::-1]
 elif side=="top":a,z=o[:h].transpose(1,0,2),n[:h].transpose(1,0,2)
 else:a,z=o[-h:][::-1].transpose(1,0,2),n[-h:][::-1].transpose(1,0,2)
 w,s=wt(a,z)
 if side=="left":alpha[:,:h]=np.minimum(alpha[:,:h],w)
 elif side=="right":alpha[:,-h:]=np.minimum(alpha[:,-h:],w[:,::-1])
 elif side=="top":alpha[:h]=np.minimum(alpha[:h],w.T)
 else:alpha[-h:]=np.minimum(alpha[-h:],w.T[::-1])
 ev[side]={"stripWidth":h,"path":s.tolist(),"min":int(s.min()),"max":int(s.max())}
mixed=m.blend_exact(o,n,alpha)
a=old.copy();a[t:b,l:r]=mixed
Image.fromarray(mixed).save(D/"G01.premixed.patch.png",optimize=True)
Image.fromarray(n).save(D/"G01.native-reuse-donor.png",optimize=True)
Image.fromarray(alpha).save(D/"G01.native-alpha.png",optimize=True)
paste=np.uint8(np.any(mixed!=o,axis=2))*255
Image.fromarray(paste).save(D/"G01.paste-mask.png",optimize=True)
Image.fromarray(a).save(D/"G01.proposal.candidate.png",optimize=True)
Image.fromarray(old).crop([100,1200,800,1680]).save(D/"G01.qa-before.png",optimize=True)
Image.fromarray(a).crop([100,1200,800,1680]).save(D/"G01.qa-after.png",optimize=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def meta(p):
 im=Image.open(p);return {"file":str(p),"sha256":sha(p),"pixels":list(im.size)}
assert np.array_equal(a[:t],old[:t]) and np.array_equal(a[b:],old[b:]) and np.array_equal(a[t:b,:l],old[t:b,:l]) and np.array_equal(a[t:b,r:],old[t:b,r:])
assert all(np.array_equal(x,y) for x,y in zip([a[0],a[-1],a[:,0],a[:,-1]],[old[0],old[-1],old[:,0],old[:,-1]]))
write={"status":"proposal-needs-visual-review","tile":"r11_c06","issueId":"G01","base":meta(base),"nativeSource":meta(src),"originalToolReceipt":str(T/"repairs-resume20261011/07-bottom-step-width/receipt.json"),"originalGenerationRecord":str(T/"repairs-resume20261011/07-bottom-step-width/generation.json"),"candidateBox":[l,t,r,b],"worldBox":[20480+l,40960+t,20480+r,40960+b],"premixed":meta(D/"G01.premixed.patch.png"),"pasteMask":meta(D/"G01.paste-mask.png"),"nativeAlpha":meta(D/"G01.native-alpha.png"),"proposal":meta(D/"G01.proposal.candidate.png"),"nativePixelReuse":[{"part":"main step face","sourceBox":[l,t-1050,end,b-1050],"targetBoxInTile":[l,t,end,b],"translation":[0,1050]},{"part":"right end cap","sourceBox":[start+168,t-1050,r+168,b-1050],"targetBoxInTile":[start,t,r,b],"translation":[-168,1050],"relativeToNativePlacement":[-168,0]},{"part":"two parts overlap","targetBoxInTile":[start,t,end,b],"minimumErrorSeam":seam.tolist()}],"outerBlendSeams":ev,"maximumFeatherRadiusPixels":2,"resampling":False,"paintedPixels":False,"colorAdjustment":False,"allOutsideRoiPreserved":True,"allOuterTileEdgesPreserved":True,"newImageGenCalls":0,"networkImageGenRestorationVerified":False,"actualModel":None,"actualQuality":None}
(D/"G01.proposal.json").write_text(json.dumps(write,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({"proposal":write["proposal"],"roi":write["candidateBox"],"changedPixels":int(np.count_nonzero(paste))}))


