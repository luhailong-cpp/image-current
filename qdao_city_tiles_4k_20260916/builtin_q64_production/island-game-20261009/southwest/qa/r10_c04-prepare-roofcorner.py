import sys,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT));import production as p
stem='r10_c04_finial_roofcorner_join_v01';box=[12600,39300,13854,40554]
base=ROOT/'qa/c04-int-lowrib-v01-r10_c04-candidate-4096.png'
gp=ROOT/'guides'/f'{stem}.native-guide.png'
Image.open(base).crop((312,2436,1566,3690)).save(gp)
co={'tile':'r10_c04','kind':'localized_native_repair','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254],'repairLocalROI':[350,420,1000,1030],'repairLocalMandatoryTarget':[500,550,790,850]}
refs=[p.metadata(gp,'native current integrated candidate edit target'),p.metadata(ROOT/'native/r10_c04_s04_02_v02.png','RIGHT eave and cylindrical roof course geometry context')]+[p.metadata(*r) for r in p.REFS]
p.dump(str(gp)+'.derivation.json',{'operation':'native 1:1 crop, no resizing','source':p.metadata(base,'current base candidate'),'sourceCrop':[312,2436,1566,3690],'sha256':p.hashfile(gp)})
p.dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
req={'tool':'image_gen.imagegen','route':'builtin','references':refs,'coordinates':co,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None}
p.dump(ROOT/'prompts'/f'{stem}.request.json',req);print(json.dumps(req))

