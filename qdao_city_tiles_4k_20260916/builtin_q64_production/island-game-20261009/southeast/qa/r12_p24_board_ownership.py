from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from workflow import *
import numpy as np
from PIL import Image
a=ROOT/'native/r12_c12_p24_v01.png';b=ROOT/'native/r12_c12_p24_v02.png';aa=np.array(Image.open(a).convert('RGB'));bb=np.array(Image.open(b).convert('RGB'))
y,x=np.mgrid[:1254,:1254]
mask=y>1162-.24*x
out=np.where(mask[:,:,None],bb,aa).astype('uint8')
q=ROOT/'qa/r12-p24-board-ownership';q.mkdir(exist_ok=True)
Image.fromarray(out).save(q/'proposal.png');Image.fromarray(mask.astype('uint8')*255).save(q/'source-id.png')
Image.fromarray(out[750:1254]).save(q/'lower-100pct.png')
write(q/'proposal.json',{'operation':'binary original-source ownership of complete lower plank surface; native RGB unchanged, no rescale/blend/draw','sources':[{'id':0,'file':str(a),'sha256':sha(a)},{'id':1,'file':str(b),'sha256':sha(b)}],'sourceIdMap':str(q/'source-id.png'),'output':str(q/'proposal.png'),'nativeOffset':[0,0],'predicate':'y > 1162 - 0.24*x','sourceReplayMismatch':int(np.any(out != np.where(mask[:,:,None],bb,aa),axis=2).sum()),'status':'proposal_pending_review'})
print(q/'proposal.png')
