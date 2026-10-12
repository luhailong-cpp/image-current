import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
here=Path(__file__).resolve().parent
f=ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-e28885c9de32.png'
for name,box in [('roof-fragments01',[300,1440,1554,2694]),('roof-fragments02',[1200,1440,2454,2694])]:
 d=here/name;d.mkdir(exist_ok=True);p.save_png(d/'context-native.png',Image.open(f).crop(box));p.put_json(d/'preparation.json',{'tile':'r03_c05','sourceCandidate':str(f),'sourceSHA256':p.sha(f),'tileBox':box,'worldBox':[16384+box[0],8192+box[1],16384+box[2],8192+box[3]],'nativePixels':[1254,1254],'resized':False,'defect':'D2 jagged mismatched native stitching between wood underlay and teal roof around tile y2048'})
print('prepared2')

