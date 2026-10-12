import sys,json,hashlib
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent.parent;D=Z/'stair-rebuild'
stem=sys.argv[1];x,y=map(int,sys.argv[2:4]);bx=[x,y,x+1254,y+1254]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=Path(sys.argv[4]) if len(sys.argv)>4 else D/'full-tile-r10_c04-context-native.png';p=D/(stem+'-source.png')
Image.open(src).crop(tuple(v+115 for v in bx)).save(p)
refs=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
inputs=[{'path':p.as_posix(),'sha256':sha(p),'role':'exact native edit target, integer crop of current 4326 assembled context'},refs[1],refs[2]]
r={'stem':stem,'tile':'r10_c04','patch':stem,'coordinates':{'globalContextBox':[x+12288,y+36864,x+13542,y+38118],'tileContextBox':bx,'role':'localized native seam repair'},'references':inputs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'sourceContext':{'path':src.as_posix(),'sha256':sha(src)},'sourceCrop':{'contextBox':[v+115 for v in bx],'resampled':False},'preparedAtUtc':datetime.now(timezone.utc).isoformat()}
(D/(stem+'.request.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'stem':stem,'refs':[r['path'] for r in inputs]}))
