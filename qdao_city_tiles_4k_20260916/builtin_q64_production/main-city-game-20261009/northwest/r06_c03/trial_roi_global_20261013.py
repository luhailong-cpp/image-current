from pathlib import Path
import sys,json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent
name,version=sys.argv[1:3];r=list(map(int,sys.argv[3:]));d=T/'repair-batches'/name;q=d/'trials'/version;q.mkdir(parents=True,exist_ok=False)
a=json.loads((d/'derivation.json').read_text());b=a['tileCropLTRB'];xy=[r[0]+b[0],r[1]+b[1],r[2]+b[0],r[3]+b[1]]
im=Image.open(a['source']).convert('RGB');im.paste(Image.open(d/'native.png').crop(r),xy[:2]);im.save(q/'candidate.png')
boxes={'top':[max(0,xy[0]-80),max(0,xy[1]-80),min(4096,xy[2]+80),min(4096,xy[1]+80)],'bottom':[max(0,xy[0]-80),max(0,xy[3]-80),min(4096,xy[2]+80),min(4096,xy[3]+80)],'left':[max(0,xy[0]-80),max(0,xy[1]-80),min(4096,xy[0]+80),min(4096,xy[3]+80)],'right':[max(0,xy[2]-80),max(0,xy[1]-80),min(4096,xy[2]+80),min(4096,xy[3]+80)]}
for k,box in boxes.items():im.crop(box).save(q/(k+'.png'))
out=dict(source=str(d/'native.png'),sourceSha256=hashlib.sha256((d/'native.png').read_bytes()).hexdigest(),sourceROI=r,tileROI=xy,output=str(q/'candidate.png'),outputSha256=hashlib.sha256((q/'candidate.png').read_bytes()).hexdigest(),perimeters={k:dict(file=str(q/(k+'.png')),tileCropLTRB=box,sha256=hashlib.sha256((q/(k+'.png')).read_bytes()).hexdigest()) for k,box in boxes.items()},sourceResampled=False,sourceRecolored=False,binaryNativeSelection=True,formalAccepted=False)
(q/'manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
