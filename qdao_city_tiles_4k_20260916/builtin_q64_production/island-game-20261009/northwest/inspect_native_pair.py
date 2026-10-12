"""Read-only source validation and mechanical native pair QA, including fixed core cut."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,argparse,runpy
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--first',required=True);ap.add_argument('--second',required=True);ap.add_argument('--axis',choices=['horizontal','vertical'],required=True);ap.add_argument('--output-dir',required=True);a=ap.parse_args()
q=Path(a.output_dir).resolve();assert q.is_relative_to(Z) and not q.exists()
m=runpy.run_path(str(Z/'assemble_tile.py'),run_name='pair_qa')
sources=[];arrays=[]
for stem in (a.first,a.second):
 p=Z/'native'/f'{stem}.png';r=int(stem[9:11])-1;c=int(stem[12:14])-1
 s,im=m['load_raw_source'](p,Path(str(p)+'.generation.json'),stem[:7],r,c);sources.append(s);arrays.append(im)
b0,b1=[s['globalNativeBox'] for s in sources]
vertical=a.axis=='vertical'
assert (b1[0]-b0[0],b1[1]-b0[1])==((0,1024) if vertical else (1024,0))
x,y=[im.transpose(1,0,2) if vertical else im for im in arrays]
err=((x[:,1024:].astype(float)-y[:,:230].astype(float))**2).mean(2)
path,stats=m['minimum_path'](err)
def join(cuts):
 out=np.empty((1254,2278,3),np.uint8)
 for row,v in enumerate(cuts):
  split=1024+int(v);out[row,:split]=x[row,:split];out[row,split:]=y[row,int(v):]
  assert np.array_equal(out[row,:split],x[row,:split]) and np.array_equal(out[row,split:],y[row,int(v):])
 return out.transpose(1,0,2) if vertical else out
dp=join(path);fixed=join(np.full(1254,115));q.mkdir(parents=True)
outputs=[]
for name,im in [('hard_minerror_native',dp),('fixed_core115_native',fixed)]:
 crop=im[875:1405,:] if vertical else im[:,875:1405]
 p=q/f'{name}_seam100pct.png';Image.fromarray(crop).save(p);outputs.append(dict(path=p.as_posix(),sha256=sha(p),nativeSize=list(Image.open(p).size)))
 p=q/f'{name}_pair.png';Image.fromarray(im).save(p);outputs.append(dict(path=p.as_posix(),sha256=sha(p),nativeSize=list(Image.open(p).size)))
rec=dict(operation='read-only native pair QA using exact same-global-coordinate source selection',sources=sources,axis=a.axis,overlapPixels=230,dpPath=path.tolist(),dpStatistics=stats,fixedCoreCut=115,resizing=False,feathering=False,registration=False,colorCorrection=False,pixelSynthesis=False,outputs=outputs,visualStatus='pending',crossTileAccepted=False)
(q/'join_record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(qa=q.as_posix(),dpStatistics=stats,crossTileAccepted=False)))
