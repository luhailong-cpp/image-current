"""Mechanically assemble selected native art using recorded unscaled source rectangles."""
from pathlib import Path
from PIL import Image
import json,sys
import numpy as np
from workflow import ROOT,read,write,sha,now
spec=read(Path(sys.argv[1]));tid=spec['tile'];revision=sys.argv[2]
im=Image.new('RGB',(4096,4096));coverage=np.zeros((4096,4096),dtype=np.uint8);parts=[]
for rc,version in spec['patchVersions'].items():
 r,c=map(int,rc);xcuts=[0,1024,2048,3072,4096]
 for shift in spec.get('seamShifts',[]):
  if r==shift['subrow']:xcuts[shift['afterSubcolumn']]+=shift['deltaPixels']
 x0,x1=xcuts[c-1:c+1];y0=(r-1)*1024;y1=r*1024
 crop=[115+x0-(c-1)*1024,115,115+x1-(c-1)*1024,1139]
 p=ROOT/'native'/f'{tid}_p{rc}_{version}.png';native=Image.open(p).convert('RGB');assert native.size==(1254,1254)
 assert 0<=crop[0]<crop[2]<=1254
 im.paste(native.crop(crop),(x0,y0));coverage[y0:y1,x0:x1]+=1
 parts.append({'file':p.as_posix(),'sha256':sha(p),'sourceCrop':crop,'destination':[x0,y0],'destinationBox':[x0,y0,x1,y1],'record':str(p)+'.generation.json'})
assert bool(np.all(coverage==1))
out=ROOT/'tiles'/f'{tid}.candidate-{revision}.png';assert not out.exists();im.save(out)
for part in parts:
 native=Image.open(part['file']).convert('RGB').crop(part['sourceCrop']);dst=im.crop(part['destinationBox']);assert np.array_equal(np.array(native),np.array(dst))
rec={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':4096,'height':4096,'operation':'exact native crop and hard paste; no resize, blending, warping or painting','contributions':parts,'seamShifts':spec.get('seamShifts',[]),'fullCoverage':True,'pixelCoverageMin':int(coverage.min()),'pixelCoverageMax':int(coverage.max()),'allContributionsPixelExact':True,'actualModel':None,'actualQuality':None,'status':'candidate_pending_updated_internal_and_external_review'}
write(Path(str(out)+'.generation.json'),rec)
write(ROOT/f'selected-native-{tid}.json',{'tile':tid,'selectionTime':now(),'entries':parts,'candidate':str(out),'candidateSha256':sha(out),'externalEdgesAccepted':False})
for r in range(1,4):
 for c in range(1,4):
  q=ROOT/'qa'/f'{tid}.junction_{r}{c}-{revision}.png';box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256];im.crop(box).save(q);write(Path(str(q)+'.generation.json'),{'file':str(q),'sha256':sha(q),'operation':'100 percent native crop','source':str(out),'sourceSha256':sha(out),'sourceCrop':box})
q=ROOT/'qa'/f'{tid}.preview-{revision}.png';im.resize((1024,1024),Image.Resampling.LANCZOS).save(q);write(Path(str(q)+'.generation.json'),{'file':str(q),'sha256':sha(q),'operation':'downscaled review preview only','source':str(out),'sourceSha256':sha(out)})
print(json.dumps({'file':str(out),'sha256':sha(out),'pixelExact':True,'fullCoverage':True}))

