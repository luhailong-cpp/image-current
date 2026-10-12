from workflow import *
from PIL import Image
import numpy as np
q=ROOT/'qa/r12_c13-resume-sol-20261012';report=read(q/'candidate-v02-seam-review.json')
f=ROOT/'tiles/r12_c13.candidate-sol-20261012-v02.png';im=Image.open(f).convert('RGB')
results=[]
for e in report.get('internalSeams',[])+report.get('junctions',[]):
 box=e.get('box') or e.get('sourceCrop');file=Path(e['file'])
 if not box:results.append({'id':e['id'],'error':'no box'});continue
 a=np.array(im.crop(box));b=np.array(Image.open(file).convert('RGB'))
 results.append({'id':e['id'],'box':box,'samePixels':bool(a.shape==b.shape and np.array_equal(a,b)),'file':str(file)})
for name,box in [('v31',(768,2048,1280,3072)),('v21',(768,1024,1280,2048)),('v43',(2816,3072,3328,4096))]:im.crop(box).save(q/f'root-actual-v02-{name}.png')
write(q/'root-qa-identity-audit.json',{'candidate':str(f),'candidateSha256':sha(f),'reportCandidate':report.get('candidate'),'reportSha':report.get('candidateSha256'),'results':results})
print(json.dumps({'reportKeys':list(report),'candidateSha256':sha(f),'total':len(results),'mismatch':sum(not r.get('samePixels',False) for r in results),'results':results[:5]}))
