from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
STEM='r09_r10_c03_package_join_v01'
BOX=[8192,36280,9446,37534]
CONTRACT=json.loads((ROOT.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def meta(p,role):
    with Image.open(p) as im:dim=list(im.size)
    return {'path':Path(p).as_posix(),'sha256':sha(p),'dimensions':dim,'role':role}
above=ROOT/'output'/'r09_c03-native-candidate-v05.png'
parts=[(above,[0,3512,1254,4096],[0,0],[8192,36280,9446,36864]),
       (ROOT/'native'/'r10_c03_s01_01_v02.png',[115,115,1139,785],[0,584],[8192,36864,9216,37534]),
       (ROOT/'native'/'r10_c03_s01_02_v01.png',[115,115,345,785],[1024,584],[9216,36864,9446,37534])]
guide=ROOT/'guides'/(STEM+'.native-guide.png')
context=ROOT/'guides'/(STEM+'.above-context.png')
assert not guide.exists() and not context.exists()
canvas=Image.new('RGB',(1254,1254))
records=[]
for path,crop,dest,global_box in parts:
    with Image.open(path) as im: canvas.paste(im.crop(crop),dest)
    records.append({**meta(path,'native same-coordinate guide contribution'),'sourceCrop':crop,'destinationTopLeft':dest,'globalIntersection':global_box})
canvas.save(guide)
with Image.open(above) as im:im.crop((0,2842,1254,4096)).save(context)
write(str(guide)+'.derivation.json',{'operation':'same-coordinate integer crop/paste only; no resampling, feathering or colour adjustment','globalBox':BOX,'derivedFrom':records,'sha256':sha(guide),'finalArt':False})
write(str(context)+'.derivation.json',{'operation':'native integer crop for above context only','source':meta(above,'actual r09_c03 final v05'),'sourceCrop':[0,2842,1254,4096],'globalBox':[8192,35610,9446,36864],'sha256':sha(context)})
coords={'tile':'r10_c03','kind':'cross-tile native package and rope continuity repair','nativeGlobalBox':BOX,'tileLocalCrop':[0,-584,1254,670],'expectedNativeDimensions':[1254,1254],'repairLocalMandatoryTarget':[0,554,670,654],'targetGlobalBox':[8192,36834,8862,36934],'seamGlobalY':36864,'seamRepairY':584,'proposedRepairRoi':[0,200,950,1060],'leftEdgeCroppedObject':True,'leftmostExternalNeighborPending':'r10_c02'}
write(ROOT/'prompts'/(STEM+'.coordinates.json'),coords)
refs=[meta(guide,'exact 1254 native edit target; repair discontinuity, preserve global geometry'),meta(context,'native actual upper-tile package context only; no layout substitution'),meta(CONTRACT['layoutReference'],'sole approved full-map layout reference'),meta(CONTRACT['detailStyleReference'],'independent material/style reference, NOT coordinate crop'),meta(CONTRACT['primaryStyleReference'],'primary approved Daoist Q painterly style; no UI/night/characters transfer')]
write(ROOT/'prompts'/(STEM+'.request.json'),{'tool':'image_gen.imagegen','createdAtUtc':datetime.now(timezone.utc).isoformat(),'references':refs,'guideDerivation':str(guide)+'.derivation.json','submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
print(json.dumps({'stem':STEM,'guide':guide.as_posix(),'context':context.as_posix(),'references':[x['path'] for x in refs],'coordinates':coords}))
