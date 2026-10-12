from pathlib import Path
import json,hashlib,runpy
from datetime import datetime,timezone
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;T=D.parent;R=T.parent
Q=D/'qa';O=D/'output';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def img(p):return np.array(Image.open(p).convert('RGB'))
def saveim(p,a):Image.fromarray(a).save(p,optimize=True);return {'file':str(p),'sha256':sha(p),'width':a.shape[1],'height':a.shape[0],'resized':False}
def savej(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
algorithm=runpy.run_path(str(R/'assemble.py'),run_name='readonly_native_assembly')
border_api=runpy.run_path(str(R/'border_assembly.py'),run_name='readonly_border_algorithm')
new={};old={};sources=[]
for col in range(1,5):
 name=f'p01_{col:02d}';rp=D/'native'/f'{name}.png.generation.json';rec=read(rp)
 assert sha(rec['file'])==rec['sha256']
 assert sha(rec['prompt'])==rec['promptSha256']
 for ref in rec['references']:assert sha(ref['file'])==ref['sha256']
 receipt=read(rec['receipt']);assert receipt['status']=='returned_image'
 new[(1,col)]=img(rec['file']);old[(1,col)]=img(T/'native'/f'{name}.png')
 sources.append({'record':str(rp),'recordSha256':sha(rp),'nativeSha256':rec['sha256'],'receipt':rec['receipt'],'receiptSha256':sha(rec['receipt']),'fixedBandMeasurements':rec['fixedBandMeasurements']})
fresh,metrics=algorithm['assemble_pixels'](new,(1,1,1,4),2)
original,_=algorithm['assemble_pixels'](old,(1,1,1,4),2)
assert np.array_equal(original,img(T/'borders'/'r11-p01.original.context.png'))
border=img(T/'borders'/'r10-south-native-overlap.png')
north,north_record=border_api['quilt'](algorithm,border,fresh,2)
candidate=north.copy()
# Preserve original lower 230px for the already-running next row. Transition
# only by a bounded 2px mechanical seam above the owned lower band.
start,end=794,1024
a=north[start:end];b=original[start:end]
seam=algorithm['minimum_seam'](np.transpose(a[2:228],(1,0,2)),np.transpose(b[2:228],(1,0,2)))+2
alpha=algorithm['feather_mask'](seam,230,2).T
candidate[start:end]=algorithm['blend_exact'](a,b,alpha)
candidate[end:]=original[end:]
assert np.array_equal(candidate[:116],border[:116])
assert np.array_equal(candidate[1024:],original[1024:])
outputs={}
for name,a in [('raw-context',fresh),('north-fixed-context',north),('north-and-bottom-fixed-context',candidate)]:
 outputs[name]=saveim(O/f'r11-p01.{name}.png',a)
 outputs[name.replace('context','core')]=saveim(O/f'r11-p01.{name.replace("context","core")}.png',a[115:1139,115:4211])
final10=R/'r10_c05'/'repairs'/'output'/'r10_c05.repaired.candidate.png'
assert sha(final10)=='f228d0e07c4ed329bdcce87a46abb0ddeb48c9688dab1d86b33456051797ecad'
prev=img(final10)
for name,a in [('original',original),('raw',fresh),('north-fixed',north),('candidate',candidate)]:
 core=a[115:1139,115:4211]
 joined=np.concatenate((prev[-320:],core[:480]),axis=0)
 saveim(Q/f'north-{name}.png',joined)
 for col in range(4):saveim(Q/f'north-{name}-c{col+1}.png',joined[:,col*1024:(col+1)*1024])
 for x in (1024,2048,3072):saveim(Q/f'vertical-{name}-x{x}.png',core[:,x-256:x+256])
 saveim(Q/f'south-transition-{name}.png',core[600:])
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'native_candidate_pending_visual_review','selected':False,'formalAccepted':False,'algorithm':str(R/'assemble.py'),'algorithmSha256':sha(R/'assemble.py'),'borderAlgorithm':str(R/'border_assembly.py'),'borderAlgorithmSha256':sha(R/'border_assembly.py'),'sources':sources,'outputs':outputs,'internalSeamMetrics':metrics,'northComposition':north_record,'bottomComposition':{'regionContextY':[start,end],'fullOriginalOwnedFromContextY':1024,'seamYByContextX':(seam+start).tolist(),'featherRadiusPixels':2,'originalBottom230PixelExact':True},'r10FinalUnchanged':True,'nativeDimensions':[1254,1254],'actualModel':None,'actualQuality':None,'sourceResampling':False,'colorAdjustment':False,'geometryWarping':False}
savej(O/'assembly.json',report)
savej(D/'selection-proposed.json',{'status':'pending_visual_review_do_not_apply','suggestedNativeSources':{f'p01_{c:02d}':f'refinement-resume20261010/native/p01_{c:02d}.png.generation.json' for c in range(1,5)},'lowerBoundaryMustUseOriginal230px':True,'compositeCandidate':outputs['north-and-bottom-fixed-context'],'formalAccepted':False})
print(json.dumps({'status':report['status'],'output':outputs['north-and-bottom-fixed-context'],'core':outputs['north-and-bottom-fixed-core'],'lower230Exact':True,'r10Unchanged':True},indent=2))
