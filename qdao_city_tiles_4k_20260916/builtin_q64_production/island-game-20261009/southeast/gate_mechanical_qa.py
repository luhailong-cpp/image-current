"""Existing-pixel provenance replay, spatial preview and four-tile junction QA."""
from pathlib import Path
from PIL import Image
import numpy as np
from workflow import ROOT,read,write,sha,now
qadir=ROOT/'qa/capacity-gate';qadir.mkdir(exist_ok=True)
audit=[]
for rel in ['tiles/r09_c12.candidate-v02.png','tiles/r10_c12.candidate-v02.png']:
 p=ROOT/rel;rec=read(Path(str(p)+'.generation.json'));actual=np.array(Image.open(p).convert('RGB'));replay=np.zeros_like(actual);coverage=np.zeros((4096,4096),dtype=np.uint8);checks=[]
 for c in rec['contributions']:
  s=Path(c['file']);box=c.get('destinationBox')
  if not box:
   x,y=c['destination'];sw=c['sourceCrop'][2]-c['sourceCrop'][0];sh=c['sourceCrop'][3]-c['sourceCrop'][1];box=[x,y,x+sw,y+sh]
  x,y,x1,y1=box
  source=np.array(Image.open(s).convert('RGB').crop(c['sourceCrop']));replay[y:y1,x:x1]=source;coverage[y:y1,x:x1]+=1
  checks.append({'source':str(s),'shaMatches':sha(s)==c['sha256'],'sourceCrop':c['sourceCrop'],'destinationBox':box,'pixelMatch':bool(np.array_equal(source,actual[y:y1,x:x1]))})
 mismatch=int(np.count_nonzero(np.any(actual!=replay,axis=2)))
 audit.append({'file':rel,'sha256':sha(p),'recordHashMatches':sha(p)==rec['sha256'],'dimensions':list(actual.shape[:2]),'sourceChecks':checks,'pixelMismatchCount':mismatch,'coverageMin':int(coverage.min()),'coverageMax':int(coverage.max()),'passed':mismatch==0 and np.all(coverage==1).item() and all(c['shaMatches'] for c in checks)})
write(qadir/'root-candidates-source-replay.json',{'time':now(),'candidates':audit,'newArtworkRequested':False})
current={'r08_c12':'tiles/r08_c12.candidate-v3.png','r09_c11':'tiles/r09_c11.candidate.png','r09_c12':'tiles/r09_c12.candidate-v02.png','r09_c13':'tiles/r09_c13.candidate.png','r10_c12':'tiles/r10_c12.candidate-v02.png'}
mosaic=Image.new('RGBA',(1536,2048),(0,0,0,0));entries=[]
for tid,rel in current.items():
 p=ROOT/rel;r=int(tid[1:3]);c=int(tid[5:7]);xy=((c-11)*512,(r-8)*512)
 mosaic.paste(Image.open(p).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS),xy)
 entries.append({'tile':tid,'source':rel,'sha256':sha(p),'destination':list(xy),'displaySize':[512,512],'completeCoverage':True})
partial={'r10_c11':{'14':'v01'},'r11_c12':{'11':'v01','12':'v01','13':'v01','14':'v02','21':'v01','22':'v01','23':'v01','24':'v01','31':'v01','32':'v01'}}
for tid,sel in partial.items():
 r=int(tid[1:3]);c=int(tid[5:7])
 for rc,v in sel.items():
  sr,sc=map(int,rc);p=ROOT/'native'/f'{tid}_p{rc}_{v}.png';xy=((c-11)*512+(sc-1)*128,(r-8)*512+(sr-1)*128)
  crop=[115,115,1139,1139];mosaic.paste(Image.open(p).convert('RGBA').crop(crop).resize((128,128),Image.Resampling.LANCZOS),xy)
  entries.append({'tile':tid,'patch':rc,'source':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'sourceCrop':crop,'destination':list(xy),'displaySize':[128,128],'completeCoverage':False})
p=qadir/'spatial-coverage-preview.png';mosaic.save(p)
write(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'operation':'mechanical downscaled spatial review mosaic of existing candidates and native cores, missing pixels transparent; no generated/painted pixels','rowRange':[8,11],'columnRange':[11,13],'entries':entries,'finalArt':False})
# The four-tile junction already has pixels even though most r10c11 is ungenerated.
a=ROOT/'tiles/r09_c11.candidate.png';b=ROOT/'tiles/r09_c12.candidate-v02.png';c=ROOT/'native/r10_c11_p14_v01.png';d=ROOT/'tiles/r10_c12.candidate-v02.png'
sources=[(a,[3840,3840,4096,4096],[0,0]),(b,[0,3840,256,4096],[256,0]),(c,[883,115,1139,371],[0,256]),(d,[0,0,256,256],[256,256])]
j=Image.new('RGB',(512,512))
for s,box,dest in sources:j.paste(Image.open(s).convert('RGB').crop(box),tuple(dest))
p=qadir/'r09c11-r09c12-r10c11-r10c12-junction.png';j.save(p)
write(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'operation':'exact native four-quadrant hard paste; no resize or blending','sources':[{'file':str(s),'sha256':sha(s),'crop':box,'destination':dest} for s,box,dest in sources],'status':'pending_visual_review'})
# Complete r09 c11/c12 shared border from current assembled candidates.
ia=Image.open(a);ib=Image.open(b);strips=[]
for r in range(4):
 boxa=[3840,r*1024,4096,(r+1)*1024];boxb=[0,r*1024,256,(r+1)*1024];im=Image.new('RGB',(512,1024))
 im.paste(ia.crop(boxa),(0,0));im.paste(ib.crop(boxb),(256,0))
 p=qadir/f'r09c11-r09c12-edge-{r+1}.png';im.save(p)
 rec={'file':str(p),'sha256':sha(p),'operation':'exact assembled candidate border crop and paste','sources':[{'file':str(a),'sha256':sha(a),'crop':boxa,'destination':[0,0]},{'file':str(b),'sha256':sha(b),'crop':boxb,'destination':[256,0]}],'status':'pending_visual_review'};write(Path(str(p)+'.generation.json'),rec);strips.append(rec)
write(qadir/'r09c11-r09c12-edge.json',{'entries':strips,'formalAccepted':False})
print({'rootCandidateReplay':[{'file':a['file'],'passed':a['passed'],'mismatchPixels':a['pixelMismatchCount']} for a in audit],'preview':str(qadir/'spatial-coverage-preview.png'),'junction':str(qadir/'r09c11-r09c12-r10c11-r10c12-junction.png')})
