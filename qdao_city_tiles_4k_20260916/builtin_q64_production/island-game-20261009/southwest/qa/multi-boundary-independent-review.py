from pathlib import Path
import json
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT/'qa'
RBOX = [11660,33940,12914,35194]

def patch(prefixes):
    out = Image.new('RGB',(1254,1254))
    for prefix in prefixes:
        report=json.loads((QA/(prefix+'-report.json')).read_text(encoding='utf-8'))
        box=report['candidateGlobalBox']
        clip=[max(RBOX[0],box[0]),max(RBOX[1],box[1]),min(RBOX[2],box[2]),min(RBOX[3],box[3])]
        if clip[0]<clip[2] and clip[1]<clip[3]:
            source=Image.open(QA/(prefix+'-candidate-4096.png'))
            out.paste(source.crop((clip[0]-box[0],clip[1]-box[1],clip[2]-box[0],clip[3]-box[1])),(clip[0]-RBOX[0],clip[1]-RBOX[1]))
    return out

before=patch(['hardseam-v04','c04-hardseam-v01'])
after=patch(['multi-boundary-v01-r09_c03','multi-boundary-v01-r09_c04'])
boxes={
    'target-rectangle':[540,790,860,1050],
    'roof-and-upper-beam':[480,130,800,700],
    'left-wood-beam-transition':[270,490,510,940],
    'bottom-door-transition':[370,1000,820,1210],
    'right-corner-transition':[820,300,1050,950],
}
for label,box in boxes.items():
    a,b=before.crop(box),after.crop(box)
    pair=Image.new('RGB',(a.width*2,a.height))
    pair.paste(a,(0,0));pair.paste(b,(a.width,0))
    pair.save(QA/('multi-boundary-independent-'+label+'-base-left-candidate-right-100pct.png'))
after.save(QA/'multi-boundary-independent-candidate-patch-100pct.png')
print(json.dumps({'repairGlobalBox':RBOX,'nativeCrops':boxes,'resampling':False}))
