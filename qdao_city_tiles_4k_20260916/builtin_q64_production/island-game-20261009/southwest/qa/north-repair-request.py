import sys,shutil,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import production as p
from PIL import Image
old,new=sys.argv[1:3]
assert old.startswith('r08_') and new.startswith('r08_')
assert not (ROOT/'prompts'/f'{new}.request.json').exists()
co=p.load(ROOT/'prompts'/f'{old}.coordinates.json')
source=ROOT/'native'/f'{old}.png'
guide=ROOT/'guides'/f'{new}.native-repair.png'
shutil.copy2(source,guide)
overlays=[]
for neighbor in sys.argv[3:]:
    nc=p.load(ROOT/'prompts'/f'{neighbor}.coordinates.json'); b=nc['nativeGlobalBox']; a=co['nativeGlobalBox']
    z=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
    assert z[0]<z[2] and z[1]<z[3]
    path=ROOT/'native'/f'{neighbor}.png'; crop=[z[0]-b[0],z[1]-b[1],z[2]-b[0],z[3]-b[1]]; dest=[z[0]-a[0],z[1]-a[1]]
    with Image.open(guide) as im: canvas=im.convert('RGB')
    with Image.open(path) as im: canvas.paste(im.crop(crop),dest)
    canvas.save(guide)
    overlays.append({**p.metadata(path,'corrected native neighbor exact-coordinate overlap'),'sourceCrop':crop,'destinationTopLeft':dest})
p.dump(str(guide)+'.derivation.json',{'operation':'Exact native source copy and optional same-coordinate neighbor crop/paste as repair guide; no pixel resampling','source':p.metadata(source,'native source to repair'),'overlays':overlays,'coordinates':co})
refs=[p.metadata(guide,'native image repair target')]+[p.metadata(*r) for r in p.REFS]
p.dump(ROOT/'prompts'/f'{new}.coordinates.json',co)
p.dump(ROOT/'prompts'/f'{new}.request.json',{'tool':'image_gen.imagegen','references':refs,'coordinates':co,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None})
print(json.dumps({'stem':new,'guide':str(guide),'refs':[x['path'] for x in refs]}))
