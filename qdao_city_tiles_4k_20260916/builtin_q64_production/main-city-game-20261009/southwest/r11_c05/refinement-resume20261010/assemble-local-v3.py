from pathlib import Path
import json,hashlib,shutil,sys,runpy
from datetime import datetime,timezone
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;R=D.parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def savej(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def arr(p):return np.array(Image.open(p).convert('RGB'))
def saveim(p,a):Image.fromarray(a).save(p,optimize=True);return {'file':str(p),'sha256':sha(p),'width':a.shape[1],'height':a.shape[0],'resized':False}
id='local-stair-join-v3';req=read(D/'prompts'/f'{id}.request.json');receipt=D/'receipts'/f'{id}.receipt.json'
src=Path(sys.argv[1]);native=D/'native'/f'{id}.png';assert not native.exists();im=Image.open(src);assert im.size==(1254,1254)
for ref in req['references']:assert sha(ref['file'])==ref['sha256']
shutil.copyfile(src,native);assert sha(src)==sha(native)
rec={'id':id,'file':str(native),'sha256':sha(native),'sourceOutput':str(src),'sourceOutputSha256':sha(src),'width':1254,'height':1254,'mode':im.mode,'format':'PNG','opaque':True,'route':'builtin','tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'nativePixelsPreserved':True,'resizedAfterGeneration':False,'prompt':req['promptFile'],'promptSha256':req['promptSha256'],'references':req['references'],'request':str(D/'prompts'/f'{id}.request.json'),'receipt':str(receipt),'receiptSha256':sha(receipt),'sourceContext':req['sourceContext'],'usedNativeCrop':[500,510,756,606],'generatedAtUtc':datetime.now(timezone.utc).isoformat()}
savej(D/'native'/f'{id}.png.generation.json',rec)
context_path=Path(req['sourceContext']['file']);assert sha(context_path)==req['sourceContext']['sha256'];context=arr(context_path);target=arr(req['references'][0]['file']);generated=arr(native)
assert np.array_equal(context[:,2500:3754],target)
old=target[510:606,500:756];new=generated[510:606,500:756];h,w=old.shape[:2];halo=16;radius=2
api=runpy.run_path(str(R/'local_repairs.py'),run_name='readonly_local_closed_seam')
for name in ['minimum_error_path','inclusion_mask']:api[name].__globals__['HALO']=halo
strips={'left':(old[:,:halo],new[:,:halo]),'right':(old[:,-halo:][:,::-1],new[:,-halo:][:,::-1]),'top':(old[:halo].transpose(1,0,2),new[:halo].transpose(1,0,2)),'bottom':(old[-halo:][::-1].transpose(1,0,2),new[-halo:][::-1].transpose(1,0,2))}
masks={};seams={}
for side,(a,b) in strips.items():
 seam=api['minimum_error_path'](a,b,radius);masks[side]=api['inclusion_mask'](seam,radius);seams[side]=seam.tolist()
alpha=np.full((h,w),255,dtype=np.uint8)
alpha[:,:halo]=np.minimum(alpha[:,:halo],masks['left']);alpha[:,-halo:]=np.minimum(alpha[:,-halo:],masks['right'][:,::-1]);alpha[:halo]=np.minimum(alpha[:halo],masks['top'].T);alpha[-halo:]=np.minimum(alpha[-halo:],masks['bottom'].T[::-1])
assert not any(a.any() for a in [alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
assert np.all(alpha[halo:-halo,halo:-halo]==255)
weight=alpha.astype(np.uint32)[...,None];local=((old.astype(np.uint32)*(255-weight)+new.astype(np.uint32)*weight+127)//255).astype(np.uint8)
out=context.copy();out[510:606,3000:3256]=local
check=out.copy();check[510:606,3000:3256]=context[510:606,3000:3256];assert np.array_equal(check,context)
assert np.array_equal(out[:116],context[:116]) and np.array_equal(out[1024:],context[1024:])
O=D/'output'/'v3';Q=D/'qa'/'v3';O.mkdir(parents=True,exist_ok=True);Q.mkdir(parents=True,exist_ok=True)
outputs={'context':saveim(O/'r11-p01.repaired.context.png',out),'core':saveim(O/'r11-p01.repaired.core.png',out[115:1139,115:4211])}
for label,a in [('before',context),('after',out)]:saveim(Q/f'local-groove-{label}.png',a[400:720,2850:3400])
report={'status':'pending_visual_review','formalAccepted':False,'script':str(Path(__file__)),'scriptSha256':sha(Path(__file__)),'baseContext':req['sourceContext'],'nativeRepairRecord':str(D/'native'/f'{id}.png.generation.json'),'nativeRepairRecordSha256':sha(D/'native'/f'{id}.png.generation.json'),'nativeUsedBox':[500,510,756,606],'targetContextBox':[3000,510,3256,606],'closedSeam':{'algorithm':str(R/'local_repairs.py'),'algorithmSha256':sha(R/'local_repairs.py'),'functions':['minimum_error_path','inclusion_mask'],'haloOverride':16,'rectanglePixels':[w,h],'featherRadiusPixels':2,'seams':seams,'alphaSha256':hashlib.sha256(alpha.tobytes()).hexdigest(),'cornerRule':'minimum of four inclusion masks'},'allPixelsOutsideTargetContextBoxUnchanged':True,'top116Unchanged':True,'bottom230Unchanged':True,'outputs':outputs,'resampling':False,'colorAdjustment':False,'geometryWarping':False}
savej(O/'local-repair-assembly.json',report);print(json.dumps(outputs,indent=2))
