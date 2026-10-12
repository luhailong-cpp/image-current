from workflow import *
from PIL import Image
import numpy as np
q=ROOT/'qa/r12_c11-sol-20261012-upper-v03'
new=ROOT/'tiles/r12_c11.candidate-sol-20261012-v03.png';old=ROOT/'tiles/r12_c11.candidate-sol-20261012-v02.png';east=ROOT/'tiles/r12_c12.candidate-sol-20261012-v01.png'
a=np.array(Image.open(new).convert('RGB'));b=np.array(Image.open(old).convert('RGB'))
unchanged=[]
for direction in ['h','v']:
 for r in range(1,5 if direction=='h' else 4):
  for c in range(1,4 if direction=='h' else 5):
   box=[c*1024-256,(r-1)*1024,c*1024+256,r*1024] if direction=='h' else [(c-1)*1024,r*1024-256,c*1024,r*1024+256]
   x,y,x1,y1=box;assert np.array_equal(a[y:y1,x:x1],b[y:y1,x:x1]);unchanged.append(f'{direction}{r}{c}')
for r in range(1,4):
 for c in range(1,4):
  x=c*1024;y=r*1024;assert np.array_equal(a[y-256:y+256,x-256:x+256],b[y-256:y+256,x-256:x+256])
for e in read(q/'overlay-edges.json')['entries']:assert sha(Path(e['file']))==e['sha256']
p=read(q/'source-pixel-proof.json');assert p['replayMismatchedPixels']==0
im=Image.new('RGB',(512,1024));im.paste(Image.open(new).convert('RGB').crop((3840,3072,4096,4096)),(0,0));im.paste(Image.open(east).convert('RGB').crop((0,3072,256,4096)),(256,0));im.save(q/'actual-east4-root.png')
write(q/'root-changed-region-review.json',{'reviewedAtUtc':now(),'reviewer':'root','candidate':str(new),'candidateSha256':sha(new),'actualPixelVerifiedUnchangedInternalSeams':unchanged,'unchangedJunctionCount':9,'previousInternalReview':str(ROOT/'qa/r12_c11-sol-20261012-final-v02/left-visual-review.json'),'independentlyViewed':['top','left','right','whole'],'changedObjectOuterEdges':'pass','completeColumnLowerShaft':'pass','sourceReplayMismatch':0,'externalEast4':str(q/'actual-east4-root.png'),'externalEast4Status':'pending actual root visual inspection','externalSouth':'pending actual r13','formalAccepted':False})
print(json.dumps({'all24InternalSeamsAnd9JunctionsUnchanged':True,'candidateSha256':sha(new),'sourceMismatch':0}))

