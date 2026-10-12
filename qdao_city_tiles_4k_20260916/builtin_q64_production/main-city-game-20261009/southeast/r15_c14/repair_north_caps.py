from pathlib import Path
import json,hashlib,datetime,sys,shutil
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;R=T/'repairs/north-caps-v1-20261012';R.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
def rec(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
CFG={'N2':{'x':1250,'apply':[1500,0,1960,320]},'N3':{'x':2250,'apply':[2520,0,3020,390]}}
if sys.argv[1]=='prepare':
 latest=read(T/'candidate/latest-assembly.json');north=read(Z/'r14_c14/candidate/latest-assembly.json');base=Path(latest['candidate']['path']);n=Path(north['candidate']['path']);assert rec(n)['sha256']==north['candidate']['sha256']
 refs=read(T/'records/p01_01_v20261012T135016_73f165cf.request.json')['referenced_image_paths'][:3]
 for id,c in CFG.items():
  d=R/id;d.mkdir();x=c['x'];target=Image.new('RGB',(1254,1254));target.paste(Image.open(n).crop((x,3469,x+1254,4096)),(0,0));target.paste(Image.open(base).crop((x,0,x+1254,627)),(0,627));tp=d/'target-native-1254.png';target.save(tp)
  alpha=np.zeros((1254,1254),dtype='uint8');x0,y0,x1,y1=c['apply'];alpha[627+y0:627+y1,x0-x:x1-x]=255;mp=d/'edit-mask-1254.png';Image.fromarray(alpha).save(mp)
  prompt='Use case: precise-object-edit. LAST image is the actual 1254 x 1254 native edit target, unscaled close-up of two adjoining map cores. TOP 627 rows are immutable old neighboring stone pavement; BOTTOM 627 rows are the new tile. First three images give approved style/material only, second-last image is strict edit mask: change only WHITE, keep BLACK exactly unchanged. Repair the blue inlay that is abruptly cut at the horizontal join y627. Do not extend blue into the old upper half. Give the existing lower blue inlay a complete clean beveled closed end slightly below the join, surrounded by the same pale grey stone continuing from the upper half. Connect the pale slab grout across y627 using exact visible upper-half endpoints and lower existing edges. No blank disconnected grooves, no horizontal rectangular patch edge, no crop boundary through a blue stone. Preserve the existing lower inlay direction and all boundary grout endpoints, keep the outer image and all unmasked stone fixed. This is a precise local geometric closure, not re-layout; do not zoom, resize, warp, change lighting, recolor the entire image, add paper, objects or lettering. Output exactly 1254 x 1254 actual native PNG.'
  req={'prompt':prompt,'referenced_image_paths':refs+[str(mp),str(tp)],'transparent_background':False};save(d/'request.json',req);(d/'prompt.txt').write_text(prompt)
  save(d/'preparation.json',{'id':id,'createdAt':now(),'base':rec(base),'baseContext':latest['context'],'neighborSelection':north,'sourcePieces':[{'source':rec(n),'crop':[x,3469,x+1254,4096],'paste':[0,0]},{'source':rec(base),'crop':[x,0,x+1254,627],'paste':[0,627]}],'applyBox':c['apply'],'targetOrigin':[x,-627],'neighborPixelsImmutable':True,'haloUsed':False,'references':[rec(p) for p in req['referenced_image_paths']],'request':rec(d/'request.json'),'actualModel':None,'actualQuality':None})
 print(str(R))
elif sys.argv[1]=='ingest':
 id,sp=sys.argv[2],Path(sys.argv[3]);d=R/id;n=d/'native.png';assert not n.exists();im=Image.open(sp);assert im.size==(1254,1254) and im.format=='PNG';shutil.copyfile(sp,n)
 save(d/'receipt.json',{'status':'succeeded_pending_visual_qa','generatedAt':now(),'tool':'image_gen.imagegen','route':'builtin','originalOutput':rec(sp),'native':rec(n),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,'resized':False,'request':rec(d/'request.json'),'preparation':rec(d/'preparation.json')});print(json.dumps(rec(n)))
elif sys.argv[1]=='compose':
 pre=read(R/'N2/preparation.json');base=Path(pre['base']['path']);a=np.asarray(Image.open(base).convert('RGB')).copy();orig=a.copy();mask=np.zeros((4096,4096),bool);steps=[]
 for id,c in CFG.items():
  d=R/id;n=d/'native.png';x0,y0,x1,y1=c['apply'];crop=[x0-c['x'],627+y0,x1-c['x'],627+y1];new=np.asarray(Image.open(n).convert('RGB').crop(crop),dtype='uint32');h,w=new.shape[:2];yy,xx=np.indices((h,w));dist=np.minimum.reduce([xx,w-1-xx,h-1-yy]);alpha=np.where(dist==0,0,np.where(dist==1,128,255)).astype('uint8');ap=d/'alpha.png';Image.fromarray(alpha).save(ap);aa=alpha.astype('uint32')[:,:,None];old=a[y0:y1,x0:x1].astype('uint32');a[y0:y1,x0:x1]=((new*aa+old*(255-aa)+127)//255).astype('uint8');mask[y0:y1,x0:x1]=True
  steps.append({'id':id,'native':rec(n),'receipt':rec(d/'receipt.json'),'sourceCrop':crop,'placement':c['apply'],'alpha':rec(ap),'formula':'uint8((new_uint32*alpha_uint32+old_uint32*(255-alpha_uint32)+127)//255)','neighborImmutable':True,'resized':False})
 assert np.array_equal(a[~mask],orig[~mask]);out=T/'candidate/r15_c14-4k-north-caps-v1-20261012.png';assert not out.exists();Image.fromarray(a).save(out)
 ctxbase=Path(pre['baseContext']['path']);ctx=Image.open(ctxbase).convert('RGB');ctx.paste(Image.fromarray(a),(115,115));cp=T/'candidate/r15_c14-context-4326-north-caps-v1-20261012.png';assert not cp.exists();ctx.save(cp)
 save(R/'composition.json',{'createdAt':now(),'tile':'r15_c14','base':rec(base),'baseContext':rec(ctxbase),'previousComposition':rec(T/'repairs/internal-composite-v4-20261012/composition.json'),'steps':steps,'candidate':rec(out),'context':rec(cp),'outsideRepairBoxesUnchanged':True,'neighborPixelsModified':False,'formalAccepted':False,'status':'pending_visual_qa'})
 for id,c in CFG.items():
  d=R/id;x=c['x'];ni=Image.open(pre['neighborSelection']['candidate']['path']);target=Image.new('RGB',(1254,1254));target.paste(ni.crop((x,3469,x+1254,4096)),(0,0));target.paste(Image.fromarray(a).crop((x,0,x+1254,627)),(0,627));target.save(d/'after-core-only-native-1254.png')
 print(json.dumps({'candidate':rec(out),'context':rec(cp),'composition':rec(R/'composition.json')}))

