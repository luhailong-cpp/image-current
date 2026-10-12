from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent;R=T/'repairs-resume-20261012';Q=R/'local-qa'
def info(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
nctx=T.parent/'r14_c13/candidate/r14_c13-context-4326-north-v6.png';ncore=T.parent/'r14_c13/candidate/r14_c13-4k-north-v6.png';base=T/'candidate/r15_c13-4k-stone-only-v3-20261012.png'
ni=Image.open(nctx).convert('RGB');north=Image.open(ncore).convert('RGB');halo=np.asarray(ni.crop((115,4211,4211,4326)));b=np.asarray(Image.open(base).convert('RGB'))
for depth in [24,40]:
 mask=np.zeros((115,4096),np.uint8);yy=np.arange(115)[:,None];weights=np.clip((depth-yy)/depth,0,1)*np.ones((1,3254));weights[:,-182:]*=np.linspace(1,0,182)[None,:];mask[:,:3254]=np.rint(weights*255).astype('uint8')
 mp=R/('north-native-halo-narrow'+str(depth)+'-alpha.png');Image.fromarray(mask).save(mp)
 out=b.copy();a=mask.astype(np.uint32);out[:115]=((halo.astype(np.uint32)*a[:,:,None]+out[:115].astype(np.uint32)*(255-a[:,:,None])+127)//255).astype('uint8');dest=Q/('trial-native-north-halo-narrow'+str(depth)+'.png');Image.fromarray(out).save(dest)
 for i,x in enumerate([0,1024,2048,3072]):
  join=Image.new('RGB',(1024,700));join.paste(north.crop((x,3796,x+1024,4096)),(0,0));join.paste(Image.fromarray(out).crop((x,0,x+1024,400)),(0,300));join.save(Q/('native-halo-narrow'+str(depth)+'-north-quarter-'+str(i+1)+'.png'))
 record={'operation':'native_integer_crop_and_saved_alpha_only','base':info(base),'source':info(nctx),'sourceCrop':[115,4211,4211,4326],'immutableNorth':info(ncore),'targetXY':[0,0],'mask':info(mp),'output':info(dest),'alphaRule':{'fullAtSouthRow':0,'zeroAtSouthRow':depth,'linear':True,'xTailFade':[3072,3254]},'resized':False,'sourceRGBChanged':False,'newGenerationCount':0,'status':'trial_pending_visual_qa'};(Q/('trial-native-north-halo-narrow'+str(depth)+'.json')).write_text(json.dumps(record,indent=2))
print('Saved native halo narrow24/40 trials and alpha masks.')
