import sys
sys.dont_write_bytecode=True
import json,hashlib,subprocess
from pathlib import Path
from PIL import Image
Z=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def save(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=Z/'qa/full-tile-r11_c02-assembly.json';t=json.loads(a.read_text())
m={'schemaVersion':1,'outputPrefix':'repair-r11_c02-internal-v1','baseAssembly':ref(a),'expectedBaseCandidateSha256':t['output']['sha256'],'repairs':[{'id':'lantern-suspension','tileContextBox':[1320,370,2574,1624],'contextBox':[1435,485,2689,1739],'repairBounds':[475,265,770,730],'margin':55,'source':ref(Z/'qa/r11_c02-lantern-suspension-v1-source-native.png'),'repair':ref(Z/'native/r11_c02_lantern_suspension_v1.png'),'generationRecord':ref(Z/'native/r11_c02_lantern_suspension_v1.png.generation.json')}]}
mp=Z/'qa/repair-r11_c02-internal-v1.manifest.json';save(mp,m)
subprocess.run([sys.executable,'-B',str(Z/'qa/repair-compose.py'),'--manifest',str(mp)],check=True)
rt=json.loads((Z/'qa/repair-r11_c02-internal-v1-trace.json').read_text())
out=Z/'qa/repair-r11_c02-internal-v1-lantern-after-100pct.png'
Image.open(rt['candidate']['path']).crop([1320,370,2574,1624]).save(out)
save(Path(str(out)+'.derivation.json'),{'file':ref(out),'source':rt['candidate'],'sourceBox':[1320,370,2574,1624],'operation':'integer crop only','nativePixelsResampled':False})
print(json.dumps({'after':ref(out)}))

