from workflow import *
from PIL import Image
import numpy as np
q=ROOT/'qa/r12-c12-lower-deck-resume-20261012-v01'
q.mkdir(exist_ok=False)
im=Image.new('RGB',(2048,2048));ids=np.full((2048,2048),255,dtype=np.uint8);sources=[]
for rc,v in [('31','v02'),('32','v04'),('41','v01'),('42','v01')]:
 r,c=map(int,rc);x=(c-1)*1024;y=(r-3)*1024;f=ROOT/'native'/f'r12_c12_p{rc}_{v}.png';ni=Image.open(f).convert('RGB')
 sid=len(sources);im.paste(ni.crop((115,115,1139,1139)),(x,y));ids[y:y+1024,x:x+1024]=sid
 sources.append({'id':sid,'file':str(f),'sha256':sha(f),'outputToNativeOffset':[115-x,115-y]})
f=ROOT/'native/r12_c12_lower_deck_joint_v01.png';ni=Image.open(f).convert('RGB');im.paste(ni.crop((115,115,1139,1139)),(512,1024));ids[1024:,512:1536]=4
sources.append({'id':4,'file':str(f),'sha256':sha(f),'outputToNativeOffset':[-397,-909]})
rgb=np.array(im);proof=[]
for s in sources:
 yy,xx=np.where(ids==s['id']);a=np.array(Image.open(s['file']).convert('RGB'));dx,dy=s['outputToNativeOffset'];n=int(np.any(rgb[yy,xx]!=a[yy+dy,xx+dx],axis=1).sum());assert n==0
 proof.append({'sourceId':s['id'],'pixels':len(xx),'mismatch':n})
im.save(q/'partial-left-bottom.png');Image.fromarray(ids).save(q/'source-id.png')
for name,box in {'left':[256,1024,768,2048],'right':[1280,1024,1792,2048],'top':[512,768,1536,1280],'middle':[768,1024,1280,2048],'corner-NW':[256,768,768,1280],'corner-NE':[1280,768,1792,1280],'bottom-visible':[512,1792,1536,2048]}.items():im.crop(box).save(q/f'{name}.png')
write(q/'source-proof.json',{'isFull4kCandidate':False,'dimensions':[2048,2048],'tileRelativeOrigin':[0,2048],'sources':sources,'sourceReplay':proof,'sourceReplayMismatch':0,'operation':'exact unchanged native crops and hard paste only','repairSource':str(f),'repairCoreSourceCrop':[115,115,1139,1139],'repairDestinationBox':[512,3072,1536,4096],'bottomExternalNeighbor':'not generated; pending','status':'pending_visual_review'})
print(q)
