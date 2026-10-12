"""Native same-coordinate candidate neighbor seam inspection; guide pixels excluded."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
import assemble_tile as assembly
import apply_native_tile_repair as repair
Z=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--stem',required=True);a=p.parse_args()
assert a.stem.startswith(('r05_c02_','r06_c02_'))
q=Z/'qa'/('native_'+a.stem);q.mkdir(exist_ok=False)
ip=Z/'guides'/(a.stem+'.input.json');meta=json.loads(ip.read_text(encoding='utf-8-sig'))
source,raw=assembly.load_raw_source(Z/'native'/(a.stem+'.png'),Z/'native'/(a.stem+'.png.generation.json'),a.stem[:7],int(a.stem[9:11])-1,int(a.stem[12:14])-1)
checks=[]
for n in meta['neighbor']:
 repair.pinned(n,Z,'neighbor exact hash')
 neighbor=np.array(Image.open(n['path']).convert('RGB'));assert neighbor.shape==(1254,1254,3)
 d=n['direction'];assert d in ('top','left','right')
 aa,bb=(neighbor,raw) if d in ('left','top') else (raw,neighbor)
 if d=='top':aa,bb=aa.transpose(1,0,2),bb.transpose(1,0,2)
 delta=aa[:,1024:].astype(float)-bb[:,:230].astype(float)
 path,stats=assembly.minimum_path(np.mean(delta*delta,axis=2))
 combined=np.empty((1254,2278,3),dtype=np.uint8)
 for y,cut in enumerate(path):
  x=1024+int(cut);combined[y,:x]=aa[y,:x];combined[y,x:]=bb[y,int(cut):]
 crop=combined[:,850:1420]
 if d=='top':crop=crop.transpose(1,0,2)
 out=q/(d+'_minerror_100pct.png');Image.fromarray(crop).save(out)
 checks.append({'direction':d,'neighbor':n,'output':repair.file_info(out),'nativeScale100Percent':True,'pathByScanline':path.tolist(),'statistics':stats})
(q/'seams.json').write_text(json.dumps({'status':'unreviewed','target':source,'checks':checks,'allPixelsOriginalSameCoordinates':True,'resizing':False,'registration':False,'feathering':False,'pixelSynthesis':False,'formalAccepted':False},indent=2)+'\n',encoding='utf8')
print(str(q))

