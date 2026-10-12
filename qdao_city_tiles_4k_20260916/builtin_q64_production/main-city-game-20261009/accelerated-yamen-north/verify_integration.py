import sys,json
from pathlib import Path
from PIL import Image
import numpy as np
import pipeline as p
d=p.read(sys.argv[1]);a=np.array(Image.open(d['before']).convert('RGB'));b=np.array(Image.open(d['after']).convert('RGB'));z=np.array(Image.open(d['expected']).convert('RGB'));m=np.array(Image.open(d['support']).convert('L'))>0
c=np.any(a!=b,2);y,x=np.where(c)
r={**d,'beforeSHA256':p.sha(d['before']),'afterSHA256':p.sha(d['after']),'pixelExactMatchToIntendedComposite':bool(np.array_equal(b,z)),'changedPixelCount':int(c.sum()),'changesOutsideRepairSupport':int((c&~m).sum()),'changedPixelBox':[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1] if len(x) else None,'outer160PixelStripsUnchanged':bool(np.array_equal(a[:160],b[:160]) and np.array_equal(a[-160:],b[-160:]) and np.array_equal(a[:,:160],b[:,:160]) and np.array_equal(a[:,-160:],b[:,-160:])),'formalAccepted':False}
p.put_json(Path(d['output']),r);print(json.dumps(r))
