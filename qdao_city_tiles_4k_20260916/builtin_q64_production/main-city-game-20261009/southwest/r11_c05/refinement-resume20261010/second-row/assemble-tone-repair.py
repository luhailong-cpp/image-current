from pathlib import Path
import json,hashlib,shutil,sys,runpy
from datetime import datetime,timezone
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;T=D.parent.parent;R=T.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def arr(p):return np.array(Image.open(p).convert('RGB'))
def savej(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def saveim(p,a):Image.fromarray(a).save(p,optimize=True);return {'file':str(p),'sha256':sha(p),'pixels':[a.shape[1],a.shape[0]],'resampled':False}
id='row2-x2048-tone';req=read(D/'prompts'/f'{id}.request.json');receipt=D/'receipts'/f'{id}.receipt.json';src=Path(sys.argv[1]);native=D/'native'/f'{id}.png'
assert not native.exists();im=Image.open(src);assert im.size==(1254,1254)
for ref in req['references']:assert sha(ref['file'])==ref['sha256']
assert sha(req['promptFile'])==req['promptSha256'];shutil.copyfile(src,native);assert sha(src)==sha(native)
rec={'id':id,'file':str(native),'sha256':sha(native),'sourceOutput':str(src),'sourceOutputSha256':sha(src),'width':1254,'height':1254,'mode':im.mode,'format':'PNG','opaque':True,'route':'builtin','tool':'image_gen.imagegen','nativePixelsPreserved':True,'resizedAfterGeneration':False,'actualModel':None,'actualQuality':None,'prompt':req['promptFile'],'promptSha256':req['promptSha256'],'references':req['references'],'request':str(D/'prompts'/f'{id}.request.json'),'receipt':str(receipt),'receiptSha256':sha(receipt),'sourceContext':req['sourceContext'],'cropWorldBox':req['cropWorldBox'],'generatedAtUtc':datetime.now(timezone.utc).isoformat()}
savej(D/'native'/f'{id}.png.generation.json',rec)
context_path=Path(req['sourceContext']['file']);assert sha(context_path)==req['sourceContext']['sha256'];context=arr(context_path);target=arr(req['references'][0]['file']);generated=arr(native)
assert np.array_equal(context[1024:2278,1536:2790],target)
box=[0,50,1254,625];x0,y0,x1,y1=box;old=target[y0:y1,x0:x1];new=generated[y0:y1,x0:x1];h,w=old.shape[:2];halo=20;radius=2
api=runpy.run_path(str(R/'local_repairs.py'),run_name='readonly_closed_material_seam')
for name in ['minimum_error_path','inclusion_mask']:api[name].__globals__['HALO']=halo
strips={'left':(old[:,:halo],new[:,:halo]),'right':(old[:,-halo:][:,::-1],new[:,-halo:][:,::-1]),'top':(old[:halo].transpose(1,0,2),new[:halo].transpose(1,0,2)),'bottom':(old[-halo:][::-1].transpose(1,0,2),new[-halo:][::-1].transpose(1,0,2))}
masks={};seams={}
for side,(a,b) in strips.items():
 seam=api['minimum_error_path'](a,b,radius);masks[side]=api['inclusion_mask'](seam,radius);seams[side]=seam.tolist()
alpha=np.full((h,w),255,dtype=np.uint8)
alpha[:,:halo]=np.minimum(alpha[:,:halo],masks['left']);alpha[:,-halo:]=np.minimum(alpha[:,-halo:],masks['right'][:,::-1]);alpha[:halo]=np.minimum(alpha[:halo],masks['top'].T);alpha[-halo:]=np.minimum(alpha[-halo:],masks['bottom'].T[::-1])
assert not any(a.any() for a in [alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
weight=alpha.astype(np.uint32)[...,None];local=((old.astype(np.uint32)*(255-weight)+new.astype(np.uint32)*weight+127)//255).astype(np.uint8)
out=context.copy();out[1074:1649,1536:2790]=local
check=out.copy();check[1074:1649,1536:2790]=context[1074:1649,1536:2790];assert np.array_equal(check,context)
assert np.array_equal(out[:1024],context[:1024]);assert np.array_equal(out[2048:],context[2048:])
O=D/'output'/'tone-v1';Q=D/'qa'/'tone-v1';O.mkdir(parents=True,exist_ok=True);Q.mkdir(parents=True,exist_ok=True)
outputs={'context':saveim(O/'r11-p01-p02.repaired.context.png',out),'core':saveim(O/'r11-p01-p02.repaired.core.png',out[115:2163,115:4211])}
for label,a in [('before',context),('after',out)]:
 saveim(Q/f'target-{label}.png',a[1024:2278,1536:2790]);saveim(Q/f'stairs-{label}.png',a[1074:1660,1200:3050])
 core=a[115:2163,115:4211]
 for x in (1024,2048,3072):saveim(Q/f'second-row-x{x}-{label}.png',core[1024:,x-320:x+320])
saveim(Q/'two-rows-core.png',out[115:2163,115:4211])
report={'status':'pending_visual_review','formalAccepted':False,'script':str(Path(__file__)),'scriptSha256':sha(Path(__file__)),'inputContext':req['sourceContext'],'newNative':{'file':str(native),'sha256':sha(native),'generationRecord':str(D/'native'/f'{id}.png.generation.json'),'generationRecordSha256':sha(D/'native'/f'{id}.png.generation.json')},'usedNativeBox':box,'affectedContextBox':[1536,1074,2790,1649],'affectedWorldBox':[17805,41919,19059,42494],'closedSeam':{'sourceAlgorithm':str(R/'local_repairs.py'),'sourceAlgorithmSha256':sha(R/'local_repairs.py'),'haloOverride':halo,'maximumFeatherRadius':radius,'seams':seams,'alphaSha256':hashlib.sha256(alpha.tobytes()).hexdigest()},'outsideAffectedBoxUnchanged':True,'firstRowContext0to1024Exact':True,'bottom230Exact':True,'sourceResampling':False,'colorAdjustment':False,'warping':False,'outputs':outputs}
savej(O/'repair-assembly.json',report);print(json.dumps({'outputs':outputs,'affectedContextBox':report['affectedContextBox'],'bottom230Exact':True},indent=2))
