from pathlib import Path
import sys
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012';S=H/'lower-merged-v1'
strip=Image.open(S/'d4-derived.png').convert('RGB')
for tag,x,box in [('d4-left-return-v1',0,[1695,2380,2949,3634]),('d4-right-return-v1',1147,[2842,2380,4096,3634])]:
 d=H/tag;d.mkdir(exist_ok=True);p.save_png(d/'edit-guide-native.png',strip.crop((x,0,x+1254,1254)))
 p.put_json(d/'preparation.json',{'tile':'r03_c05','tileBox':box,'worldBox':[16384+box[0],8192+box[1],16384+box[2],8192+box[3]],'guideSource':p.reference(S/'d4-derived.png','unadopted D4 native strip'),'pixels':[1254,1254],'operation':'Exact native crop of trial, no resize','adopted':False})
print('Prepared D4 return guides')

