from pathlib import Path
import json,hashlib,datetime,shutil
import numpy as np
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r15_c14');R=T/'repairs/edge-continuity-v7-20261012'
def read(p):return json.loads(Path(p).read_text())
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def save(p,j):Path(p).write_text(json.dumps(j,indent=2))
files={'W2':'exec-6dd8488a-f7f0-4ad8-9e64-0a0176bf7534.png','WL':'exec-354b925b-121c-4a1a-8a06-7ba8bb559720.png','N4':'exec-f4029343-c32f-41ec-a1e1-05854590d6e7.png'}
for id,fn in files.items():
 d=R/id;source=Path(r'C:/Users/luyua/.codex/generated_images/01a12076-a410-78f0-a5e7-e2e4d8c934a3')/fn;n=d/'native.png';assert not n.exists();assert Image.open(source).size==(1254,1254) and Image.open(source).format=='PNG';shutil.copyfile(source,n);save(d/'receipt.json',{'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'succeeded_pending_visual_qa','tool':'image_gen.imagegen','route':'builtin','originalOutput':rec(source),'native':rec(n),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,'resized':False,'request':rec(d/'request.json'),'preparation':rec(d/'preparation.json')})
prep=read(R/'W2/preparation.json');base=Path(prep['base']['path']);a=np.asarray(Image.open(base).convert('RGB')).copy();orig=a.copy();mask=np.zeros((4096,4096),bool);steps=[]
for id in files:
 d=R/id;p=read(d/'preparation.json');x0,y0,x1,y1=p['apply'];cx,cy=p['origin'];crop=[x0-cx,y0-cy,x1-cx,y1-cy];n=d/'native.png';new=np.asarray(Image.open(n).convert('RGB').crop(crop),dtype='uint32');h,w=new.shape[:2];yy,xx=np.indices((h,w));dist=np.minimum.reduce(([xx] if x0>0 else [])+([yy] if y0>0 else [])+([w-1-xx] if x1<4096 else [])+([h-1-yy] if y1<4096 else []));alpha=np.where(dist==0,0,np.where(dist==1,128,255)).astype('uint8');ap=d/'alpha.png';Image.fromarray(alpha).save(ap);aa=alpha.astype('uint32')[:,:,None];old=a[y0:y1,x0:x1].astype('uint32');a[y0:y1,x0:x1]=((new*aa+old*(255-aa)+127)//255).astype('uint8');mask[y0:y1,x0:x1]=True;steps.append({'id':id,'native':rec(n),'receipt':rec(d/'receipt.json'),'sourceCrop':crop,'placement':p['apply'],'alpha':rec(ap),'formula':'uint8((new_uint32*alpha_uint32+old_uint32*(255-alpha_uint32)+127)//255)','resized':False})
assert np.array_equal(a[~mask],orig[~mask]);assert np.array_equal(a[-115:],orig[-115:])
out=T/'candidate/r15_c14-4k-external-partial-v7-20261012.png';assert not out.exists();Image.fromarray(a).save(out);ctxbase=Path(prep['baseContext']['path']);ctx=Image.open(ctxbase).convert('RGB');ctx.paste(Image.fromarray(a),(115,115));cp=T/'candidate/r15_c14-context-4326-external-partial-v7-20261012.png';assert not cp.exists();ctx.save(cp)
save(R/'composition.json',{'tile':'r15_c14','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':rec(base),'baseContext':rec(ctxbase),'previousComposition':rec(T/'repairs/west-upper-compose-v2-20261012/composition.json'),'steps':steps,'candidate':rec(out),'context':rec(cp),'outsideRepairBoxesUnchanged':True,'southLast115Unchanged':True,'neighborPixelsModified':False,'formalAccepted':False,'status':'pending_visual_qa'})
for id in files:
 d=R/id;p=read(d/'preparation.json');im=Image.open(d/'target-native-1254.png').convert('RGB');piece=p['sourcePieces'][1];im.paste(Image.fromarray(a).crop(piece['crop']),tuple(piece['paste']));im.save(d/'after-core-only-native-1254.png')
print(json.dumps({'candidate':rec(out),'context':rec(cp),'composition':rec(R/'composition.json')}))

