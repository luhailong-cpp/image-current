import json,hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent
source=R/'qa/full-tile-r09_c04-context-native.png'
assembly=R/'qa/full-tile-r09_c04-assembly.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shared=json.loads((R/'references.json').read_text())
with Image.open(source) as im:
 for name,box,bounds,margin in [('post',[2400,1450,3654,2704],[450,400,950,850],100),('lantern',[2957,2400,4211,3654],[760,450,1160,900],80)]:
  stem='r09_c04_repair_'+name+'_v1'
  sourcebox=[v+115 for v in box]
  path=R/'layout-only'/f'{stem}_source.png'
  im.crop(sourcebox).save(path)
  globalbox=[12288+box[0],32768+box[1],12288+box[2],32768+box[3]]
  deriv={'role':'native integer-crop repair target, no enlargement','source':{'path':source.as_posix(),'sha256':sha(source)},'sourceAssembly':{'path':assembly.as_posix(),'sha256':sha(assembly)},'sourceBox':sourcebox,'tileContextBox':box,'globalContextBox':globalbox,'dimensions':[1254,1254],'sha256':sha(path)}
  Path(str(path)+'.derivation.json').write_text(json.dumps(deriv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  req={'tile':'r09_c04','patch':'repair_'+name,'coordinates':{'globalContextBox':globalbox,'tileContextBox':box,'sourceCoreBox':bounds,'role':'localized native seam repair; not one of the regular 16 grid patches'},'references':[{'path':path.as_posix(),'role':'exact native crop to locally repair seam; preserve geometry'},*shared],'repairBounds':bounds,'margin':margin}
  (R/'native'/f'{stem}.request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(json.dumps({'stem':stem,'source':str(path),'box':box,'globalBox':globalbox}))
