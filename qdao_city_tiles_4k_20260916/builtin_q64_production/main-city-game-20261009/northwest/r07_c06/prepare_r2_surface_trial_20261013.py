from pathlib import Path
from PIL import Image
import json
r=Path(__file__).resolve().parent;q=r/'qa/resume-r2c4-surface05-20261013';q.mkdir(exist_ok=False);c=Image.open(r/'candidate/r07_c06-candidate-native-roi-v05.png').convert('RGB');s=Image.open(r/'native/s02_04_surfacefix05.png').convert('RGB');c.paste(s.crop((115,115,1139,1139)),(3072,1024));c.save(q/'candidate.png')
for name,box in {'upper-corner':(2944,896,3392,1312),'west-band':(2944,1024,3392,2048),'lower-junction':(2880,1856,3392,2240),'north-edge':(3072,896,4096,1152),'south-edge':(3072,1920,4096,2176),'east-edge':(3968,1024,4096,2048)}.items():c.crop(box).save(q/(name+'.png'))
(q/'derivation.json').write_text(json.dumps(dict(base=str(r/'candidate/r07_c06-candidate-native-roi-v05.png'),newSource=str(r/'native/s02_04_surfacefix05.png'),sourceROI=[115,115,1139,1139],candidateROI=[3072,1024,4096,2048],trialOnly=True,noResample=True),indent=2),encoding='utf-8')
