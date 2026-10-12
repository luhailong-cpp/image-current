from pathlib import Path
import json,hashlib,runpy
from datetime import datetime,timezone
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;SW=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def jsave(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def saveim(p,a):Image.fromarray(a).save(p,optimize=True);return {'path':str(p),'sha256':sha(p),'pixels':[a.shape[1],a.shape[0]],'resampled':False}
req=read(D/'request-v2.json')
for ref in req['references']:assert sha(ref['path'])==ref['sha256']
assert sha(req['promptPath'])==req['promptSha256']
src=Path(r"C:\Users\luyua\.codex\generated_images\01a12568-32a5-7300-bfbe-f5de662c1aa1\exec-f45dc3bd-17c2-49f6-b0e5-7518d501f19d.png");native=D/'native/p04_02-joint-v2.png';assert sha(src)==sha(native)
im=Image.open(native);assert im.size==(1254,1254)
A=np.array(Image.open(req['references'][0]['path']).convert('RGB'));B=np.array(im.convert('RGB'))
receipt=D/'receipts/p04_02-joint-v2.receipt.json'
rec={'id':req['id'],'path':str(native),'sha256':sha(native),'sourceOutput':str(src),'sourceOutputSha256':sha(src),'width':1254,'height':1254,'mode':im.mode,'format':im.format,'route':'builtin','tool':'image_gen.imagegen','nativePixelsPreserved':True,'resizedAfterGeneration':False,'actualModel':None,'actualQuality':None,'prompt':req['promptPath'],'promptSha256':req['promptSha256'],'references':req['references'],'request':str(D/'request-v2.json'),'requestSha256':sha(D/'request-v2.json'),'receipt':str(receipt),'receiptSha256':sha(receipt),'generatedAtUtc':datetime.now(timezone.utc).isoformat()}
jsave(D/'native/p04_02-joint-v2.png.generation.json',rec)
box=[310,510,840,965];x0,y0,x1,y1=box;old=A[y0:y1,x0:x1];new=B[y0:y1,x0:x1];h,w=old.shape[:2];halo=20;radius=2
api=runpy.run_path(str(SW/'local_repairs.py'),run_name='readonly_closed_joint_seam')
for name in ['minimum_error_path','inclusion_mask']:api[name].__globals__['HALO']=halo
strips={'left':(old[:,:halo],new[:,:halo]),'right':(old[:,-halo:][:,::-1],new[:,-halo:][:,::-1]),'top':(old[:halo].transpose(1,0,2),new[:halo].transpose(1,0,2)),'bottom':(old[-halo:][::-1].transpose(1,0,2),new[-halo:][::-1].transpose(1,0,2))}
masks={};seams={}
for side,(a,b) in strips.items():
 seam=api['minimum_error_path'](a,b,radius);masks[side]=api['inclusion_mask'](seam,radius);seams[side]=seam.tolist()
alpha=np.full((h,w),255,dtype=np.uint8)
alpha[:,:halo]=np.minimum(alpha[:,:halo],masks['left']);alpha[:,-halo:]=np.minimum(alpha[:,-halo:],masks['right'][:,::-1]);alpha[:halo]=np.minimum(alpha[:halo],masks['top'].T);alpha[-halo:]=np.minimum(alpha[-halo:],masks['bottom'].T[::-1])
assert not any(a.any() for a in [alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
weight=alpha.astype(np.uint32)[...,None];patch=((old.astype(np.uint32)*(255-weight)+new.astype(np.uint32)*weight+127)//255).astype(np.uint8)
fixed=A.copy();fixed[y0:y1,x0:x1]=patch
assert np.array_equal(fixed[:230],A[:230]) and np.array_equal(fixed[-230:],A[-230:]) and np.array_equal(fixed[:,:230],A[:,:230]) and np.array_equal(fixed[:,-230:],A[:,-230:])
check=fixed.copy();check[y0:y1,x0:x1]=A[y0:y1,x0:x1];assert np.array_equal(check,A)
O=D/'output/v2';Q=D/'qa/v2';O.mkdir(exist_ok=True,parents=True);Q.mkdir(exist_ok=True,parents=True)
outputs={'nativeCandidate':saveim(O/'p04_02.joint-fixed.candidate.png',fixed),'patch':saveim(O/'p04_02.joint-fixed.overlay.patch.png',patch)}
for label,a in [('before',A),('generated',B),('candidate',fixed)]:
 saveim(Q/f'incoming-{label}.png',a[820:1000,270:450])
 saveim(Q/f'junction-{label}.png',a[495:635,725:855])
 saveim(Q/f'extension-{label}.png',a[490:990,280:870])
alignment=[]
for x in [0,100,200,230,250,280,300,320,350]:
 a=int(800+np.argmin(A[800:1200,x].mean(1)));b=int(800+np.argmin(fixed[800:1200,x].mean(1)))
 alignment.append({'x':x,'originalY':a,'candidateY':b,'deltaY':b-a})
report={'status':'pending_visual_review','formalAccepted':False,'newNative':rec,'inputNative':req['references'][0],'usedNativeBox':box,'patchPasteNativeXY':[x0,y0],'affectedContextBox':[x0+1024,y0+3072,x1+1024,y1+3072],'affectedTileCoreBox':[x0+909,y0+2957,x1+909,y1+2957],'affectedWorldBox':[x0+17293,y0+43917,x1+17293,y1+43917],'closedSeam':{'sourceAlgorithm':str(SW/'local_repairs.py'),'sourceAlgorithmSha256':sha(SW/'local_repairs.py'),'haloOverride':halo,'maximumFeatherRadius':radius,'seams':seams,'alphaSha256':hashlib.sha256(alpha.tobytes()).hexdigest()},'fourOuter230PixelBandsExact':True,'outsideAffectedBoxUnchanged':True,'originalNativeUnmodified':True,'incomingJointAlignment':alignment,'resampling':False,'colorAdjustment':False,'warping':False,'outputs':outputs,'script':str(Path(__file__)),'scriptSha256':sha(Path(__file__))}
jsave(O/'repair-assembly.json',report)
print(json.dumps({'outputs':outputs,'affectedContextBox':report['affectedContextBox'],'locked230':True,'incomingAlignment':alignment},indent=2))

