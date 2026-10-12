from pathlib import Path
import json,hashlib,shutil,datetime
import numpy as np
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r15_c14');S=T/'repairs/west-upper-v1-20261012';D=T/'repairs/west-upper-compose-v2-20261012';D.mkdir()
def read(p):return json.loads(Path(p).read_text())
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def save(p,j):Path(p).write_text(json.dumps(j,indent=2))
prep=read(S/'preparation.json');n=S/'native.png'
base=Path(prep['base']['path']);a=np.asarray(Image.open(base).convert('RGB')).copy();orig=a.copy();box=[0,0,95,740];crop=[627,0,722,740];new=np.asarray(Image.open(n).convert('RGB').crop(crop),dtype='uint32');h,w=new.shape[:2];yy,xx=np.indices((h,w));dist=np.minimum(w-1-xx,h-1-yy);alpha=np.where(dist==0,0,np.where(dist==1,128,255)).astype('uint8');ap=D/'alpha.png';Image.fromarray(alpha).save(ap);aa=alpha.astype('uint32')[:,:,None];a[:740,:95]=((new*aa+orig[:740,:95].astype('uint32')*(255-aa)+127)//255).astype('uint8');mask=np.zeros((4096,4096),bool);mask[:740,:95]=True;assert np.array_equal(a[~mask],orig[~mask])
out=T/'candidate/r15_c14-4k-external-partial-v6-20261012.png';assert not out.exists();Image.fromarray(a).save(out);ctxbase=Path(prep['baseContext']['path']);ctx=Image.open(ctxbase).convert('RGB');ctx.paste(Image.fromarray(a),(115,115));cp=T/'candidate/r15_c14-context-4326-external-partial-v6-20261012.png';assert not cp.exists();ctx.save(cp)
m={'tile':'r15_c14','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':rec(base),'baseContext':rec(ctxbase),'previousComposition':rec(T/'repairs/north-cap-thin-v4-20261012/composition.json'),'steps':[{'id':'west-upper','native':rec(n),'receipt':rec(S/'receipt.json'),'sourceCrop':crop,'placement':box,'alpha':rec(ap),'formula':'uint8((new_uint32*alpha_uint32+old_uint32*(255-alpha_uint32)+127)//255)','resized':False}],'candidate':rec(out),'context':rec(cp),'outsideRepairBoxesUnchanged':True,'neighborPixelsModified':False,'formalAccepted':False,'status':'pending_visual_qa'};save(D/'composition.json',m)
west=Image.open(prep['westSelection']['candidate']['path']);im=Image.new('RGB',(1254,1254));im.paste(west.crop((3469,0,4096,1254)),(0,0));im.paste(Image.fromarray(a).crop((0,0,627,1254)),(627,0));im.save(D/'after-core-only-native-1254.png')
print(json.dumps({'candidate':rec(out),'context':rec(cp),'composition':rec(D/'composition.json')}))
