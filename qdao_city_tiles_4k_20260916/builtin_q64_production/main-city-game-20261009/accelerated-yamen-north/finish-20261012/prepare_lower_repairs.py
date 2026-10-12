from pathlib import Path
import sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012';base=ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-945fa7bcbb42.png'
im=Image.open(base).convert('RGB')
for tag,box in [('d4-left-v1',[1695,2380,2949,3634]),('d4-right-v1',[2842,2380,4096,3634]),('d5-gold-joint-v1',[400,2550,1654,3804]),('e1-west-v1',None),('e2-west-v1',None)]:
 d=H/tag;d.mkdir(exist_ok=True)
 if box:
  p.save_png(d/'edit-guide-native.png',im.crop(tuple(box)))
  p.put_json(d/'preparation.json',{'tile':'r03_c05','tileBox':box,'worldBox':[16384+box[0],8192+box[1],16384+box[2],8192+box[3]],'sourceCandidate':p.reference(base,'native baseline'),'pixels':[1254,1254],'operation':'Exact native crop, no resize'})
 else:
  import numpy as np
  y=1740 if tag.startswith('e1') else 2842
  west=Image.open(ROOT/'r03_c04/candidate/r03_c04-pipeline-fixed-native-contexts-424e41dd0ce0.png').convert('RGB')
  a=np.concatenate([np.array(west)[y:y+1254,3469:],np.array(im)[y:y+1254,:627]],axis=1)
  p.save_png(d/'edit-guide-native.png',Image.fromarray(a))
  p.put_json(d/'preparation.json',{'tile':'r03_c05','affectedTiles':['r03_c04','r03_c05'],'worldBox':[15757,8192+y,17011,8192+y+1254],'tileBoxes':{'r03_c04':[3469,y,4096,y+1254],'r03_c05':[0,y,627,y+1254]},'pixels':[1254,1254],'operation':'Exact native neighboring crop, no resize'})
print('Prepared D4, D5, E1, E2 guides.')

