from pathlib import Path
import json
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
QA=ROOT/'qa'
RBOX=[11660,33940,12914,35194]

def patch(prefixes, crop_box):
    out=Image.new('RGB',(crop_box[2]-crop_box[0],crop_box[3]-crop_box[1]))
    for prefix in prefixes:
        report=json.loads((QA/(prefix+'-report.json')).read_text(encoding='utf-8'))
        box=report['candidateGlobalBox']
        clip=[max(crop_box[0],box[0]),max(crop_box[1],box[1]),min(crop_box[2],box[2]),min(crop_box[3],box[3])]
        if clip[0]<clip[2] and clip[1]<clip[3]:
            source=Image.open(QA/(prefix+'-candidate-4096.png'))
            out.paste(source.crop((clip[0]-box[0],clip[1]-box[1],clip[2]-box[0],clip[3]-box[1])),(clip[0]-crop_box[0],clip[1]-crop_box[1]))
    return out

before=['hardseam-v04','c04-hardseam-v01']
after=['multi-boundary-v02-r09_c03','multi-boundary-v02-r09_c04']
boxes={
  'bottom-panel-perimeter':[480,1100,1070,1320],
  'left-beam-perimeter':[-50,570,210,1060],
  'left-roof-perimeter':[-50,-50,180,550],
  'right-wall-perimeter':[1120,510,1310,1100],
  'former-v01-left-beam-defect':[270,490,510,940],
  'former-v01-bottom-panel-defect':[370,1000,820,1210],
}
for label,box in boxes.items():
    global_box=[box[j]+RBOX[j%2] for j in range(4)]
    a,b=patch(before,global_box),patch(after,global_box)
    pair=Image.new('RGB',(a.width*2,a.height))
    pair.paste(a,(0,0));pair.paste(b,(a.width,0))
    pair.save(QA/('multi-boundary-v02-independent-'+label+'-base-left-candidate-right-100pct.png'))
patch(after,RBOX).save(QA/'multi-boundary-v02-independent-candidate-patch-100pct.png')
print(json.dumps({'repairGlobalBox':RBOX,'nativeCrops':boxes,'resampling':False}))
