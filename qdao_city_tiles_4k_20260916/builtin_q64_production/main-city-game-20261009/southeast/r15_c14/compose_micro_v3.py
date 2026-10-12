from pathlib import Path
import json,hashlib,datetime,shutil
import numpy as np
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r15_c14');D=T/'repairs/internal-micro-v3-20261012'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
prep=read(D/'preparation.json');source=Path(r'C:/Users/luyua/.codex/generated_images/01a12076-a410-78f0-a5e7-e2e4d8c934a3/exec-fd9aa41c-f448-43d7-915a-4980e3ccd6a5.png')
assert Image.open(source).size==(1254,1254) and Image.open(source).format=='PNG'
n=D/'native.png';assert not n.exists();shutil.copyfile(source,n)
save(D/'receipt.json',{'status':'succeeded_pending_visual_qa','generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','originalOutput':rec(source),'native':rec(n),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,'resized':False,'request':rec(D/'request.json'),'preparation':rec(D/'preparation.json')})
base=Path(prep['base']['path']);a=np.asarray(Image.open(base).convert('RGB')).copy();orig=a.copy();cx,cy,_,_=prep['targetCrop'];steps=[];mask=np.zeros((4096,4096),bool)
for i,(x0,y0,x1,y1) in enumerate(prep['applyRegions']):
 crop=[x0-cx,y0-cy,x1-cx,y1-cy];new=np.asarray(Image.open(n).convert('RGB').crop(crop),dtype='uint32');h,w=new.shape[:2];yy,xx=np.indices((h,w));dist=np.minimum.reduce([xx,yy,w-1-xx,h-1-yy]);alpha=np.where(dist==0,0,np.where(dist==1,128,255)).astype('uint8');ap=D/f'alpha-{i+1}.png';Image.fromarray(alpha).save(ap);aa=alpha.astype('uint32')[:,:,None];old=a[y0:y1,x0:x1].astype('uint32');a[y0:y1,x0:x1]=((new*aa+old*(255-aa)+127)//255).astype('uint8');mask[y0:y1,x0:x1]=True
 steps.append({'id':f'micro-{i+1}','native':rec(n),'receipt':rec(D/'receipt.json'),'sourceCrop':crop,'placement':[x0,y0,x1,y1],'alpha':rec(ap),'formula':'uint8((new_uint32*alpha_uint32+old_uint32*(255-alpha_uint32)+127)//255)','resized':False})
assert np.array_equal(a[~mask],orig[~mask])
out=T/'candidate/r15_c14-4k-internal-repair-v3-20261012.png';assert not out.exists();Image.fromarray(a).save(out)
ctxbase=T/'candidate/r15_c14-context-4326-internal-repair-v2-20261012.png';ctx=Image.open(ctxbase).convert('RGB');ctx.paste(Image.fromarray(a),(115,115));cp=T/'candidate/r15_c14-context-4326-internal-repair-v3-20261012.png';assert not cp.exists();ctx.save(cp)
m={'tile':'r15_c14','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':rec(base),'baseContext':rec(ctxbase),'previousComposition':rec(T/'repairs/internal-boundary-v2-20261012/composition.json'),'steps':steps,'candidate':rec(out),'context':rec(cp),'outsideRepairBoxesUnchanged':True,'formalAccepted':False,'status':'pending_visual_qa'}
save(D/'composition.json',m);Image.fromarray(a).crop(prep['targetCrop']).save(D/'after-native-1254.png')
print(json.dumps({'candidate':rec(out),'context':rec(cp),'composition':rec(D/'composition.json')}))

