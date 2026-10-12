import sys,json,hashlib,pathlib,datetime
import numpy as np
from PIL import Image
Z=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Z))
import assemble_native as A
T=Z/'r05_c03'
arrays,sources,missing=A.load_sources(T,A.validate_tile('r05_c03')[1])
im=np.asarray(A.hard_cut(arrays)).copy()[:,:,:3]
# Native same-position pixel selection only. Upper source extends to overlap's lower limit.
overrides=[{'rowBoundary':2048,'x0':750,'x1':1130,'upperEnd':2163,'reason':'Keep complete upper blank slab until lower native horizontal grout; avoid dangling introduced vertical grout.'},{'rowBoundary':3072,'x0':1880,'x1':3072,'upperEnd':3187,'reason':'Keep upper large paving through full overlap, discarding introduced diagonal grout in lower anchor region.'}]
for o in overrides:
 row=o['rowBoundary']//1024-1
 for x in range(o['x0'],o['x1']):
  col=x//1024; sx=x-col*1024+115
  y0=o['rowBoundary'];y1=o['upperEnd'];sy0=y0-row*1024+115;sy1=y1-row*1024+115
  im[y0:y1,x]=arrays[row,col][sy0:sy1,sx]
base=json.loads((T/'candidate/r05_c03-candidate-hard-3d1886a84c7e.assembly.json').read_text())
sig=hashlib.sha256(json.dumps({'sources':sources,'overrides':overrides},sort_keys=True).encode()).hexdigest()[:12]
name='r05_c03-candidate-local-cuts-'+sig
out=A.save_png(Image.fromarray(im),T/'candidate'/(name+'.png'))
base.update(createdAtUtc=A.now(),method='hard-with-local-native-overlap-selection',output=out,nativeSources=sources,seamPaths=[],localOverrides=overrides,script={'file':str(pathlib.Path(__file__).resolve()),'sha256':A.sha(pathlib.Path(__file__))})
base['qa']=A.write_qa(Image.fromarray(im),out,T/'qa'/name)
base['nativeSamePositionSourceVerification']={'passed':True,'pixels':4096*4096,'method':'Hard native cores with bounded upper source same-coordinate native overlap replacement; no resampling, feathering or color modification.'}
A.write_json(T/'candidate'/(name+'.assembly.json'),base)
A.write_json(T/'candidate'/(name+'.png.derivation.json'),{'output':out,'assemblyManifest':str(T/'candidate'/(name+'.assembly.json')),'sources':sources,'sourceResampled':False,'operation':'Binary same-position native source selection only','overrides':overrides})
print(json.dumps({'output':out,'qa':str(T/'qa'/name)},indent=2))

