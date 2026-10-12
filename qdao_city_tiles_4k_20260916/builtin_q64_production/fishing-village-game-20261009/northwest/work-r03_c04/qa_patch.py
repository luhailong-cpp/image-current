from pathlib import Path
import sys, json, hashlib, importlib.util
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent; R=W.parent
spec=importlib.util.spec_from_file_location('assembler',W/'assemble_r03_c04.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ident=sys.argv[1]; base=ident.rsplit('_v',1)[0]
g=W/'guides'/f'{base}.layout-and-native-overlap.png';p=R/'native'/f'{ident}.png'
d=json.loads(Path(str(g)+'.derivation.json').read_text(encoding='utf-8'))
a=np.array(Image.open(g).convert('RGB'));b=np.array(Image.open(p).convert('RGB'))
N=1254;O=230; qa=W/'qa'; details=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(axis):
 x,y=(a[:,:O],b[:,:O]) if axis=='west' else (a[:O].transpose(1,0,2),b[:O].transpose(1,0,2))
 seam,cost=m.minimum_vertical_seam(x,y);mask=np.arange(O)[None,:]>=seam[:,None]
 merged=np.where(mask[...,None],y,x)
 patch=b.copy()
 if axis=='west':patch[:,:O]=merged;crop=patch[:,:430]
 else:patch[:O]=merged.transpose(1,0,2);crop=patch[:430]
 out=qa/f'{ident}.{axis}-actual230-100pct.png';Image.fromarray(crop).save(out)
 details.append({'axis':axis,'pathLocal':seam.tolist(),'cost':cost,'cropFile':str(out),'note':'Native pixels only; guide-provided overlap; full tile/corner and external-row-composite QA still required'})
if any(n['destinationBox'][0]==0 and n['destinationBox'][2]==O and n['destinationBox'][3]-n['destinationBox'][1]==N for n in d['neighbors']):emit('west')
if any(n['destinationBox'][1]==0 and n['destinationBox'][3]==O and n['destinationBox'][2]-n['destinationBox'][0]==N for n in d['neighbors']):emit('north')
if any(n['destinationBox'][1]==1024 and n['destinationBox'][3]==1254 and n['destinationBox'][2]-n['destinationBox'][0]==N for n in d['neighbors']):
 x=b[-O:].transpose(1,0,2);y=a[-O:].transpose(1,0,2);seam,cost=m.minimum_vertical_seam(x,y);mask=np.arange(O)[None,:]>=seam[:,None];merged=np.where(mask[...,None],y,x);patch=b.copy();patch[-O:]=merged.transpose(1,0,2);out=qa/f'{ident}.south-actual230-100pct.png';Image.fromarray(patch[-430:]).save(out);details.append({'axis':'south','pathLocal':seam.tolist(),'cost':cost,'cropFile':str(out),'note':'Bottom230 exact native southern neighbor pixels; candidate patch top, southern source bottom. Corners need final composite QA.'})
(qa/f'{ident}.actual230-diagnostic.json').write_text(json.dumps({'native':str(p),'sha256':sha(p),'guide':str(g),'guideSha256':sha(g),'joins':details,'visualAcceptance':None,'resample':False,'blend':False},indent=2),encoding='utf-8')
print(json.dumps({'native':ident,'diagnostics':[d['cropFile'] for d in details]}))
