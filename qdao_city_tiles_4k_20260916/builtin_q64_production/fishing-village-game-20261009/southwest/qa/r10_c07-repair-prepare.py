import sys
sys.dont_write_bytecode = True
from pathlib import Path
from PIL import Image
import json, hashlib
Z = Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, data):
    with p.open('x', encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)
source=Z/'qa/full-tile-r10_c07-context-native.png'
base=Image.open(source).convert('RGB')
refs=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
specs=[('curb',[650,2500,1904,3754],[240,170,850,1050]),('wood',[2842,1550,4096,2804],[90,270,1210,930])]
for rid, box, bounds in specs:
    dst=Z/f'qa/repair-r10_c07-{rid}-source-native.png'
    cb=[v+115 for v in box]
    if not dst.exists():
        base.crop(cb).save(dst)
        write(Path(str(dst)+'.derivation.json'),{'operation':'integer native crop, no resampling','source':{'path':source.as_posix(),'sha256':sha(source)},'sourceBox':cb,'tileContextBox':box,'size':[1254,1254],'sha256':sha(dst)})
    stem=f'r10_c07_localrepair_{rid}_v1'
    req=Z/f'native/{stem}.request.json'
    if not req.exists(): write(req,{'stem':stem,'tile':'r10_c07','patch':'localrepair_'+rid,'coordinates':{'id':'localrepair_'+rid,'role':'localized native seam repair: '+rid,'globalContextBox':[box[0]+24576,box[1]+36864,box[2]+24576,box[3]+36864],'tileContextBox':box,'expectedNativeDimensions':[1254,1254],'repairBounds':bounds,'margin':60},'references':[{'path':dst.as_posix(),'role':'edit target: exact native crop from stable assembled r10_c07','sha256':sha(dst),'dimensions':[1254,1254]}]+refs,'overlaps':[],'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
    print(req.as_posix())
