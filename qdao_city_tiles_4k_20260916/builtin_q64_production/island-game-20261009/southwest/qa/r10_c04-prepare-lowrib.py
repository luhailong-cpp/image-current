import sys,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT));import production as p
stem='r10_c04_lowrib_col12_join_v01';box=[12750,39706,14004,40960]
base=ROOT/'qa/c04-hardseam-r10c04-v01-candidate-4096.png'
gp=ROOT/'guides'/f'{stem}.native-guide.png'
Image.open(base).crop((462,2842,1716,4096)).save(gp)
co={'tile':'r10_c04','kind':'localized_native_repair','nativeGlobalBox':box,'expectedNativeDimensions':[1254,1254],'repairLocalROI':[300,850,1000,1254],'repairLocalMandatoryTarget':[430,1050,750,1254]}
refs=[p.metadata(gp,'native candidate crop and edit target'),p.metadata(ROOT/'native/r10_c04_s04_02_v02.png','RIGHT roof rib geometry context')]+[p.metadata(*r) for r in p.REFS]
p.dump(str(gp)+'.derivation.json',{'operation':'native 1:1 crop, no resizing','source':p.metadata(base,'base candidate'),'sourceCrop':[462,2842,1716,4096],'sha256':p.hashfile(gp)})
p.dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
req={'tool':'image_gen.imagegen','route':'builtin','references':refs,'coordinates':co,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None}
p.dump(ROOT/'prompts'/f'{stem}.request.json',req);print(json.dumps(req))

