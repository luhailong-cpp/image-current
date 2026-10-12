"""Prepare exact-coordinate repair target from existing partial native assembly; no drawing."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *

stem,tile,prefix,x0,y0=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5])
assert tile in {f'r{r:02}_c{c:02}' for r in range(11,15) for c in [3,4]}
assert not (ROOT/'prompts'/f'{stem}.request.json').exists()
report_path=ROOT/'qa'/f'{prefix}-report.json';report=load(report_path)
assert report['tile']==tile and report['exactSourcePixels'] and report['mismatchedPixels']==0
src=Path(report['art']);assert hashfile(src)==report['sha256']
box=[x0,y0,x0+1254,y0+1254];basebox=report['candidateGlobalBox']
assert box[0]>=basebox[0] and box[1]>=basebox[1] and box[2]<=basebox[2] and box[3]<=basebox[3]
crop=[box[0]-basebox[0],box[1]-basebox[1],box[2]-basebox[0],box[3]-basebox[1]]
guide=ROOT/'guides'/f'{stem}.native-repair.png'
with Image.open(src) as im:im.crop(crop).save(guide)
co={'tile':tile,'kind':'localized native geometry repair from exact partial assembly','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254]}
dump(str(guide)+'.derivation.json',{'operation':'same-global-coordinate exact1254 crop; no native resampling or drawing','source':metadata(src,'native partial assembly'),'sourceReport':{'path':str(report_path),'sha256':hashfile(report_path)},'sourceCrop':crop,'nativeGlobalBox':box,'sha256':hashfile(guide)})
dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
refs=[metadata(guide,'fixed-coordinate native repair target; correct only specified seam geometry, preserve remaining architecture')]+[metadata(*r) for r in REFS]
dump(ROOT/'prompts'/f'{stem}.request.json',{'tool':'image_gen.imagegen','references':refs,'coordinates':co,'submitted':False,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None})
print(json.dumps({'stem':stem,'guide':str(guide),'coordinates':co,'references':[r['path'] for r in refs]},ensure_ascii=False))
