from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
T=Path(__file__).resolve().parent;R=T/'repairs-resume-20261012';Q=R/'local-qa';Q.mkdir(exist_ok=True)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
record=read(T/'production-resume-20261012.json');base=record['baseline'];old=Image.open(base['candidate']['path']).convert('RGB');cur=old.copy()
names=sys.argv[1:];ops=[]
for name in names:
 prep=read(R/(name+'.preparation.json'));source=read(R/(name+'.source.json'));image=Image.open(source['path']).convert('RGB')
 if name.startswith('north-'):
  x=prep['southCrop'][0];y=0;srcbox=prep.get('sourceGeneratedSouthCrop',[0,400,1254,754]);piece=image.crop(srcbox)
  yy=np.arange(354,dtype=float);wy=np.where(yy<120,1,np.clip((354-yy)/234,0,1))
  xx=np.arange(1254,dtype=float);wx=np.minimum(np.clip(xx/72,0,1),np.clip((1253-xx)/72,0,1))
  if x==0: wx[:72]=1
  mask=np.rint(255*wy[:,None]*wx[None,:]).astype('uint8')
 else:
  x,y=prep['sourceCrop'][:2];srcbox=[0,0,1254,1254];piece=image
  yy=np.arange(1254,dtype=float);xx=np.arange(1254,dtype=float)
  wy=np.minimum(np.clip((yy-525)/12,0,1),np.clip((685-yy)/15,0,1));wx=np.minimum(np.clip((xx-400)/60,0,1),np.clip((982-xx)/16,0,1));mask=np.rint(255*wy[:,None]*wx[None,:]).astype('uint8')
 mp=R/(name+'-apply-mask.png')
 if not mp.exists(): Image.fromarray(mask).save(mp)
 else: assert np.array_equal(np.asarray(Image.open(mp)),mask)
 cur.paste(piece,(x,y),Image.open(mp));ops.append({'id':name,'source':source,'sourceCrop':srcbox,'targetXY':[x,y],'mask':{'path':str(mp),'sha256':sha(mp)}})
label='-'.join(n.replace('north-','').replace('-v1','') for n in names);p=Q/('trial-'+label+'.png');cur.save(p)
north=Image.open(T.parent/'r14_c13/candidate/r14_c13-4k-north-v6.png').convert('RGB')
for op in ops:
 name=op['id'];prep=read(R/(name+'.preparation.json'))
 if name.startswith('north-'):
  x=prep['southCrop'][0];join=Image.new('RGB',(1254,700));join.paste(north.crop((x,3796,x+1254,4096)),(0,0));join.paste(cur.crop((x,0,x+1254,400)),(0,300));join.save(Q/(name+'-trial-north-join.png'))
 else:
  x,y=op['targetXY'];cur.crop((x+80,y+500,x+1000,y+700)).save(Q/(name+'-trial-detail.png'))
manifest={'base':base,'operations':ops,'trial':{'path':str(p),'sha256':sha(p)},'resized':False};write(Q/('trial-'+label+'.json'),manifest)
print(json.dumps({'trial':manifest['trial'],'manifest':str(Q/('trial-'+label+'.json'))},indent=2))
