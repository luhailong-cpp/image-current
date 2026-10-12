import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012';O=H/'final-native-boundaries';O.mkdir(exist_ok=True)
tags={'r03_c04':'d9f811b3adb4','r03_c05':'9e876e7effe2','r04_c04':'2d815289e5cc','r04_c05':'4e4ac2a282d9'}
files={t:ROOT/t/'candidate'/f'{t}-pipeline-fixed-native-contexts-{v}.png' for t,v in tags.items()}
a={t:np.array(Image.open(f).convert('RGB')) for t,f in files.items()}
sm=p.read(H/'staged-final-v2/staging-manifest.json')
old={t:np.array(Image.open(r['file']).convert('RGB')) for t,r in sm['baseCandidates'].items()}
records=[]
for u,v,axis in [('r03_c04','r03_c05','x'),('r04_c04','r04_c05','x'),('r03_c04','r04_c04','y'),('r03_c05','r04_c05','y')]:
 for seg in range(4):
  st=seg*1024
  if axis=='x':
   pair=np.concatenate([a[u][st:st+1024,-160:],a[v][st:st+1024,:160]],axis=1)
   before=np.concatenate([old[u][st:st+1024,-160:],old[v][st:st+1024,:160]],axis=1)
   im=Image.fromarray(pair).transpose(Image.Transpose.ROTATE_90)
  else:
   pair=np.concatenate([a[u][-160:,st:st+1024],a[v][:160,st:st+1024]],axis=0)
   before=np.concatenate([old[u][-160:,st:st+1024],old[v][:160,st:st+1024]],axis=0)
   im=Image.fromarray(pair)
  f=O/f'{u}-{v}-segment{seg+1}.png';r=p.save_png(f,im)
  records.append(dict(r,leftOrNorthTile=u,rightOrSouthTile=v,axis=axis,segment=seg+1,changedFromBase=not np.array_equal(pair,before),nativePixelScale=1,actuallyViewed=False))
top=np.concatenate([a['r03_c04'][-160:,-160:],a['r03_c05'][-160:,:160]],axis=1);bot=np.concatenate([a['r04_c04'][:160,-160:],a['r04_c05'][:160,:160]],axis=1)
p.save_png(O/'fourway-native.png',Image.fromarray(np.concatenate([top,bot],axis=0)))
# Dynamic existence check of existing authorized boundary references.
outer=p.read(ROOT/'outer-neighbor-inventory.json');available=[];missing=[]
for edge in outer['edges']:
 for i,source in enumerate(edge['sources']):
  f=Path(source['file'])
  if not f.exists():missing.append({'tile':edge['tile'],'edge':edge['edge'],'neighbor':edge['neighbor'],'patch':source['patch'],'expectedFile':str(f)});continue
  if edge['edge']!='south':available.append({'edge':edge,'source':p.reference(f,'currently present neighbor raw')});continue
  tile=edge['tile'];seg=i;st=seg*1024;neighbor=np.array(Image.open(f).convert('RGB'))[115:275,115:1139]
  pair=np.concatenate([a[tile][-160:,st:st+1024],neighbor],axis=0)
  df=O/f'{tile}-{edge["neighbor"]}-segment{seg+1}.png';r=p.save_png(df,Image.fromarray(pair))
  available.append(dict(r,tile=tile,neighbor=edge['neighbor'],edge='south',segment=seg+1,neighborSource=p.reference(f,'old available neighbor core; not a fresh formal full-tile adoption'),nativePixelScale=1,actuallyViewed=False))
p.put_json(O/'boundary-index.json',{'sharedAssignedBoundarySegments':records,'fourway':str(O/'fourway-native.png'),'availableOuterBoundarySources':available,'missingOuterBoundarySegments':missing,'missingNeighborTiles':sorted(set(m['neighbor'] for m in missing)),'formalAccepted':False})
print('shared changed',[Path(r['file']).name for r in records if r['changedFromBase']]);print('outer',len(available),'missing',len(missing))

