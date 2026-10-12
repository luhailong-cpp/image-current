import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012';base=ROOT/'r04_c05/candidate/r04_c05-pipeline-fixed-native-contexts-0e9a0c64dd52.png';im=Image.open(base).convert('RGB')
for tag,box in [('c05-wood-v1',[0,430,1254,1684]),('c05-floor-v1',[1450,1400,2704,2654]),('c05-plinth-v1',[1500,2730,2754,3984]),('c05-green-band-v1',[2842,2842,4096,4096])]:
 d=H/tag;d.mkdir(exist_ok=True);p.save_png(d/'edit-guide-native.png',im.crop(tuple(box)))
 p.put_json(d/'preparation.json',{'tile':'r04_c05','tileBox':box,'worldBox':[16384+box[0],12288+box[1],16384+box[2],12288+box[3]],'sourceCandidate':p.reference(base,'native baseline'),'pixels':[1254,1254],'operation':'Exact native crop without resize','adopted':False})
src=H/'lower-merged-v3/d4-derived.png';d=H/'d4-color-splice-v1';d.mkdir(exist_ok=True);p.save_png(d/'edit-guide-native.png',Image.open(src).crop((585,0,1839,1254)))
p.put_json(d/'preparation.json',{'tile':'r03_c05','tileBox':[2280,2380,3534,3634],'worldBox':[18664,10572,19918,11826],'guideSource':p.reference(src,'unadopted D4 native strip'),'pixels':[1254,1254],'operation':'Exact native crop without resize','adopted':False})
print('Prepared final native micro-repair guides')

