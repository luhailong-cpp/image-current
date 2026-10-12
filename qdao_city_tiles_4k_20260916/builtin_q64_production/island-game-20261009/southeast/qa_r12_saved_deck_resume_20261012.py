from workflow import *
from PIL import Image
import numpy as np
import sys
rev=sys.argv[1] if len(sys.argv)>1 else 'v01'
q=ROOT/'qa'/f'r12-c12-saved-deck-resume-20261012-{rev}';q.mkdir(exist_ok=False)
versions={'11':'v03','12':'v02','13':'v04','14':'v04','21':'v01','22':'v01','23':'v03','24':'v01'}
base=Image.new('RGB',(4096,2048));ids=np.full((2048,4096),255,dtype=np.uint8);sources=[]
for i,(rc,v) in enumerate(versions.items()):
 r,c=map(int,rc);x=(c-1)*1024;y=(r-1)*1024;f=ROOT/'native'/f'r12_c12_p{rc}_{v}.png';im=Image.open(f).convert('RGB');assert im.size==(1254,1254)
 base.paste(im.crop((115,115,1139,1139)),(x,y));ids[y:y+1024,x:x+1024]=i;sources.append({'id':i,'file':str(f),'sha256':sha(f),'tileToNativeOffset':[115-x,115-y]})
out=base.copy();joint=ROOT/'native'/f'r12_c12_deck_whole_joint_{rev}.png';jim=Image.open(joint).convert('RGB');assert jim.size==(1254,1254)
box=[1536,0,2560,1024];out.paste(jim.crop((115,115,1139,1139)),(1536,0));ids[:1024,1536:2560]=8;sources.append({'id':8,'file':str(joint),'sha256':sha(joint),'tileToNativeOffset':[-1421,115]})
rgb=np.array(out);mismatch=0;proven=[]
for s in sources:
 yy,xx=np.where(ids==s['id']);a=np.array(Image.open(s['file']).convert('RGB'));dx,dy=s['tileToNativeOffset'];n=int(np.any(rgb[yy,xx]!=a[yy+dy,xx+dx],axis=1).sum());mismatch+=n;proven.append({'sourceId':s['id'],'pixels':len(xx),'mismatch':n})
assert mismatch==0 and np.all(ids!=255)
out.save(q/'partial-two-rows.png');Image.fromarray(ids).save(q/'source-id.png')
base.crop((1792,0,2304,1024)).save(q/'old-middle.png');out.crop((1792,0,2304,1024)).save(q/'repaired-middle.png')
for name,cb in {'left':[1280,0,1792,1024],'right':[2304,0,2816,1024],'bottom':[1536,768,2560,1280]}.items():out.crop(cb).save(q/f'{name}.png')
north=ROOT/'tiles/r11_c12.candidate-v02.png';nim=Image.open(north).convert('RGB');n=Image.new('RGB',(1024,512));n.paste(nim.crop((1536,3840,2560,4096)),(0,0));n.paste(out.crop((1536,0,2560,256)),(0,256));n.save(q/'north.png')
for name,x,y in [('NW',1536,0),('NE',2560,0),('SW',1536,1024),('SE',2560,1024)]:
 if y==0:
  k=Image.new('RGB',(512,512));k.paste(nim.crop((x-256,3840,x+256,4096)),(0,0));k.paste(out.crop((x-256,0,x+256,256)),(0,256))
 else:k=out.crop((x-256,y-256,x+256,y+256))
 k.save(q/f'corner-{name}.png')
write(q/'source-proof.json',{'tile':'r12_c12','status':'saved_native_repair_proposal_pending_outer_join_review','isFull4kCandidate':False,'sourceIdMap':str(q/'source-id.png'),'partialOutput':str(q/'partial-two-rows.png'),'partialSha256':sha(q/'partial-two-rows.png'),'dimensions':[4096,2048],'operation':'exact native crop/paste only; no RGB adjustment/rescale/blending/warp/paint','sourceReplayMismatch':mismatch,'sourceReplay':proven,'sources':sources,'repairSource':str(joint),'repairCoreSourceCrop':[115,115,1139,1139],'repairDestinationBox':box,'realNorthCandidate':str(north),'realNorthSha256':sha(north),'qaCuts':['left','right','bottom','north','corner-NW','corner-NE','corner-SW','corner-SE','repaired-middle']})
print(json.dumps({'folder':str(q),'sourceReplayMismatch':mismatch,'repairedDestinationBox':box}))
