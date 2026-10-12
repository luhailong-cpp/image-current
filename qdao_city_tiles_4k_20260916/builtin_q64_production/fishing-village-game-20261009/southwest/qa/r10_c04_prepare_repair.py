import json,hashlib,sys
from pathlib import Path
from PIL import Image
Z=Path(__file__).resolve().parents[1]
tag=sys.argv[1]
boxes={'stair_upper':[1472,400,2726,1654],'stair_lower':[1472,1424,2726,2678]}
b=boxes[tag]
source=Z/'qa'/('repair-r10_c04-upper-v1-candidate-4096.png' if tag=='stair_lower' else 'preflight-r10_c04-v1-candidate-4096.png')
stem='r10_c04_'+tag+'_v1'
native=Z/'layout-only'/f'{stem}_native-target.png'
Image.open(source).crop(b).save(native)
refs=json.loads((Z/'references.json').read_text(encoding='utf8'))
gb=[b[0]+12288,b[1]+36864,b[2]+12288,b[3]+36864]
guide=Z/'layout-only'/f'{stem}_layout.png'
Image.open(refs[0]['path']).transform((1254,1254),Image.Transform.EXTENT,[v*1254/57344 for v in gb],resample=Image.Resampling.NEAREST).save(guide)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p,role,src,op in [(native,'native integer crop for localized seam repair',source,{'integerCropBox':b,'resampling':False}),(guide,'layout-only enlarged crop, never final pixels',refs[0]['path'],{'sourceBoxFloat':[v*1254/57344 for v in gb],'resampling':'nearest layout-only'})]:
 Path(str(p)+'.derivation.json').write_text(json.dumps({'file':p.as_posix(),'sha256':sha(p),'role':role,'derivedFrom':[{'path':str(src),'sha256':sha(src)}],'operation':op},indent=2)+'\n',encoding='utf8')
coords={'role':'localized native seam repair: '+tag,'globalContextBox':gb,'globalCoreBox':[gb[0]+115,gb[1]+115,gb[2]-115,gb[3]-115],'tileLocalContextBox':b,'sourceCoreBox':[115,115,1139,1139],'expectedNativeDimensions':[1254,1254]}
req={'stem':stem,'tile':'r10_c04','patch':tag,'coordinates':coords,'references':[],'submittedParameters':{'model':None,'quality':None,'transparent_background':False}}
(Z/'native'/f'{stem}.request.json').write_text(json.dumps(req,indent=2)+'\n',encoding='utf8')
print(json.dumps({'stem':stem,'target':native.as_posix(),'guide':guide.as_posix(),'coordinates':coords}))
