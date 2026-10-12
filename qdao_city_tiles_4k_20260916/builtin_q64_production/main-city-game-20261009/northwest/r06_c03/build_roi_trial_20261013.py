from pathlib import Path
import json,sys,hashlib
from PIL import Image
T=Path(__file__).resolve().parent
name=sys.argv[1];roi=list(map(int,sys.argv[2:]));d=T/'repair-batches'/name
a=json.loads((d/'derivation.json').read_text());im=Image.open(d/'edit-target.png').convert('RGB');im.paste(Image.open(d/'native.png').crop(roi),roi[:2]);im.save(d/'trial-roi.png')
boxes={'top':[max(0,roi[0]-80),max(0,roi[1]-80),min(1254,roi[2]+80),min(1254,roi[1]+80)],'bottom':[max(0,roi[0]-80),max(0,roi[3]-80),min(1254,roi[2]+80),min(1254,roi[3]+80)],'left':[max(0,roi[0]-80),max(0,roi[1]-80),min(1254,roi[0]+80),min(1254,roi[3]+80)],'right':[max(0,roi[2]-80),max(0,roi[1]-80),min(1254,roi[2]+80),min(1254,roi[3]+80)]}
for k,b in boxes.items():im.crop(b).save(d/('trial-'+k+'.png'))
out=dict(nativeSource=str(d/'native.png'),nativeSha256=hashlib.sha256((d/'native.png').read_bytes()).hexdigest(),sourceROI=roi,tileROI=[roi[0]+a['tileCropLTRB'][0],roi[1]+a['tileCropLTRB'][1],roi[2]+a['tileCropLTRB'][0],roi[3]+a['tileCropLTRB'][1]],trial=str(d/'trial-roi.png'),perimeterCrops={k:dict(file=str(d/('trial-'+k+'.png')),cropLTRB=b) for k,b in boxes.items()},sourceResampled=False,sourceRecolored=False,binaryNativeSelection=True,formalAccepted=False)
(d/'trial.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
