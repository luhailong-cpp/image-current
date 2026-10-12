import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=Q/'block2x2-r09r10c06c07-v1-context-native.png';im=Image.open(src).convert('RGB');refs=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
specs=[('lamp',[5740,3520,6994,4774],[420,330,740,1040]),('grout',[3650,3650,4904,4904],[240,300,1090,1050]),('notch',[7168,3600,8422,4854],[300,300,1150,1050])]
for rid,box,bounds in specs:
 p=Q/f'r10c07-joint-{rid}-source-v1-native.png';im.crop(box).save(p)
 save(Path(str(p)+'.derivation.json'),{'source':{'path':src.as_posix(),'sha256':sha(src)},'sourceBox':box,'operation':'integer crop only; no resampling','sha256':sha(p),'dimensions':[1254,1254]})
 stem=f'r10_c07_localrepair_joint_{rid}_v1'
 save(Z/f'native/{stem}.request.json',{'stem':stem,'tile':'r10_c07','patch':'localrepair_joint_'+rid,'coordinates':{'id':'joint_'+rid,'role':'localized native seam repair: four-block joint '+rid,'contextBox':box,'globalContextBox':[box[0]+20365,box[1]+32653,box[2]+20365,box[3]+32653],'expectedNativeDimensions':[1254,1254],'repairBounds':bounds,'margin':60},'references':[{'path':p.as_posix(),'role':'edit target: exact native crop from stable four-tile composition','sha256':sha(p),'dimensions':[1254,1254]}]+refs,'overlaps':[],'submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
 print(stem)
