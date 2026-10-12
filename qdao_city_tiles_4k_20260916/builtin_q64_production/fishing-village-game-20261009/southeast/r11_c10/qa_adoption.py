from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;S=T/'qa'/'adoption';S.mkdir(parents=True,exist_ok=True)
source=T/'r11_c10-candidate-4096.png';im=Image.open(source);origin=[36864,40960]
worlds={'G1':[37546,43885,38441,44515],'Q1':[37521,43043,38301,43723]}
out=[]
for key,b in worlds.items():
 x0,y0,x1,y1=[b[0]-origin[0],b[1]-origin[1],b[2]-origin[0],b[3]-origin[1]]
 boxes={'left':[x0-128,y0-128,x0+128,y1+128],'right':[x1-128,y0-128,x1+128,y1+128],'top':[x0-128,y0-128,x1+128,y0+128],'bottom':[x0-128,y1-128,x1+128,y1+128]}
 for side,box in boxes.items():
  p=S/(key+'-'+side+'.png');im.crop(box).save(p)
  d={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':str(source),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'crop':box,'operation':'unscaled native adoption boundary QA crop','resamplingApplied':False}
  p.with_suffix('.png.derivation.json').write_text(json.dumps(d,indent=2),encoding='utf-8');out.append(d)
(S/'manifest.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'count':len(out),'source':str(source)}))

