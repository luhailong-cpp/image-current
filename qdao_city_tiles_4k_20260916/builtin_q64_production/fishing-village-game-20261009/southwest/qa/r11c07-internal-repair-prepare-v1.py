import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parents[1];Q=Z/'qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=Q/'full-tile-r11_c07-assembly.json';d=json.loads(a.read_text());src=Path(d['context']['path']);im=Image.open(src).convert('RGB');refs=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
specs=[('post',[2460,1430,3714,2684],[505,380,825,960]),('sand',[400,2500,1654,3754],[330,360,790,880])]
for rid,tb,bounds in specs:
 cb=[v+115 for v in tb];p=Q/f'r11c07-internal-{rid}-source-v1-native.png';im.crop(cb).save(p)
 save(Path(str(p)+'.derivation.json'),{'source':{'path':src.as_posix(),'sha256':sha(src)},'sourceBox':cb,'tileContextBox':tb,'operation':'integer crop only','sha256':sha(p),'dimensions':[1254,1254]})
 stem=f'r11_c07_localrepair_{rid}_v1';save(Z/f'native/{stem}.request.json',{'stem':stem,'tile':'r11_c07','patch':'localrepair_'+rid,'coordinates':{'id':'localrepair_'+rid,'role':'localized native seam repair: internal '+rid,'tileContextBox':tb,'contextBox':cb,'globalContextBox':[tb[0]+24576,tb[1]+40960,tb[2]+24576,tb[3]+40960],'expectedNativeDimensions':[1254,1254],'repairBounds':bounds,'margin':60},'references':[{'path':p.as_posix(),'sha256':sha(p),'role':'edit target native crop from stable internal assembly'}]+refs,'overlaps':[],'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
print('prepared two native1254 internal repair sources')

