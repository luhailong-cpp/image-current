"""Copy the actual built-in output and compose with saved integer alpha."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys,importlib.util
import numpy as np
from PIL import Image,ImageFilter
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;Z=T.parent;D=T/'repairs'/'single-stone-railing-20261012-v2'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
def png(p,im):
    with Path(p).open('xb') as f:im.save(f,format='PNG')
def file(p):return {'path':str(p),'sha256':sha(p)}
def art(p):
    d=file(p)
    with Image.open(p) as im:d['pixels']=list(im.size)
    return d
m=read(D/'preparation.json');original=Path(sys.argv[1]);native=D/'repair-native-1254.png'
with Image.open(original) as im:
    im.load();assert im.format=='PNG' and im.size==(1254,1254) and im.mode in ('RGB','RGBA')
    if im.mode=='RGBA':assert im.getextrema()[3]==(255,255)
if not native.exists():shutil.copyfile(original,native)
assert sha(native)==sha(original)
receipt=D/'receipt.json'
if not receipt.exists():write(receipt,{'savedAtUtc':datetime.now(timezone.utc).isoformat(),'serviceReturnTimeUtc':None,'tool':'image_gen.imagegen','route':'builtin','status':'succeeded_pending_visual_review','actualModel':None,'actualQuality':None,'source':file(original),'output':art(native),'sourceSha256':sha(original),'outputSha256':sha(native),'resizedAfterGeneration':False,'finalArtUpscaled':False})
record=Path(str(native)+'.generation.json')
if not record.exists():write(record,{'id':D.name,'tile':T.name,'file':str(native),'sha256':sha(native),'width':1254,'height':1254,'format':'PNG','mode':Image.open(native).mode,'tool':'image_gen.imagegen','route':'builtin','status':'succeeded_pending_visual_review','actualModel':None,'actualQuality':None,'resizedAfterGeneration':False,'finalArtUpscaled':False,'activeLogicalPatch':False,'repairBoxIn4096':m['cropBoxIn4096'],'request':file(D/'request.json'),'prompt':file(D/'prompt.txt'),'references':m['references'],'preparation':file(D/'preparation.json'),'receipt':file(receipt),'originalOutputPath':str(original)})
for item in [m['sourceCandidate'],m['sourceContext'],m['sourceAssembly'],m['target'],*m['references']]:assert sha(item['path'])==item['sha256']
assert read(D/'request.json')['referenced_image_paths']==[x['path'] for x in m['references']]
box=m['cropBoxIn4096'];base=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));old=base[box[1]:box[3],box[0]:box[2]].copy();new=np.array(Image.open(native).convert('RGB'));assert np.array_equal(old,np.array(Image.open(m['target']['path']).convert('RGB')))
spec=importlib.util.spec_from_file_location('_repair_seam',Z/'assemble_candidate.py');algo=importlib.util.module_from_spec(spec);spec.loader.exec_module(algo)
b=64;h,w=old.shape[:2]
paths={'top':algo.minimum_vertical_seam(old[:b].transpose(1,0,2),new[:b].transpose(1,0,2)),'bottom':algo.minimum_vertical_seam(old[-b:].transpose(1,0,2),new[-b:].transpose(1,0,2)),'left':algo.minimum_vertical_seam(old[:,:b],new[:,:b]),'right':algo.minimum_vertical_seam(old[:,-b:],new[:,-b:])}
a=np.full((h,w),255,np.uint8)
a[:b]=np.where(np.arange(b)[:,None]>=paths['top'][None,:],255,0)
a[-b:]=np.where(np.arange(b)[:,None]<paths['bottom'][None,:],255,0)
a[:,:b]=np.minimum(a[:,:b],np.where(np.arange(b)[None,:]>=paths['left'][:,None],255,0).astype(np.uint8))
a[:,-b:]=np.minimum(a[:,-b:],np.where(np.arange(b)[None,:]<paths['right'][:,None],255,0).astype(np.uint8))
a=np.array(Image.fromarray(a).filter(ImageFilter.GaussianBlur(2)));a[[0,-1]]=0;a[:,[0,-1]]=0
png(D/'alpha.png',Image.fromarray(a))
with (D/'seam-paths.npz').open('xb') as f:np.savez_compressed(f,**paths)
mixed=((old.astype(np.uint32)*(255-a[:,:,None])+new.astype(np.uint32)*a[:,:,None]+127)//255).astype(np.uint8)
base[box[1]:box[3],box[0]:box[2]]=mixed
candidate=D/'candidate-4096.png';context=D/'context-4326.png'
png(candidate,Image.fromarray(base));ctx=np.array(Image.open(m['sourceContext']['path']).convert('RGB'));ctx[115:4211,115:4211]=base;png(context,Image.fromarray(ctx))
png(D/'composed-local-1254.png',Image.fromarray(mixed))
rects={'top-boundary':[box[0],box[1]-256,box[2],box[1]+256],'bottom-boundary':[box[0],box[3]-256,box[2],box[3]+256],'left-boundary':[box[0]-256,box[1],box[0]+256,box[3]],'right-boundary':[box[2]-256,box[1],box[2]+256,box[3]]}
qa=[]
for name,rect in rects.items():
    p=D/(name+'-100pct.png');png(p,Image.fromarray(base).crop(rect));qa.append(dict(art(p),cropBoxIn4096=rect,resized=False))
manifest={'schemaVersion':1,'tile':T.name,'version':D.name,'composedAtUtc':datetime.now(timezone.utc).isoformat(),'sourceCandidate':m['sourceCandidate'],'sourceContext':m['sourceContext'],'sourceAssembly':m['sourceAssembly'],'native':art(native),'generationRecord':file(record),'preparation':file(D/'preparation.json'),'request':file(D/'request.json'),'prompt':file(D/'prompt.txt'),'receipt':file(receipt),'alpha':art(D/'alpha.png'),'seamPaths':file(D/'seam-paths.npz'),'compositor':file(__file__),'algorithm':file(Z/'assemble_candidate.py'),'nativeCrop':[0,0,1254,1254],'pasteBoxIn4096':box,'blendArithmetic':'(old*(255-alpha)+new*alpha+127)//255 uint32','method':'minimum-error paths in four 64px perimeter bands, radius2 on alpha only; exact original/native RGB samples','resampling':False,'RGBColorCorrection':False,'layoutOnlyPixelsComposited':False,'candidate':art(candidate),'context':art(context),'QAImages':qa,'status':'independent_trial_pending_boundary_review','formalAccepted':False}
write(D/'composition.json',manifest)
# Independently replay saved alpha and compare the two saved outputs exactly.
saved=np.array(Image.open(D/'alpha.png'));replay=np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'));replay[box[1]:box[3],box[0]:box[2]]=((old.astype(np.uint32)*(255-saved[:,:,None])+new.astype(np.uint32)*saved[:,:,None]+127)//255).astype(np.uint8)
assert np.array_equal(replay,np.array(Image.open(candidate).convert('RGB')))
assert np.array_equal(replay,np.array(Image.open(context).convert('RGB'))[115:4211,115:4211])
outside=np.ones((4096,4096),bool);outside[box[1]:box[3],box[0]:box[2]]=False
assert np.array_equal(replay[outside],np.array(Image.open(m['sourceCandidate']['path']).convert('RGB'))[outside])
write(D/'replay-verification.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'candidateExactReplay':True,'contextCoreExactMatch':True,'outsideRepairBoxUnchanged':True,'originalOutputByteIdentical':True,'composition':file(D/'composition.json'),'candidate':art(candidate),'formalAccepted':False})
print(json.dumps({'candidate':art(candidate),'composition':file(D/'composition.json'),'reviewImages':qa}))
