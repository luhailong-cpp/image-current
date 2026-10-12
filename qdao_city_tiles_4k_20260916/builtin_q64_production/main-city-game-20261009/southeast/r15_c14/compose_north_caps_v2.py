from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r15_c14');S=T/'repairs/north-caps-v1-20261012';D=T/'repairs/north-caps-compose-v2-20261012';D.mkdir()
def read(p):return json.loads(Path(p).read_text())
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def save(p,j):Path(p).write_text(json.dumps(j,indent=2))
def seam(cost):
 h,w=cost.shape;acc=cost[0].astype('float64');back=np.zeros((h,w),dtype='int32')
 for y in range(1,h):
  z=np.pad(acc,(1,1),constant_values=np.inf);v=np.stack([z[:-2],z[1:-1],z[2:]]);k=np.argmin(v,axis=0);back[y]=np.arange(w)+k-1;acc=cost[y]+np.min(v,axis=0)
 result=np.zeros(h,dtype='int32');result[-1]=np.argmin(acc)
 for y in range(h-1,0,-1):result[y-1]=back[y,result[y]]
 return result
m=read(S/'composition.json');base=Path(m['base']['path']);a=np.asarray(Image.open(base).convert('RGB')).copy();orig=a.copy();steps=[];editable=np.zeros((4096,4096),bool)
CFG={'N2':{'box':[1450,0,2000,240],'origin':[1250,-627],'side':45,'bottom':75},'N3':{'box':[2250,0,3504,627],'origin':[2250,-627],'side':100,'bottom':160}}
for id,c in CFG.items():
 d=D/id;d.mkdir();native=S/id/'native.png';x0,y0,x1,y1=c['box'];cx,cy=c['origin'];crop=[x0-cx,y0-cy,x1-cx,y1-cy];new=np.asarray(Image.open(native).convert('RGB').crop(crop));old=a[y0:y1,x0:x1].copy();h,w=old.shape[:2]
 cost=np.mean((new.astype('float32')-old.astype('float32'))**2,axis=2)+0.001
 bw=c['side'];bh=c['bottom'];left=seam(cost[:,10:bw])+10;right=seam(cost[:,w-bw:w-10])+w-bw;bottom=seam(cost[h-bh:h-10,:].T)+h-bh;yy,xx=np.indices((h,w));inside=(xx>=left[:,None])&(xx<=right[:,None])&(yy<=bottom[None,:]);erode=inside.copy()
 for k in range(2):
  pad=np.pad(erode,1,constant_values=False);pad[0,1:-1]=erode[0];nxt=erode&pad[:-2,1:-1]&pad[2:,1:-1]&pad[1:-1,:-2]&pad[1:-1,2:]
  if k==0:alpha=np.where(inside,128,0).astype('uint8')
  alpha[nxt]=255;erode=nxt
 ap=d/'alpha.png';Image.fromarray(alpha).save(ap);aa=alpha.astype('uint32')[:,:,None];a[y0:y1,x0:x1]=((new.astype('uint32')*aa+old.astype('uint32')*(255-aa)+127)//255).astype('uint8');editable[y0:y1,x0:x1]|=alpha>0
 save(d/'seam-paths.json',{'left':left.tolist(),'right':right.tolist(),'bottom':bottom.tolist(),'cost':'mean squared RGB difference; dynamic programming +/-1 step; no pixel recoloring','bandSide':bw,'bandBottom':bh,'featherPixels':2})
 steps.append({'id':id,'native':rec(native),'receipt':rec(S/id/'receipt.json'),'sourceCrop':crop,'placement':c['box'],'alpha':rec(ap),'seamPaths':rec(d/'seam-paths.json'),'formula':'uint8((new_uint32*alpha_uint32+old_uint32*(255-alpha_uint32)+127)//255)','resized':False})
assert np.array_equal(a[~editable],orig[~editable]);out=T/'candidate/r15_c14-4k-north-caps-v2-20261012.png';assert not out.exists();Image.fromarray(a).save(out);ctxbase=Path(m['baseContext']['path']);ctx=Image.open(ctxbase).convert('RGB');ctx.paste(Image.fromarray(a),(115,115));cp=T/'candidate/r15_c14-context-4326-north-caps-v2-20261012.png';assert not cp.exists();ctx.save(cp)
save(D/'composition.json',{'tile':'r15_c14','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':rec(base),'baseContext':rec(ctxbase),'previousComposition':rec(T/'repairs/internal-composite-v4-20261012/composition.json'),'steps':steps,'candidate':rec(out),'context':rec(cp),'noNewGeneration':True,'outsideAlphaUnchanged':True,'neighborPixelsModified':False,'formalAccepted':False,'status':'pending_visual_qa'})
north=Image.open(read(S/'N2/preparation.json')['neighborSelection']['candidate']['path'])
for id,c in CFG.items():
 x=c['origin'][0];im=Image.new('RGB',(1254,1254));im.paste(north.crop((x,3469,x+1254,4096)),(0,0));im.paste(Image.fromarray(a).crop((x,0,x+1254,627)),(0,627));im.save(D/id/'after-core-only-native-1254.png')
print(json.dumps({'candidate':rec(out),'composition':rec(D/'composition.json')}))

