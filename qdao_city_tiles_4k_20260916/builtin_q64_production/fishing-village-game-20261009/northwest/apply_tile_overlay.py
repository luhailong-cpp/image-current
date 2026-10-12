from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
from apply_r03_c03_repairs import overlay_mask
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def resolve(p):return Path(p) if Path(p).is_absolute() else ROOT/p
def fileval(v):return v['file'] if isinstance(v,dict) else v
ap=argparse.ArgumentParser();ap.add_argument('base');ap.add_argument('native');ap.add_argument('tag');ap.add_argument('--context');args=ap.parse_args()
basep=resolve(args.base);base=read(basep);tile=base['tile'];origin=base.get('globalBox',base.get('globalCoreBox'))[:2]
a=np.array(Image.open(resolve(fileval(base['candidate']))).convert('RGB'));ids=np.array(Image.open(resolve(fileval(base['sourceIdMap'])))).astype(np.uint16)
sources=base['sources'];src=ROOT/'native'/f'{args.native}.png';rp=Path(str(src)+'.generation.json');r=read(rp)
assert sha(src)==r['sha256']
g=r['globalNativeBox'];box=[g[0]-origin[0],g[1]-origin[1],g[2]-origin[0],g[3]-origin[1]];x0,y0,x1,y1=box
assert 0<=x0<x1<=4096 and 0<=y0<4096 and y1<=4211
repair=np.array(Image.open(src).convert('RGB'))
if y1>4096:
 assert args.context, 'Outside tile halo requires exact native context'
 context=np.array(Image.open(resolve(args.context)).convert('RGB'))
 assert context.shape==(1254,1254,3) and np.array_equal(context[:4096-y0],a[y0:4096,x0:x1])
else:context=a[y0:y1,x0:x1]
mask,paths=overlay_mask(context,repair);sid=max(s['sourceId'] for s in sources)+1
height=min(y1,4096)-y0;cm=mask[:height]
a[y0:y0+height,x0:x1][cm]=repair[:height][cm];ids[y0:y0+height,x0:x1][cm]=sid
sources.append({'sourceId':sid,'file':str(src),'sha256':sha(src),'generationRecord':str(rp),'generationRecordSha256':sha(rp),'nativeBox':box})
counts=[]
for s in sources:
 gr=read(resolve(s['generationRecord']));g=gr['globalNativeBox'];s['nativeBox']=[g[0]-origin[0],g[1]-origin[1],g[2]-origin[0],g[3]-origin[1]]
 y,x=np.nonzero(ids==s['sourceId']);im=np.array(Image.open(resolve(s['file'])).convert('RGB'));sx=x-s['nativeBox'][0];sy=y-s['nativeBox'][1]
 assert (sx>=0).all() and (sx<1254).all() and (sy>=0).all() and (sy<1254).all()
 assert sha(resolve(s['file']))==s['sha256'] and np.array_equal(a[y,x],im[sy,sx])
 counts.append({'sourceId':s['sourceId'],'pixels':len(x)})
out=ROOT/f'work-{tile}/tiles';p=out/f'{tile}.candidate-{args.tag}.png';ip=out/f'{tile}.source-id-{args.tag}.png';recp=out/f'{tile}.{args.tag}.assembly.json'
assert not any(z.exists() for z in [p,ip,recp])
Image.fromarray(a).save(p);Image.fromarray(ids.astype(np.uint16)).save(ip)
rec={'tile':tile,'status':'candidate-repair-pending-QA','candidate':str(p),'sha256':sha(p),'size':[4096,4096],'globalBox':[*origin,origin[0]+4096,origin[1]+4096],'sources':sources,'pixelSourceVerified':True,'pixelCount':4096*4096,'sourceIdMap':str(ip),'sourceIdSha256':sha(ip),'base':{'record':str(basep),'sha256':sha(basep)},'overlay':{'source':str(src),'nativeBox':box,'paths':paths,'selectedPixels':int(mask.sum())},'counts':counts,'resample':False,'blend':False,'formalAccepted':False}
recp.write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
qa=ROOT/f'work-{tile}/qa/{args.tag}';qa.mkdir(exist_ok=True);crops=[]
for name,b in [('north',[x0,y0,x1,y0+230]),('south',[x0,y1-230,x1,y1]),('west',[x0,y0,x0+230,y1]),('east',[x1-230,y0,x1,y1])]:
 for k in range(2):
  bb=[b[0]+627*k,b[1],min(b[2],b[0]+627*(k+1)),b[3]] if name in ['north','south'] else [b[0],b[1]+627*k,b[2],min(b[3],b[1]+627*(k+1))]
  q=qa/f'{name}-{k+1}.png';Image.fromarray(a).crop(bb).save(q);crops.append({'file':str(q),'sha256':sha(q),'box':bb})
for name,b in [('nw',[x0,y0,x0+300,y0+300]),('ne',[x1-300,y0,x1,y0+300]),('sw',[x0,y1-300,x0+300,y1]),('se',[x1-300,y1-300,x1,y1])]:
 q=qa/f'{name}.png';Image.fromarray(a).crop(b).save(q);crops.append({'file':str(q),'sha256':sha(q),'box':b})
(qa/'crops.json').write_text(json.dumps(crops,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidate':str(p),'sha256':sha(p),'assembly':str(recp),'pixelsVerified':4096*4096,'changed':int(mask.sum())}))

