import sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012'
a=np.array(Image.open(ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-945fa7bcbb42.png').convert('RGB'))
d=np.array(Image.open(H/'d1-merged-v1/derived-strip.png').convert('RGB'));m=np.array(Image.open(H/'d1-merged-v1/alpha.png'))>0
a[430:1684,:2354][m]=d[m]
# This is an unadopted guide, not a final candidate.
for tag,box in [('d1-right-return-v1',[1100,550,2354,1804])]:
 out=H/tag;out.mkdir(exist_ok=True)
 p.save_png(out/'edit-guide-native.png',Image.fromarray(a).crop(tuple(box)))
 p.put_json(out/'preparation.json',{'tile':'r03_c05','tileBox':box,'worldBox':[16384+box[0],8192+box[1],16384+box[2],8192+box[3]],'sourceCandidate':str(ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-945fa7bcbb42.png'),'guideDerivedStrip':str(H/'d1-merged-v1/derived-strip.png'),'guideOperation':'Copy trial pixels at identical native coordinate then crop, no resize','pixels':[1254,1254],'adopted':False})
west=np.array(Image.open(ROOT/'r03_c04/candidate/r03_c04-pipeline-fixed-native-contexts-424e41dd0ce0.png').convert('RGB'))[430:1684,3500:]
cross=np.concatenate([west,a[430:1684,:658]],axis=1)
out=H/'d1-west-join-v1';out.mkdir(exist_ok=True)
p.save_png(out/'edit-guide-native.png',Image.fromarray(cross))
p.put_json(out/'preparation.json',{'tile':'r03_c05','affectedTiles':['r03_c04','r03_c05'],'worldBox':[15788,8622,17042,9876],'tileBoxes':{'r03_c04':[3500,430,4096,1684],'r03_c05':[0,430,658,1684]},'pixels':[1254,1254],'guideOperation':'Same-coordinate neighboring candidate crop plus unadopted D1 trial. No resize','adopted':False})
p.put_json(H/'d1-merged-v1/visual-review.json',{'reviewedAllTenQACrops':True,'status':'needs_local_return_repairs','mainRoofPattern':'pass','leftRamp':'ghost near x0..90','sourceJoin':'notch near x1240 y860','bottomRightReturn':'several duplicate ridges y~860','adopted':False})
print('Prepared two exact native repair guides.')

