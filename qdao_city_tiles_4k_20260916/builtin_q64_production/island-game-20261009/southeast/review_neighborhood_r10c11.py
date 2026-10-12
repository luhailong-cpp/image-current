from workflow import *
from PIL import Image
from io import BytesIO
import hashlib
q=ROOT/'qa/r10_c11-neighborhood-v01';q.mkdir(exist_ok=True)
paths={'nw':ROOT/'tiles/r09_c11.candidate.png','ne':ROOT/'tiles/r09_c12.candidate-v02.png','sw':ROOT/'tiles/r10_c11.candidate.png','se':ROOT/'tiles/r10_c12.candidate-v02.png'}
ims={};sources={}
for k,p in paths.items():
 b=p.read_bytes();ims[k]=Image.open(BytesIO(b)).convert('RGB');assert ims[k].size==(4096,4096);sources[k]={'file':str(p),'sha256':hashlib.sha256(b).hexdigest()}
entries=[]
for i in range(4):
 x=i*1024
 im=Image.new('RGB',(1024,512));im.paste(ims['nw'].crop((x,3840,x+1024,4096)),(0,0));im.paste(ims['sw'].crop((x,0,x+1024,256)),(0,256))
 p=q/f'north-{i+1}.png';im.save(p);entries.append({'id':f'north-{i+1}','file':str(p),'sources':['nw','sw'],'sourceCrops':[[x,3840,x+1024,4096],[x,0,x+1024,256]],'destinations':[[0,0],[0,256]],'sha256':sha(p)})
 y=i*1024
 im=Image.new('RGB',(512,1024));im.paste(ims['sw'].crop((3840,y,4096,y+1024)),(0,0));im.paste(ims['se'].crop((0,y,256,y+1024)),(256,0))
 p=q/f'east-{i+1}.png';im.save(p);entries.append({'id':f'east-{i+1}','file':str(p),'sources':['sw','se'],'sourceCrops':[[3840,y,4096,y+1024],[0,y,256,y+1024]],'destinations':[[0,0],[256,0]],'sha256':sha(p)})
im=Image.new('RGB',(512,512));parts=[('nw',(3840,3840,4096,4096),(0,0)),('ne',(0,3840,256,4096),(256,0)),('sw',(3840,0,4096,256),(0,256)),('se',(0,0,256,256),(256,256))]
for k,b,d in parts:im.paste(ims[k].crop(b),d)
p=q/'central-junction.png';im.save(p);entries.append({'id':'central-junction','file':str(p),'parts':parts,'sha256':sha(p)})
view=Image.new('RGB',(2048,2048))
for k,d in [('nw',(0,0)),('ne',(1024,0)),('sw',(0,1024)),('se',(1024,1024))]:view.paste(ims[k].resize((1024,1024),Image.Resampling.LANCZOS),d)
p=q/'2x2-review-preview.png';view.save(p)
write(q/'index.json',{'createdAt':now(),'sources':sources,'entries':entries,'reviewPreview':{'file':str(p),'sha256':sha(p),'downscaledForReviewOnly':True},'operation':'exact unscaled native seam crops; preview separately downscaled','formalAccepted':False})
print(str(q/'index.json'))

