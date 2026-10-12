import sys,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
prefix=sys.argv[1]
images={t:Image.open(ROOT/'qa'/f'{prefix}-{t}-candidate-4096.png').convert('RGB') for t in ['r10_c03','r10_c04']}
def crop(box):
 o=Image.new('RGB',(box[2]-box[0],box[3]-box[1]))
 for t,x0 in [('r10_c03',8192),('r10_c04',12288)]:
  a=max(box[0],x0);b=max(box[1],36864);c=min(box[2],x0+4096);d=min(box[3],40960)
  if c>a and d>b:o.paste(images[t].crop((a-x0,b-36864,c-x0,d-36864)),(a-box[0],b-box[1]))
 return o
for n,(a,b) in enumerate([(37260,38460),(38360,39560),(39460,40660)],1):crop((11560,a,13014,b)).save(ROOT/'qa'/f'{prefix}-whole-part{n}-native100.png')
for label,y in [('upper-middle',38320),('middle-lower',39290)]:crop((11560,y-140,13014,y+260)).save(ROOT/'qa'/f'{prefix}-{label}-native100.png')
crop((11560,37260,13014,40660)).resize((727,1700),Image.Resampling.LANCZOS).save(ROOT/'qa'/f'{prefix}-whole-preview-QA-only.png')
print(prefix,'native views built')
