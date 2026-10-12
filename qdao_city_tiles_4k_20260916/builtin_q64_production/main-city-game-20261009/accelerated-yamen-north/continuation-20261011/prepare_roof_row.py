import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=Path(__file__).resolve().parent;f=ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-945fa7bcbb42.png'
for name,box in [('roof-row01',[1695,2400,2949,3654]),('roof-row02',[2842,2400,4096,3654])]:
 d=HERE/name;d.mkdir(exist_ok=True);p.save_png(d/'context-native.png',Image.open(f).crop(box));p.put_json(d/'preparation.json',{'tile':'r03_c05','sourceCandidate':str(f),'sourceSHA256':p.sha(f),'tileBox':box,'nativePixels':[1254,1254],'defect':'D4 interrupted roof rows around tile y2960'})
print('prepared2')

