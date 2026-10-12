from pathlib import Path
import sys,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import production as p
stem,tile,base,x,y=sys.argv[1:6];x=int(x);y=int(y)
assert tile in p.load(ROOT/'qa'/'expansion-east-worker-map.json')['assignedTiles']
assert 0<=x<=2842 and 0<=y<=2842
req=ROOT/'prompts'/f'{stem}.request.json';assert not req.exists()
source=ROOT/'qa'/f'{base}-candidate-4096.png'
guide=ROOT/'guides'/f'{stem}.native-repair-guide.png'
Image.open(source).crop((x,y,x+1254,y+1254)).save(guide)
r,c=int(tile[1:3]),int(tile[5:7]);gx=(c-1)*4096+x;gy=(r-1)*4096+y
co={'tile':tile,'kind':'local_native_repair','nativeGlobalBox':[gx,gy,gx+1254,gy+1254],'expectedNativeDimensions':[1254,1254],'baseLocalCrop':[x,y,x+1254,y+1254]}
p.dump(str(guide)+'.derivation.json',{'operation':'Exact 1:1 crop from native candidate; no resampling','source':p.metadata(source,'native same-coordinate candidate'),'sourceCrop':[x,y,x+1254,y+1254],'coordinates':co,'sha256':p.hashfile(guide)})
refs=[p.metadata(guide,'edit target: native candidate exact crop')]+[p.metadata(*ref) for ref in p.REFS]
p.dump(req,{'tool':'image_gen.imagegen','references':refs,'coordinates':co,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None})
p.dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
print(json.dumps({'stem':stem,'guide':str(guide),'coordinates':co}))
