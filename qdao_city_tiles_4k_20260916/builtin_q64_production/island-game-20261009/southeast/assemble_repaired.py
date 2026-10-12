"""Reassemble exact source rectangles after one native seam insert."""
from pathlib import Path
from PIL import Image
import numpy as np
from workflow import ROOT,read,write,sha,now
old=ROOT/'tiles/r10_c12.candidate-v01.png'
rec=read(Path(str(old)+'.generation.json'))
cut=[1677,0,2189,1024]
parts=[]
for p in rec['contributions']:
 x0,y0,x1,y1=p['destinationBox']
 ix0,iy0,ix1,iy1=max(x0,cut[0]),max(y0,cut[1]),min(x1,cut[2]),min(y1,cut[3])
 if ix1<=ix0 or iy1<=iy0:
  parts.append(p);continue
 boxes=[[x0,y0,x1,iy0],[x0,iy1,x1,y1],[x0,iy0,ix0,iy1],[ix1,iy0,x1,iy1]]
 for a,b,c,d in boxes:
  if c<=a or d<=b:continue
  q=dict(p);q['destinationBox']=[a,b,c,d];q['destination']=[a,b]
  sx,sy=p['sourceCrop'][:2];q['sourceCrop']=[sx+a-x0,sy+b-y0,sx+c-x0,sy+d-y0];parts.append(q)
native=ROOT/'native/r10_c12_h12-repair_v01.png'
parts.append({'file':str(native),'sha256':sha(native),'sourceCrop':[371,115,883,1139],'destination':[1677,0],'destinationBox':cut,'record':str(native)+'.generation.json'})
im=Image.new('RGB',(4096,4096));coverage=np.zeros((4096,4096),dtype=np.uint8)
for p in parts:
 assert sha(Path(p['file']))==p['sha256']
 a,b,c,d=p['destinationBox'];im.paste(Image.open(p['file']).convert('RGB').crop(p['sourceCrop']),(a,b));coverage[b:d,a:c]+=1
assert np.all(coverage==1)
for p in parts:
 assert np.array_equal(np.array(im.crop(p['destinationBox'])),np.array(Image.open(p['file']).convert('RGB').crop(p['sourceCrop'])))
out=ROOT/'tiles/r10_c12.candidate-v02.png';assert not out.exists();im.save(out)
rec.update(file=str(out),sha256=sha(out),generatedAt=now(),contributions=parts,allContributionsPixelExact=True,pixelCoverageMin=1,pixelCoverageMax=1,status='candidate_pending_independent_review',replaces={'file':str(old),'sha256':sha(old)},seamRepair={'file':str(native),'crop':[371,115,883,1139],'destinationBox':cut,'reason':'Repair shifted seam paving color and short stone-joint truncation'})
write(Path(str(out)+'.generation.json'),rec)
write(ROOT/'selected-native-r10_c12.json',{'tile':'r10_c12','selectionTime':now(),'entries':parts,'candidate':str(out),'candidateSha256':sha(out),'externalEdgesAccepted':False})
q=ROOT/'qa/r10_c12.preview-v02.png';im.resize((1024,1024),Image.Resampling.LANCZOS).save(q)
write(Path(str(q)+'.generation.json'),{'file':str(q),'sha256':sha(q),'source':str(out),'sourceSha256':sha(out),'operation':'downscaled review preview only'})
for r in range(1,4):
 for c in range(1,4):
  box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256]
  q=ROOT/'qa'/f'r10_c12.junction_{r}{c}-v02.png';im.crop(box).save(q)
  write(Path(str(q)+'.generation.json'),{'file':str(q),'sha256':sha(q),'source':str(out),'sourceSha256':sha(out),'sourceCrop':box,'operation':'100 percent native crop'})
print({'file':str(out),'sha256':sha(out),'sourceRectangles':len(parts),'pixelExact':True,'coverageExactlyOnce':True})
