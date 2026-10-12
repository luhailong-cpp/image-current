from pathlib import Path
import sys
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T.parent))
import production_v2 as p
import assemble_native as A
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
prev=T/'qa/trial-bottom-floor-cap-02/index.json';m=p.read(prev);base=p.read(m['priorAssembly']['file']);pix=np.array(Image.open(m['candidate']['file']).convert('RGB'));own=np.array(Image.open(m['sourceIndex']['file']));bp=np.array(Image.open(base['output']['file']).convert('RGB'));bo=np.array(Image.open(base['sourceIndex']['file']));x,y,x2,y2=1007,3832,1047,3856
pix[y:y2,x:x2]=bp[y:y2,x:x2];own[y:y2,x:x2]=bo[y:y2,x:x2]
sources=m['sources'];proof=[]
for i,s in enumerate(sources):
 ys,xs=np.where(own==i);im=np.array(Image.open(s['file']).convert('RGB'));ox,oy=s['tileOriginXY'];assert np.array_equal(pix[ys,xs],im[ys-oy,xs-ox]);proof.append({'sourceIndex':i,'pixelCount':int(len(xs)),'exactNativePixels':True})
D=T/'qa/trial-bottom-floor-cap-02-trimmed';D.mkdir(exist_ok=True);assert not (D/'index.json').exists();im=Image.fromarray(pix);out=A.save_png(im,D/'candidate.png');oi=A.save_png(Image.fromarray(own),D/'source-index.png');qa=A.write_qa(im,out,D/'internal');entries=[]
for name,box in {'cap-and-perimeter':[724,3507,1324,4096],'trim-detail':[944,3752,1104,3912],'bottom-detail':[924,3900,1124,4096]}.items():
 e=A.save_png(im.crop(box),D/(name+'.png'));e.update(name=name,cropLTRB=box,nativePixelScale=1,actuallyViewed=False);entries.append(e)
p.write_json(D/'index.json',{'candidate':out,'sourceIndex':oi,'sources':sources,'pixelProof':proof,'fullNativePixelProof':True,'resampled':False,'blended':False,'priorTrial':ref(prev),'restoredOriginalSourceRegion':{'tileROI':[x,y,x2,y2],'sourceAssembly':m['priorAssembly'],'note':'Original native pixels below the actual outgoing grout endpoint remove a generated nine-pixel overshoot; no pixel value synthesized.'},'internalQa':qa,'entries':entries,'formalAccepted':False},replace=False);print(out)
