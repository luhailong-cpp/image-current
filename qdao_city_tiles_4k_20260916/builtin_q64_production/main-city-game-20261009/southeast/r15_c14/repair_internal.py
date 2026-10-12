from pathlib import Path
import json,hashlib,datetime,sys,shutil
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
R=T/'repairs/internal-v1-20261012'
R.mkdir(parents=True,exist_ok=True)
BASE=T/'candidate/r15_c14-4k-candidate-c7fe4d0fb7016f67422f.png'
CONTEXT=T/'candidate/r15_c14-context-4326-c7fe4d0fb7016f67422f.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
CONFIG={
 'I01':{'crop':[610,1080,1864,2334],'apply':[840,1230,1580,2260], 'instruction':'Repair the abrupt dead ends of slab grout in the middle vertical zone of the LAST image, local x230..970 y150..1180. Several grooves stop in blank stone and a blue horizontal inset has an unfinished left end near local x400 y1085. Connect every dark grout line into a coherent closed slab network; remove the isolated blue horizontal fragment by continuing the surrounding pale-grey slab texture and joints. Keep all paper, red lantern portion at far left/bottom, perimeter geometry, existing diagonal paving perspective and exact crop unchanged. Do not add new blue bands or props. This is a close crop, never zoom or reframe.'},
 'I02':{'crop':[1510,1740,2764,2994],'apply':[1810,2020,2240,2390], 'instruction':'Repair only the unfinished LEFT EDGE and TOP termination of the grey-blue diagonal inset near local x350..650 y300..600 in LAST image. The blue stone strip fades into a pale slab and has an orphan short joint. Give the existing blue inset a crisp closed end that meets the surrounding diagonal slab grout naturally; every joint must meet another joint. Retain all existing stone positions, strip direction, wall/pillar/foliage near bottom, lighting and texture. No new band, objects or reframing. Keep outer 150 pixels unchanged.'},
 'I03':{'crop':[2842,430,4096,1684],'apply':[3270,820,3730,1140], 'instruction':'Repair only the short dangling diagonal dark groove in the upper-middle pale slab near local x500..720 y480..630 of LAST image. Remove this orphan groove and its detached bright bevel by smoothly continuing the same pale stone slab texture. Keep the complete surrounding slab outlines, blue inset borders, top/bottom/left/right perimeter, all colors and crop fixed. Do not add joints, borders or objects. Only this tiny structural blemish is repaired, no reframing.'}
}
if sys.argv[1]=='prepare':
 refs=read(T/'records/p01_01_v20261012T135016_73f165cf.request.json')['referenced_image_paths'][:3]
 for id,c in CONFIG.items():
  d=R/id;d.mkdir(exist_ok=True);target=d/'target-native-1254.png'
  assert not target.exists()
  Image.open(BASE).crop(c['crop']).save(target)
  prompt='Edit the LAST attached image only. Return exactly 1254 x 1254 actual native PNG, never resize, upscale, rotate or warp. First three images are approved whole-layout/detail/style references, not the output framing. Preserve original Q-cute painterly stone material and geometry. '+c['instruction']
  (d/'prompt.txt').write_text(prompt,encoding='utf-8')
  req={'prompt':prompt,'referenced_image_paths':refs+[str(target)],'transparent_background':False};save(d/'request.json',req)
  save(d/'preparation.json',{'id':id,'preparedAt':now(),'base':{'path':str(BASE),'sha256':sha(BASE)},'crop':c['crop'],'applyBox':c['apply'],'noResize':True,'references':[{'path':p,'sha256':sha(p)} for p in refs+[str(target)]],'requestSha256':sha(d/'request.json'),'actualModel':None,'actualQuality':None})
 print(json.dumps({'directory':str(R),'ids':list(CONFIG)}))
elif sys.argv[1]=='ingest':
 id,source=sys.argv[2],Path(sys.argv[3]);d=R/id;im=Image.open(source);assert im.size==(1254,1254) and im.format=='PNG'
 native=d/'native.png';assert not native.exists();shutil.copyfile(source,native)
 save(d/'receipt.json',{'status':'succeeded_pending_visual_qa','tool':'image_gen.imagegen','route':'builtin','generatedAt':now(),'originalOutputPath':str(source),'sourceSha256':sha(source),'nativePath':str(native),'nativeSha256':sha(native),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,'resizedAfterGeneration':False,'finalArtUpscaled':False,'request':{'path':str(d/'request-with-mask.json'),'sha256':sha(d/'request-with-mask.json')},'preparation':{'path':str(d/'preparation-with-mask.json'),'sha256':sha(d/'preparation-with-mask.json')}})
 print(json.dumps({'id':id,'nativeSha256':sha(native)}))
elif sys.argv[1]=='compose':
 a=np.asarray(Image.open(BASE).convert('RGB')).copy();steps=[]
 for id,c in CONFIG.items():
  d=R/id;native=d/'native.png';assert native.exists();x0,y0,x1,y1=c['apply'];cx,cy,_,_=c['crop'];crop=[x0-cx,y0-cy,x1-cx,y1-cy];new=np.asarray(Image.open(native).convert('RGB').crop(crop),dtype=np.uint32)
  h,w=new.shape[:2];yy,xx=np.indices((h,w));dist=np.minimum.reduce([xx,yy,w-1-xx,h-1-yy]);alpha=np.where(dist==0,0,np.where(dist==1,128,255)).astype('uint8');ap=d/'alpha.png';Image.fromarray(alpha).save(ap)
  old=a[y0:y1,x0:x1].astype('uint32');aa=alpha.astype('uint32')[:,:,None];a[y0:y1,x0:x1]=((new*aa+old*(255-aa)+127)//255).astype('uint8')
  steps.append({'id':id,'native':{'path':str(native),'sha256':sha(native)},'receipt':{'path':str(d/'receipt.json'),'sha256':sha(d/'receipt.json')},'sourceCrop':crop,'placement':c['apply'],'alpha':{'path':str(ap),'sha256':sha(ap)},'formula':'uint8((new_uint32 * alpha_uint32 + old_uint32 * (255-alpha_uint32) + 127) // 255)','featherPixels':2,'resized':False})
 out=T/'candidate/r15_c14-4k-internal-repair-v1-20261012.png';assert not out.exists();Image.fromarray(a).save(out)
 ctx=Image.open(CONTEXT).convert('RGB');ctx.paste(Image.fromarray(a),(115,115));cp=T/'candidate/r15_c14-context-4326-internal-repair-v1-20261012.png';assert not cp.exists();ctx.save(cp)
 old=np.asarray(Image.open(BASE).convert('RGB'));mask=np.zeros((4096,4096),bool)
 for c in CONFIG.values():x0,y0,x1,y1=c['apply'];mask[y0:y1,x0:x1]=True
 assert np.array_equal(a[~mask],old[~mask])
 m={'tile':'r15_c14','createdAt':now(),'base':{'path':str(BASE),'sha256':sha(BASE)},'baseContext':{'path':str(CONTEXT),'sha256':sha(CONTEXT)},'steps':steps,'candidate':{'path':str(out),'sha256':sha(out)},'context':{'path':str(cp),'sha256':sha(cp)},'outsideRepairBoxesUnchanged':True,'oldNeighborPixelsModified':False,'formalAccepted':False,'status':'candidate_pending_local_visual_qa'};save(R/'composition.json',m)
 for id,c in CONFIG.items():Image.fromarray(a).crop(c['crop']).save(R/id/'after-native-1254.png')
 print(json.dumps(m,indent=2))
