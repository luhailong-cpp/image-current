from pathlib import Path
from PIL import Image
import numpy as np,sys
from workflow import ROOT,read,write,sha,now
revision=sys.argv[1];tile='r11_c11';out=ROOT/'qa'/f'{tile}-{revision}';out.mkdir(exist_ok=True)
candidate=ROOT/'tiles'/f'{tile}.candidate-{revision}.png';im=Image.open(candidate).convert('RGB');assert im.size==(4096,4096)
index={'tile':tile,'candidate':str(candidate),'sha256':sha(candidate),'generatedAt':now(),'seams':[],'junctions':[],'external':[],'formalAcceptedCount':0}
def save(name,img,category,e):
 f=out/f'{name}.png';img.save(f);e.update({'id':name,'file':str(f),'sha256':sha(f),'status':'pending_visual_review'});index[category].append(e)
for r in range(4):
 for c in range(1,4):
  box=[c*1024-256,r*1024,c*1024+256,(r+1)*1024];save(f'h{r+1}{c}',im.crop(box),'seams',{'sourceCrop':box})
for r in range(1,4):
 for c in range(4):
  box=[c*1024,r*1024-256,(c+1)*1024,r*1024+256];save(f'v{r}{c+1}',im.crop(box),'seams',{'sourceCrop':box})
for r in range(1,4):
 for c in range(1,4):
  box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256];save(f'j{r}{c}',im.crop(box),'junctions',{'sourceCrop':box})
npath=ROOT/'tiles'/'r10_c11.candidate-v04.png';epath=ROOT/'tiles'/'r11_c12.candidate-v02.png';nepath=ROOT/'tiles'/'r10_c12.candidate-v02.png'
n=Image.open(npath).convert('RGB');e=Image.open(epath).convert('RGB');ne=Image.open(nepath).convert('RGB')
for i in range(4):
 a=[i*1024,3840,(i+1)*1024,4096];b=[i*1024,0,(i+1)*1024,256];q=Image.new('RGB',(1024,512));q.paste(n.crop(a),(0,0));q.paste(im.crop(b),(0,256));save(f'north-{i+1}',q,'external',{'sources':[{'file':str(npath),'sha256':sha(npath),'crop':a,'destination':[0,0]},{'file':str(candidate),'sha256':sha(candidate),'crop':b,'destination':[0,256]}]})
 a=[3840,i*1024,4096,(i+1)*1024];b=[0,i*1024,256,(i+1)*1024];q=Image.new('RGB',(512,1024));q.paste(im.crop(a),(0,0));q.paste(e.crop(b),(256,0));save(f'east-{i+1}',q,'external',{'sources':[{'file':str(candidate),'sha256':sha(candidate),'crop':a,'destination':[0,0]},{'file':str(epath),'sha256':sha(epath),'crop':b,'destination':[256,0]}]})
q=Image.new('RGB',(512,512));specs=[(npath,n,[3840,3840,4096,4096],[0,0]),(nepath,ne,[0,3840,256,4096],[256,0]),(candidate,im,[3840,0,4096,256],[0,256]),(epath,e,[0,0,256,256],[256,256])]
for _,src,box,dest in specs:q.paste(src.crop(box),dest)
save('northeast-four-tile-junction',q,'external',{'sources':[{'file':str(p),'sha256':sha(p),'crop':box,'destination':dest}for p,_,box,dest in specs]})
im.resize((1024,1024),Image.Resampling.LANCZOS).save(out/'preview.png');index['preview']={'file':str(out/'preview.png'),'operation':'downsampled review only'}
write(out/'index.json',index)
audit=[]
for p in read(Path(str(candidate)+'.generation.json'))['contributions']:
 f=Path(p['file']);rec=read(Path(str(f)+'.generation.json'));assert sha(f)==p['sha256'];assert rec['sha256']==sha(f)
 assert np.array_equal(np.array(Image.open(f).convert('RGB').crop(p['sourceCrop'])),np.array(im.crop(p['destinationBox'])))
 assert sha(Path(rec['prompt']))==rec['promptSha256']
 for ref in rec['references']:assert sha(Path(ref['file']))==ref['sha256']
 audit.append({'file':str(f),'sha256':sha(f),'sourceCrop':p['sourceCrop'],'destinationBox':p['destinationBox'],'pixelExact':True,'promptAndReferencesHashesMatch':True})
write(out/'source-audit.json',{'candidate':str(candidate),'sha256':sha(candidate),'createdAt':now(),'width':4096,'height':4096,'sourceReplay':audit,'pixelExact':True,'actualModel':None,'actualQuality':None,'resizing':False,'blending':False,'painting':False})
print({'qa':str(out),'seams':24,'junctions':9,'externalCrops':9,'sourceProof':True})
