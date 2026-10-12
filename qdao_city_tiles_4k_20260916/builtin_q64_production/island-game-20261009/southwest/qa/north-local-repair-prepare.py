from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
stem,tile,prefix=sys.argv[1:4];x,y=map(int,sys.argv[4:6]);box=[x,y,x+1254,y+1254]
art=ROOT/'qa'/(prefix+'-candidate-4096.png'); rep=ROOT/'qa'/(prefix+'-report.json');r=load(rep); b=r['candidateGlobalBox']
assert b[0]<=x and b[1]<=y and box[2]<=b[2] and box[3]<=b[3]
guide=ROOT/'guides'/(stem+'.native-repair.png');assert not (ROOT/'prompts'/(stem+'.request.json')).exists()
crop=[box[0]-b[0],box[1]-b[1],box[2]-b[0],box[3]-b[1]]
with Image.open(art) as im:cropped=im.crop(crop)
if guide.exists():
    with Image.open(guide) as old:assert old.size==cropped.size and old.tobytes()==cropped.tobytes()
else:cropped.save(guide)
co={'tile':tile,'kind':'localized native geometry seam repair','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254]}
dump(str(guide)+'.derivation.json',{'operation':'exact same-global-coordinate native crop; no resampling, painting or blending','source':metadata(art,'native candidate edit target'),'sourceReport':{'path':str(rep),'sha256':hashfile(rep),'role':'source-id/pixel trace report'},'sourceCrop':crop,'globalBox':box,'sha256':hashfile(guide)})
refs=[metadata(guide,'fixed native geometry repair target; preserve layout and outer continuity')]+[metadata(*v) for v in REFS]
dump(ROOT/'prompts'/(stem+'.coordinates.json'),co)
dump(ROOT/'prompts'/(stem+'.request.json'),{'tool':'image_gen.imagegen','coordinates':co,'references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None})
print(json.dumps({'stem':stem,'guide':str(guide),'box':box}))
