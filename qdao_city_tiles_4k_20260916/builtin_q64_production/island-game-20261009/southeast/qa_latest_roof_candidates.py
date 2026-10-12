from workflow import *
from PIL import Image
import subprocess,sys
specs=[('r09_c11','v02',[]),('r09_c12','v06',[{'subrow':4,'afterSubcolumn':2,'deltaPixels':-115}])]
for tid,rev,shifts in specs:
 spec=ROOT/f'qa-spec-{tid}.json';write(spec,{'tile':tid,'seamShifts':shifts});subprocess.run([sys.executable,str(ROOT/'qa_from_candidate.py'),str(spec),rev],check=True)
 base=ROOT/'tiles'/('r09_c11.candidate.png' if tid=='r09_c11' else 'r09_c12.candidate-v02.png');out=ROOT/'tiles'/f'{tid}.candidate-{rev}.png';a=Image.open(base).convert('RGB');b=Image.open(out).convert('RGB');d=read(ROOT/'qa'/f'{tid}-{rev}'/'seams.json');changed=[];replay=[]
 for p in d['entries']:
  equal=a.crop(p['sourceCrop']).tobytes()==b.crop(p['sourceCrop']).tobytes();replay.append({'id':p['id'],'unchanged':equal})
  if not equal:changed.append(p['id'])
 for r in range(1,4):
  for c in range(1,4):
   box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256];q=ROOT/'qa'/f'{tid}.junction_{r}{c}-{rev}.png';b.crop(box).save(q)
 b.resize((1024,1024),Image.Resampling.LANCZOS).save(ROOT/'qa'/f'{tid}.preview-{rev}.png')
 write(ROOT/'qa'/f'{tid}-{rev}'/'prior-reviewed-pixel-replay.json',{'base':str(base),'baseSha256':sha(base),'candidate':str(out),'candidateSha256':sha(out),'entries':replay,'changedSeams':changed})
 print(tid,changed)

