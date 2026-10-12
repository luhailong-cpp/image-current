import json,hashlib
from pathlib import Path
from PIL import Image
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=z/'qa/full-tile-r09_c05-context-native.png'
asm=json.loads((z/'qa/full-tile-r09_c05-assembly.json').read_text())
assert sha(src)==asm['context']['sha256']
refs=json.loads((z/'references.json').read_text())
layout=Path(refs[0]['path'])
for rid,b,bounds,margin in [('darkpost',[2957,400,4211,1654],[480,450,910,830],60),('sand',[450,2957,1704,4211],[440,230,770,1240],60)]:
 stem='r09_c05_repair_'+rid+'_v1'
 source=z/'layout-only'/f'{stem}_source.png'
 guide=z/'layout-only'/f'{stem}_layout.png'
 cb=[v+115 for v in b]
 globalbox=[b[0]+16384,b[1]+32768,b[2]+16384,b[3]+32768]
 Image.open(src).crop(cb).save(source)
 write(str(source)+'.derivation.json',{'file':source.as_posix(),'sha256':sha(source),'role':'native integer repair edit target','source':{'path':src.as_posix(),'sha256':sha(src)},'sourceBox':cb,'tileCoreRelativeBox':b,'globalContextBox':globalbox,'operation':'native integer crop only','noResize':True})
 scaled=[v*1254/57344 for v in globalbox]
 Image.open(layout).transform((1254,1254),Image.Transform.EXTENT,scaled,resample=Image.Resampling.NEAREST).save(guide)
 write(str(guide)+'.derivation.json',{'file':guide.as_posix(),'sha256':sha(guide),'role':'layout-only enlarged coordinate crop, never final pixels','source':{'path':layout.as_posix(),'sha256':sha(layout)},'sourceBoxFloat':scaled,'globalContextBox':globalbox,'operation':'layout-only nearest coordinate crop enlargement'})
 ref=[{'path':source.as_posix(),'sha256':sha(source),'role':'edit target: exact native crop, preserve all geometry and outer ring'},{'path':guide.as_posix(),'sha256':sha(guide),'role':'same-coordinate layout guidance only; preserve target exact geometry'},*refs]
 for r in ref: assert sha(r['path'])==r['sha256']
 write(z/'native'/f'{stem}.request.json',{'stem':stem,'tile':'r09_c05','patch':'repair_'+rid,'coordinates':{'globalContextBox':globalbox,'tileContextBox':b,'sourceCoreBox':bounds,'role':'localized native seam repair; not one of the regular 16 grid patches'},'references':ref,'repairBounds':bounds,'margin':margin,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'sourceAssembly':{'path':(z/'qa/full-tile-r09_c05-assembly.json').as_posix(),'sha256':sha(z/'qa/full-tile-r09_c05-assembly.json')}})
 print(stem,sha(source))

