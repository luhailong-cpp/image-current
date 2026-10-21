import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'path':Path(p).as_posix(),'sha256':sha(p)}
def save(p,v):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=Z/'qa/full-tile-r11_c02-assembly.json'; t=json.loads(a.read_text())
affected=['v2048-part02','h1024-part03','intersection-x2048-y1024']
audit={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'stair_continue','tile':'r11_c02','status':'repair_required','trace':ref(a),'candidate':t['output'],'context':t['context'],'nativeQaViewedCount':39,'viewed':[{'file':q['file'],'sha256':q['sha256'],'result':'repair_required' if any(s in q['file'] for s in affected) else 'pass'} for q in t['qa']],'findings':[{'id':'lantern_suspension','description':'Round red lantern near tile x1940,y1100 has a block cap but no visible rope or bracket attaching it to the tree; add a physically connected short suspension without moving the lantern.','coreBox':[1810,580,2070,1040],'status':'repair_required'}],'unresolved':['lantern_suspension'],'formalAcceptedCount':0}
save(Z/'qa/r11_c02-internal-native-art-audit-v1.json',audit)
box=[1320,370,2574,1624]; src=Z/'qa/r11_c02-lantern-suspension-v1-source-native.png'
assert not src.exists()
Image.open(t['output']['path']).crop(box).save(src)
save(Path(str(src)+'.derivation.json'),{'source':t['output'],'sourceBox':box,'operation':'integer crop only','file':ref(src),'nativePixelsResampled':False})
stem='r11_c02_lantern_suspension_v1'; refs=[{'path':src.as_posix(),'role':'exact native local edit target','sha256':sha(src)}]
shared=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'));refs+=shared[1:]
req={'stem':stem,'tile':'r11_c02','patch':'local_lantern_suspension','coordinates':{'role':'localized native seam repair: lantern suspension','globalContextBox':[5416,41330,6670,42584],'tileCoreBox':box,'expectedNativeDimensions':[1254,1254]},'references':refs,'submittedParameters':{'model':None,'quality':None,'transparent_background':False}}
save(Z/'native'/(stem+'.request.json'),req)
preview=Z/'qa/r11_c02-composition-preview-v1.png';im=Image.open(t['output']['path']);im.resize((1400,1400),Image.Resampling.LANCZOS).save(preview)
save(Path(str(preview)+'.derivation.json'),{'role':'inspection preview only, never native output','operation':'downscale for composition inspection','source':t['output'],'file':ref(preview)})
print(json.dumps({'source':ref(src),'audit':ref(Z/'qa/r11_c02-internal-native-art-audit-v1.json'),'refs':[r['path'] for r in refs],'preview':preview.as_posix()}))

