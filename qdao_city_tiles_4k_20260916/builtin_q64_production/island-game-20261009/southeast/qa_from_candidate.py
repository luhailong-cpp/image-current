from PIL import Image
from pathlib import Path
import sys
from workflow import ROOT,read,write,sha,now
spec=read(Path(sys.argv[1]));tid=spec['tile'];revision=sys.argv[2];src=ROOT/'tiles'/f'{tid}.candidate-{revision}.png';im=Image.open(src).convert('RGB');folder=ROOT/'qa'/f'{tid}-{revision}';folder.mkdir(exist_ok=True);entries=[]
for r in range(1,5):
 cuts=[1024,2048,3072]
 for s in spec.get('seamShifts',[]):
  if s['subrow']==r:cuts[s['afterSubcolumn']-1]+=s['deltaPixels']
 for c,x in enumerate(cuts,1):
  box=[x-256,(r-1)*1024,x+256,r*1024];name=f'h{r}{c}';out=folder/f'{name}.png';im.crop(box).save(out);entries.append({'id':name,'direction':'horizontal','sourceCrop':box,'file':str(out),'sha256':sha(out),'status':'pending_visual_review'})
for r in range(1,4):
 for c in range(1,5):
  box=[(c-1)*1024,r*1024-256,c*1024,r*1024+256];name=f'v{r}{c}';out=folder/f'{name}.png';im.crop(box).save(out);entries.append({'id':name,'direction':'vertical','sourceCrop':box,'file':str(out),'sha256':sha(out),'status':'pending_visual_review'})
write(folder/'seams.json',{'createdAt':now(),'candidate':str(src),'candidateSha256':sha(src),'operation':'exact original-pixel seam crops from assembled candidate, no resampling','seamCount':len(entries),'entries':entries,'formalAccepted':False})
print(str(folder/'seams.json'))

