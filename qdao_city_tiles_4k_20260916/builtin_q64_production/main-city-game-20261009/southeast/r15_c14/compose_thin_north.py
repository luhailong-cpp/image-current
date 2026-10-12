from pathlib import Path
import json,hashlib,shutil,datetime
import numpy as np
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r15_c14');S=T/'repairs/north-caps-v1-20261012';D=T/'repairs/north-cap-thin-v3-20261012'
def read(p):return json.loads(Path(p).read_text())
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def save(p,j):Path(p).write_text(json.dumps(j,indent=2))
source=Path(r'C:/Users/luyua/.codex/generated_images/01a12076-a410-78f0-a5e7-e2e4d8c934a3/exec-397786ab-92e5-4474-b843-eb0032127c30.png');n=D/'native.png';assert Image.open(source).size==(1254,1254) and Image.open(source).format=='PNG';assert not n.exists();shutil.copyfile(source,n)
save(D/'receipt.json',{'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'succeeded_pending_visual_qa','tool':'image_gen.imagegen','route':'builtin','originalOutput':rec(source),'native':rec(n),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,'resized':False,'request':rec(D/'request.json'),'preparation':rec(D/'preparation.json')})
m=read(S/'composition.json');base=Path(m['base']['path']);a=np.asarray(Image.open(base).convert('RGB')).copy();orig=a.copy();steps=[];mask=np.zeros((4096,4096),bool)
CFG=[('N2',S/'N2/native.png',S/'N2/receipt.json',1250,[1510,0,1880,35]),('N3',n,D/'receipt.json',2250,[2580,0,2920,35])]
for id,native,receipt,ox,box in CFG:
 x0,y0,x1,y1=box;crop=[x0-ox,627+y0,x1-ox,627+y1];new=np.asarray(Image.open(native).convert('RGB').crop(crop),dtype='uint32');h,w=new.shape[:2];yy,xx=np.indices((h,w));dist=np.minimum.reduce([xx,w-1-xx,h-1-yy]);alpha=np.where(dist==0,0,np.where(dist==1,128,255)).astype('uint8');ap=D/f'{id}-alpha.png';Image.fromarray(alpha).save(ap);aa=alpha.astype('uint32')[:,:,None];old=a[y0:y1,x0:x1].astype('uint32');a[y0:y1,x0:x1]=((new*aa+old*(255-aa)+127)//255).astype('uint8');mask[y0:y1,x0:x1]=True;steps.append({'id':id,'native':rec(native),'receipt':rec(receipt),'sourceCrop':crop,'placement':box,'alpha':rec(ap),'formula':'uint8((new_uint32*alpha_uint32+old_uint32*(255-alpha_uint32)+127)//255)','resized':False})
assert np.array_equal(a[~mask],orig[~mask]);out=T/'candidate/r15_c14-4k-north-cap-thin-v3-20261012.png';assert not out.exists();Image.fromarray(a).save(out);ctxbase=Path(m['baseContext']['path']);ctx=Image.open(ctxbase).convert('RGB');ctx.paste(Image.fromarray(a),(115,115));cp=T/'candidate/r15_c14-context-4326-north-cap-thin-v3-20261012.png';assert not cp.exists();ctx.save(cp)
save(D/'composition.json',{'tile':'r15_c14','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':rec(base),'baseContext':rec(ctxbase),'previousComposition':rec(T/'repairs/internal-composite-v4-20261012/composition.json'),'steps':steps,'candidate':rec(out),'context':rec(cp),'outsideRepairBoxesUnchanged':True,'neighborPixelsModified':False,'formalAccepted':False,'status':'pending_visual_qa'})
north=Image.open(read(S/'N2/preparation.json')['neighborSelection']['candidate']['path'])
for id,_,_,x,_ in CFG:
 im=Image.new('RGB',(1254,1254));im.paste(north.crop((x,3469,x+1254,4096)),(0,0));im.paste(Image.fromarray(a).crop((x,0,x+1254,627)),(0,627));im.save(D/f'{id}-after-core-only-native-1254.png')
print(json.dumps({'candidate':rec(out),'context':rec(cp),'composition':rec(D/'composition.json')}))

