from pathlib import Path
from PIL import Image
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT));import production as p
stem='r10_c04_s03_02_v03';reqpath=ROOT/'prompts'/(stem+'.request.json');req=p.load(reqpath)
guide=ROOT/'guides'/(stem+'.native-overlap-guide.png')
original=ROOT/'native'/'r10_c04_s03_02_v02.png'
with Image.open(original) as im:canvas=im.convert('RGB')
parts=[p.metadata(original,'native rejected candidate; preserve correct ground/gold material outside wall repair')]
box=req['coordinates']['nativeGlobalBox']
neighbors=([req['leftAtPreparation']] if req['leftAtPreparation'] else [])+[req['rightAtPreparation'],req['top']]
for n in neighbors:
 f=ROOT/'native'/(n+'.png');rec=p.load(str(f)+'.generation.json');nb=rec['coordinates']['nativeGlobalBox']
 ib=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
 crop=[ib[0]-nb[0],ib[1]-nb[1],ib[2]-nb[0],ib[3]-nb[1]];dest=[ib[0]-box[0],ib[1]-box[1]]
 with Image.open(f) as im:canvas.paste(im.crop(crop),dest)
 parts.append({**p.metadata(f,'same coordinate native constraint'),'sourceCrop':crop,'destinationTopLeft':dest})
canvas.save(guide)
p.dump(str(guide)+'.derivation.json',{'operation':'native same-coordinate crop/paste over rejected native base to pin actual accepted TOP and RIGHT; no resampling','sources':parts,'coordinates':req['coordinates'],'sha256':p.hashfile(guide)})
req['references'][0]=p.metadata(guide,'native repair guide; actual TOP and RIGHT pasted at same coordinates over v01; correct post foot and plinth height to RIGHT fixed source');req['repairOf']='r10_c04_s03_02_v02';p.dump(reqpath,req)
p.dump(ROOT/'qa'/'r10_c04_s03_02_v02-rejection.json',{'status':'rejected','reason':'TOP repaired; RIGHT post foot and ground-plinth outer edge end 60-75px lower than accepted right neighbor. Correct the whole foot and nearby ground plane before continuation.','nativeEvidence':'qa/r10_c04_s03_02_v02-right-column-top-native100.png'})
print('Repair guide references and rejection recorded')


