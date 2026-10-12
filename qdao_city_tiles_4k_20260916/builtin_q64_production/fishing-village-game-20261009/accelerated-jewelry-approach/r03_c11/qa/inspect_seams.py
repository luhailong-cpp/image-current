from pathlib import Path
from PIL import Image
import json, numpy as np
HERE=Path(__file__).resolve().parent
TILE=HERE.parent
ROOT=TILE.parent
candidate=TILE/'candidate/r03_c11-4096-candidate-v2.png'
if not candidate.exists(): candidate=TILE/'candidate/r03_c11-4096-candidate-v1.png'
im=Image.open(candidate).convert('RGB')
metrics=[]
for axis in ['vertical','horizontal']:
    for a in [1024,2048,3072]:
        sheet=Image.new('RGB',(1024,1024))
        for i in range(4):
            if axis=='vertical':
                crop=im.crop((a-128,i*1024,a+128,(i+1)*1024))
                sheet.paste(crop,(i*256,0))
                arr=np.asarray(crop).astype(float); dif=np.abs(np.diff(arr,axis=1)); boundary=dif[:,127,:]; local=dif[:,112:144,:]
            else:
                crop=im.crop((i*1024,a-128,(i+1)*1024,a+128))
                sheet.paste(crop,(0,i*256))
                arr=np.asarray(crop).astype(float); dif=np.abs(np.diff(arr,axis=0)); boundary=dif[127,:,:]; local=dif[112:144,:,:]
            metrics.append({'axis':axis,'coordinate':a,'segment':i,'meanAbsoluteBoundaryChannelDelta':round(float(boundary.mean()),3),'nearbyMeanDelta':round(float(local.mean()),3)})
        sheet.save(HERE/f'{axis}-{a}-contact-native.png')
west=Image.new('RGB',(4096,4096))
for r in range(1,5):
    for c in range(1,5):
        sel=json.loads((ROOT/'r03_c10/records'/f'p{r}{c}.selection.json').read_text(encoding='utf-8-sig'))
        west.paste(Image.open(sel['file']).crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
sheet=Image.new('RGB',(1024,1024))
for i in range(4):
    crop=Image.new('RGB',(256,1024))
    crop.paste(west.crop((3968,i*1024,4096,(i+1)*1024)),(0,0))
    crop.paste(im.crop((0,i*1024,128,(i+1)*1024)),(128,0))
    crop.save(HERE/f'west-external-y{i*1024}-native.png')
    sheet.paste(crop,(i*256,0))
sheet.save(HERE/'west-external-contact-native.png')
(HERE/'seam-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
print(json.dumps(metrics))
