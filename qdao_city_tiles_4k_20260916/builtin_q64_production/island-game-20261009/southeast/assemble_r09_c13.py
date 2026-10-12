"""r09_c13 only: exact native crops, QA and provenance; no painting."""
from pathlib import Path
from PIL import Image
import numpy as np
from workflow import ROOT,read,write,sha,now,progress
import subprocess,sys
versions={'11':'v01','12':'v01','13':'v02','14':'v01','21':'v02','22':'v01','23':'v01','24':'v01','31':'v01','32':'v01','33':'v03','34':'v01','41':'v02','42':'v01','43':'v02','44':'v01'}
tid='r09_c13'
im=Image.new('RGB',(4096,4096));parts=[];images={}
for rc,v in versions.items():
 r,c=map(int,rc);p=ROOT/'native'/f'{tid}_p{rc}_{v}.png';src=Image.open(p).convert('RGB')
 assert src.size==(1254,1254)
 record=read(Path(str(p)+'.generation.json'))
 assert record['sha256']==sha(p) and record['actualModel'] is None and record['actualQuality'] is None
 crop=[115,115,1139,1139];xy=[(c-1)*1024,(r-1)*1024];box=xy+[xy[0]+1024,xy[1]+1024]
 im.paste(src.crop(crop),xy);images[rc]=src
 parts.append({'file':p.as_posix(),'sha256':sha(p),'sourceCrop':crop,'destination':xy,'destinationBox':box,'record':str(p)+'.generation.json'})
out=ROOT/'tiles'/f'{tid}.candidate.png'
assert not out.exists()
im.save(out)
for part in parts:
 assert np.array_equal(np.array(Image.open(part['file']).crop(part['sourceCrop'])),np.array(im.crop(part['destinationBox'])))
rec={'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'width':4096,'height':4096,'operation':'exact unscaled 1024 core crops and hard paste of 16 native 1254 patches; no resize, blending, warping or painting','derivedFrom':parts,'contributions':parts,'fullCoverage':True,'pixelCoverageMin':1,'pixelCoverageMax':1,'allContributionsPixelExact':True,'actualModel':None,'actualQuality':None,'status':'candidate_pending_internal_and_external_review'}
write(Path(str(out)+'.generation.json'),rec)
write(ROOT/f'selected-native-{tid}.json',{'tile':tid,'selectionTime':now(),'entries':parts,'patchVersions':versions,'candidate':out.as_posix(),'candidateSha256':sha(out),'internalEdgesAccepted':False,'externalEdgesAccepted':False,'formalAccepted':False})
qa=[]
for r in range(1,5):
 for c in range(1,5):
  rc=f'{r}{c}'
  for direction,rr,cc in [('horizontal',r,c+1),('vertical',r+1,c)]:
   if rr>4 or cc>4:continue
   other=f'{rr}{cc}';ident=f'{tid}-p{rc}-p{other}'
   subprocess.run([sys.executable,str(ROOT/'qa/check_pair.py'),f'{tid}_p{rc}_{versions[rc]}.png',f'{tid}_p{other}_{versions[other]}.png',direction,ident],capture_output=True,check=True)
   qa.append({'id':ident,'direction':direction,'record':str(ROOT/'qa'/f'{ident}.json'),'status':'pending_visual_review'})
for r in range(1,4):
 for c in range(1,4):
  p=ROOT/'qa'/f'{tid}.junction_{r}{c}.png';box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256];im.crop(box).save(p)
  write(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'operation':'100-percent native crop for junction QA','derivedFrom':[{'file':str(out),'sha256':sha(out),'sourceCrop':box}]})
for r,v in [(1,'v01'),(2,'v01'),(3,'v01'),(4,'v02')]:
 a=f'r09_c12_p{r}4_{v}.png';b=f'{tid}_p{r}1_{versions[f"{r}1"]}.png';ident=f'{tid}-external-left-row{r}'
 subprocess.run([sys.executable,str(ROOT/'qa/check_pair.py'),a,b,'horizontal',ident],capture_output=True,check=True)
 qa.append({'id':ident,'direction':'horizontal','record':str(ROOT/'qa'/f'{ident}.json'),'status':'pending_visual_review','external':True})
prev=ROOT/'qa'/f'{tid}.preview.png';im.resize((1024,1024),Image.Resampling.LANCZOS).save(prev)
write(Path(str(prev)+'.generation.json'),{'file':str(prev),'sha256':sha(prev),'operation':'downscale for review only; not final art','derivedFrom':[{'file':str(out),'sha256':sha(out)}]})
write(ROOT/'qa'/f'{tid}.review-index.json',{'tile':tid,'candidate':str(out),'candidateSha256':sha(out),'seams':qa,'junctionCount':9,'formalAccepted':False})
progress(status='candidate_assembled_pending_QA',usableNativeCount=16,complete4kCount=1,formalAcceptedCount=0,currentPatch=None,nextStep='Review 24 internal seams, nine junctions and four existing left-edge joins; other external edges unverified')
print({'file':str(out),'sha256':sha(out),'pixelExact':True,'fullCoverage':True})

