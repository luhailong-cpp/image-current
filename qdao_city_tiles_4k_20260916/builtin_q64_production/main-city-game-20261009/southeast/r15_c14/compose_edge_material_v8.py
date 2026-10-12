from pathlib import Path
import json,hashlib,datetime,sys
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;R=T/'repairs/edge-material-v8-20261012'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def save(p,j):Path(p).write_text(json.dumps(j,indent=2),encoding='utf-8')
version=sys.argv[1];ids=sys.argv[2:];D=T/('repairs/'+version);D.mkdir(exist_ok=False)
prep=read(R/ids[0]/'preparation.json');base=Path(prep['base']['path']);a=np.asarray(Image.open(base).convert('RGB')).copy();orig=a.copy();mask=np.zeros((4096,4096),bool);steps=[]
for id in ids:
 d=R/id;p=read(d/'preparation.json');x0,y0,x1,y1=p['apply']
 if version in ['edge-material-v9-20261013','edge-geometry-v10-20261013']:
  if id=='NM1':x1=1070
  if id=='NM2':x0=1070
  if id=='WM2':x0,y0,x1,y1=0,1115,180,1530
 if id=='WM1' and 'NM1' in ids:y0=180
 cx,cy=p['origin'];crop=[x0-cx,y0-cy,x1-cx,y1-cy];n=d/'native.png';assert Image.open(n).size==(1254,1254)
 new=np.asarray(Image.open(n).convert('RGB').crop(crop),dtype='uint32');h,w=new.shape[:2];yy,xx=np.indices((h,w));dist=np.minimum.reduce(([xx] if x0>0 else [])+([yy] if y0>0 else [])+([w-1-xx] if x1<4096 else [])+([h-1-yy] if y1<4096 else []));alpha=np.where(dist==0,0,np.where(dist==1,128,255)).astype('uint8');ap=D/(id+'-alpha.png');Image.fromarray(alpha).save(ap);aa=alpha.astype('uint32')[:,:,None];old=a[y0:y1,x0:x1].astype('uint32');a[y0:y1,x0:x1]=((new*aa+old*(255-aa)+127)//255).astype('uint8');mask[y0:y1,x0:x1]=True
 steps.append({'id':id,'native':rec(n),'receipt':rec(d/'receipt.json'),'sourceCrop':crop,'placement':[x0,y0,x1,y1],'alpha':rec(ap),'formula':'uint8((new_uint32*alpha_uint32+old_uint32*(255-alpha_uint32)+127)//255)','resized':False})
assert np.array_equal(a[~mask],orig[~mask]);assert np.array_equal(a[-115:],orig[-115:])
out=T/('candidate/r15_c14-4k-'+version+'.png');assert not out.exists();Image.fromarray(a).save(out);ctxbase=Path(prep['baseContext']['path']);ctx=Image.open(ctxbase).convert('RGB');ctx.paste(Image.fromarray(a),(115,115));cp=T/('candidate/r15_c14-context-4326-'+version+'.png');assert not cp.exists();ctx.save(cp)
save(D/'composition.json',{'tile':'r15_c14','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':rec(base),'baseContext':rec(ctxbase),'previousComposition':rec(T/'repairs/edge-continuity-v7-20261012/composition.json'),'steps':steps,'candidate':rec(out),'context':rec(cp),'outsideRepairBoxesUnchanged':True,'southLast115Unchanged':True,'neighborPixelsModified':False,'formalAccepted':False,'status':'pending_visual_qa'})
Q=T/('review/'+version);Q.mkdir(exist_ok=False)
for id in ids:
 p=read(R/id/'preparation.json');im=Image.open(R/id/'target-native-1254.png').convert('RGB');piece=p['sourcePieces'][1];im.paste(Image.fromarray(a).crop(piece['crop']),tuple(piece['paste']));im.save(Q/(id+'-joint-after-100pct.png'))
print(json.dumps({'candidate':rec(out),'context':rec(cp),'composition':rec(D/'composition.json')}))
