import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa';N=Z/'native'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
trace=Q/'block2x2-r10r11c06c07-v1-trace.json';t=json.loads(trace.read_text(encoding='utf-8'));box=[7168,3740,8422,4994]
p=Q/'r11_c07-north-rail-repair-v1-source-native.png';assert not p.exists()
with Image.open(t['context']['path']) as im:im.crop(box).save(p)
stem='r11_c07_north_rail_repair_v1'
refs=[{**ref(p),'role':'edit target: exact native crop; fix only railing that is sharply cut off at y586'}]
req={'stem':stem,'tile':'r11_c07','patch':'localized_north_rail_repair','coordinates':{'role':'localized native seam repair of railing across r10_c07/r11_c07','contextBoxInBlock':box,'globalContextBox':[27533,40489,28787,41743],'expectedNativeDimensions':[1254,1254]},'references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'baseTrace':ref(trace)}
(N/(stem+'.request.json')).write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(ref(p)))
