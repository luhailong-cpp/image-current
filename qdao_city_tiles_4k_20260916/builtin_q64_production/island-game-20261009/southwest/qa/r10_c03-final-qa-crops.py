from pathlib import Path
import json
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent
prefix='r10c03-rail-v01-r10_c03'
im=Image.open(D/(prefix+'-candidate-4096.png'))
scroll=Image.open(D/'r10c03-scroll-v01-r10_c03-candidate-4096.png')
final=np.array(im); prior=np.array(scroll)
records=[]
def save(label,box):
 p=D/(prefix+'-qa-'+label+'.png')
 im.crop(box).save(p)
 records.append({'path':p.as_posix(),'localBox':box,'globalBox':[box[0]+8192,box[1]+36864,box[2]+8192,box[3]+36864],'scale':'1:1'})
for k in (1024,2048,3072):
 for j in range(4):
  save(f'vertical-{k}-segment-{j+1}',[k-200,j*1024,k+200,(j+1)*1024])
  save(f'horizontal-{k}-segment-{j+1}',[j*1024,k-200,(j+1)*1024,k+200])
for y in (1024,2048,3072):
 for x in (1024,2048,3072): save(f'cross-{x}-{y}',[x-300,y-300,x+300,y+300])
save('scroll-target',[8715-8192,39360-36864,9969-8192,40614-36864])
save('rail-target',[9650-8192,38797-36864,10904-8192,40051-36864])
im.resize((1254,1254),Image.Resampling.LANCZOS).save(D/(prefix+'-qa-preview-1254-only.png'))
box=[9175,39360,9450,40614]; x0,y0,x1,y1=box
a=final[y0-36864:y1-36864,x0-8192:x1-8192]
b=prior[y0-36864:y1-36864,x0-8192:x1-8192]
assert np.array_equal(a,b)
(D/(prefix+'-qa-crops.json')).write_text(json.dumps({'nativeCrops':records,'goldWoodTargetPreservation':{'globalBox':box,'pixelsCompared':a.shape[0]*a.shape[1],'unchangedAfterRailing':True}},indent=2),encoding='utf-8')
print(json.dumps({'cropCount':len(records),'goldTargetPixelsUnchanged':a.shape[0]*a.shape[1]}))

