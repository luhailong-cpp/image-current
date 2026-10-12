import json,sys
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]));import pipeline as p
base=HERE.parent/'candidate/r04_c04-pipeline-minimum-error-774db18be885-bd8f13.png'
box=[1500,475,2754,1729]
info=p.save_png(HERE/'context-native.png',Image.open(base).crop(box))
p.put_json(HERE/'preparation.json',{'baseCandidate':str(base),'baseCandidateSHA256':p.sha(base),'contextTileBox':box,'contextWorldBox':[13788,12763,15042,14017],**info,'nativeScale':1,'target':'Gold shaft hard paint cutoff at tile y1097, x2088..2136'})
