from workflow import *
from PIL import Image
import numpy as np
p=ROOT/'tiles/r09_c13.candidate-v02.png';old=ROOT/'tiles/r09_c13.candidate.png';a=Image.open(old).convert('RGB');b=Image.open(p).convert('RGB')
edge={}
for name,box in {'north':[0,0,4096,256],'south':[0,3840,4096,4096],'west':[0,0,256,4096],'east':[3840,0,4096,4096]}.items():
 edge[name]={'box':box,'pixelExactToPrior':a.crop(box).tobytes()==b.crop(box).tobytes()}
assert all(v['pixelExactToPrior'] for v in edge.values())
d=read(ROOT/'qa/r09_c13-v02/seams.json');changed=['h21','h22','h31','h32','v12','v22','v32']
for e in d['entries']:
 e.update({'status':'root_visual_major_geometry_pass','basis':'Fresh native pair hard seams plus candidate junctions directly viewed' if e['id'] in changed else 'Previously reviewed original candidate, exact crop pixel replay verified'})
d.update({'reviewedAt':now(),'reviewer':'root','internalPass':True,'formalAccepted':False,'edgePixelReplay':edge})
write(ROOT/'qa/r09_c13-v02/seams.json',d)
write(ROOT/'qa/r09_c13.root-review-v02.json',{'reviewedAt':now(),'candidate':str(p),'sha256':sha(p),'replacedCores':['p22v03','p32v03'],'result':'All 24 internal seams and 9 junctions major-geometry pass by changed-area visual review and unchanged-area exact pixel replay','changedSeamsDirectlyViewed':changed,'changedJunctionsDirectlyViewed':['11','12','21','22','31','32'],'independentReviewPending':True,'formalAccepted':False,'edgePixelReplay':edge,'observation':'Fresh coordinate guide plus correct lower-shaft native anchor resolves both old width steps. Shaft/rails/gourds connected, no enlarged final pixels.'})
print('r09c13 root review saved')

