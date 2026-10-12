from pathlib import Path
import json,hashlib,datetime,sys,shutil
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
R=T/'repairs/internal-boundary-v2-20261012'
BASE=T/'candidate/r15_c14-4k-internal-repair-v1-20261012.png'
CTX=T/'candidate/r15_c14-context-4326-internal-repair-v1-20261012.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
def rec(p):return {'path':str(p),'sha256':sha(p)}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
CONFIG={
'A':{'crop':[850,1770,2104,3024],'apply':[1120,2150,1650,2390],'instruction':'Fix only the rectangular crop artifact in the middle upper area, local x270..800 y380..620. The pale slab currently ends along an artificial horizontal line and cuts into the diagonal blue inset. Keep the coherent upper grout network and the existing lower blue diagonal inset. Close the blue inset with one clean natural beveled stone end meeting existing diagonal grout; remove the horizontal rectangular pale patch edge and join the displaced slab groove. Do not remove the whole blue diagonal strip or move its lower continuation. All joints must meet into closed slabs; no dead ends or tiny stepped edges.'},
'B':{'crop':[1600,1860,2854,3114],'apply':[1980,2250,2270,2560],'instruction':'Fix only the small angular jog in the LEFT border of the blue diagonal inset in the center, local x380..670 y390..700. There is a short horizontal rectangular notch at the old crop boundary. Continue the existing single straight diagonal beveled border smoothly through the notch, matching exactly its entry at top and exit at bottom of the white editable mask. Keep all cross-joints, blue slab sizes, top closed end, and all surrounding geometry in place. No new blue strip or grid re-layout.'}}
if sys.argv[1]=='prepare':
 R.mkdir(exist_ok=True)
 refs=read(T/'records/p01_01_v20261012T135016_73f165cf.request.json')['referenced_image_paths'][:3]
 for id,c in CONFIG.items():
  d=R/id;d.mkdir();target=d/'target-native-1254.png';Image.open(BASE).crop(c['crop']).save(target)
  alpha=np.zeros((1254,1254),dtype='uint8');x0,y0,x1,y1=c['apply'];cx,cy,_,_=c['crop'];alpha[y0-cy:y1-cy,x0-cx:x1-cx]=255;mask=d/'edit-mask-1254.png';Image.fromarray(alpha).save(mask)
  prompt='Use case: precise-object-edit. Edit ONLY the LAST image, exactly 1254 x 1254 native PNG. First 3 references define approved material only; second-last image is a binary edit mask. WHITE mask area may change, BLACK area must remain identical. The last image is an actual close crop, do not zoom, reframe, resize, warp or recolor. '+c['instruction']+' Preserve texture, light and shadows. This is a minute continuity repair, not a new layout.'
  req={'prompt':prompt,'referenced_image_paths':refs+[str(mask),str(target)],'transparent_background':False}
  save(d/'request.json',req);(d/'prompt.txt').write_text(prompt,encoding='utf-8')
  save(d/'preparation.json',{'preparedAt':now(),'base':rec(BASE),'crop':c['crop'],'apply':c['apply'],'references':[rec(p) for p in req['referenced_image_paths']],'request':rec(d/'request.json'),'actualModel':None,'actualQuality':None,'sourcePixelsUnscaled':True})
 print(str(R))
elif sys.argv[1]=='ingest':
 id,source=sys.argv[2],Path(sys.argv[3]);d=R/id;n=d/'native.png';assert not n.exists();im=Image.open(source);assert im.size==(1254,1254) and im.format=='PNG';shutil.copyfile(source,n)
 save(d/'receipt.json',{'status':'succeeded_pending_visual_qa','tool':'image_gen.imagegen','route':'builtin','generatedAt':now(),'originalOutput':rec(source),'native':rec(n),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,'noResize':True,'request':rec(d/'request.json'),'preparation':rec(d/'preparation.json')})
 print(json.dumps(rec(n)))
elif sys.argv[1]=='compose':
 a=np.asarray(Image.open(BASE).convert('RGB')).copy();oldbase=a.copy();steps=[];editable=np.zeros((4096,4096),bool)
 for id,c in CONFIG.items():
  d=R/id;n=d/'native.png';x0,y0,x1,y1=c['apply'];cx,cy,_,_=c['crop'];crop=[x0-cx,y0-cy,x1-cx,y1-cy];new=np.asarray(Image.open(n).convert('RGB').crop(crop),dtype='uint32');h,w=new.shape[:2];yy,xx=np.indices((h,w));dist=np.minimum.reduce([xx,yy,w-1-xx,h-1-yy]);alpha=np.where(dist==0,0,np.where(dist==1,128,255)).astype('uint8');ap=d/'alpha.png';Image.fromarray(alpha).save(ap);aa=alpha.astype('uint32')[:,:,None];old=a[y0:y1,x0:x1].astype('uint32');a[y0:y1,x0:x1]=((new*aa+old*(255-aa)+127)//255).astype('uint8');editable[y0:y1,x0:x1]=True
  steps.append({'id':id,'native':rec(n),'receipt':rec(d/'receipt.json'),'sourceCrop':crop,'placement':c['apply'],'alpha':rec(ap),'formula':'uint8((new_uint32*alpha_uint32+old_uint32*(255-alpha_uint32)+127)//255)','resized':False})
 out=T/'candidate/r15_c14-4k-internal-repair-v2-20261012.png';assert not out.exists();Image.fromarray(a).save(out);ctx=Image.open(CTX).convert('RGB');ctx.paste(Image.fromarray(a),(115,115));cp=T/'candidate/r15_c14-context-4326-internal-repair-v2-20261012.png';assert not cp.exists();ctx.save(cp)
 assert np.array_equal(a[~editable],oldbase[~editable])
 save(R/'composition.json',{'createdAt':now(),'tile':'r15_c14','base':rec(BASE),'baseContext':rec(CTX),'previousComposition':rec(T/'repairs/internal-v1-20261012/composition.json'),'steps':steps,'candidate':rec(out),'context':rec(cp),'outsideRepairBoxesUnchanged':True,'formalAccepted':False,'status':'pending_visual_qa'})
 for id,c in CONFIG.items():Image.fromarray(a).crop(c['crop']).save(R/id/'after-native-1254.png')
 print(json.dumps({'candidate':rec(out),'context':rec(cp),'composition':rec(R/'composition.json')}))

