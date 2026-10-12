from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;B=W.parent;S=W/'stage-bridge'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
p=S/'r05_c03.candidate.png';im=Image.open(p);ids=Image.open(S/'r05_c03.source-id.png')
box=[9000,18000,10254,19254];rel=[box[0]-8192,box[1]-16384,box[2]-8192,box[3]-16384]
g=W/'guides/cream-corner-whole-native.png';im.crop(rel).save(g);ids.crop(rel).save(W/'guides/cream-corner-whole-native.source-id.png')
write(str(g)+'.derivation.json',{'file':str(g),'sha256':sha(g),'globalNativeBox':box,'operation':'exact integer crop of native hardcut candidate; no resize','candidate':str(p),'candidateSha256':sha(p),'assembly':str(S/'assembly.json'),'sourceIdMap':str(W/'guides/cream-corner-whole-native.source-id.png'),'guidePixelsUsedInFinal':False})
n=Image.open(B/'delivery-2x2/stage-v3/r04_c03.png');band=Image.new('RGB',(4096,600));band.paste(n.crop((0,3796,4096,4096)),(0,0));band.paste(im.crop((0,0,4096,300)),(0,300));band.save(S/'qa/north-whole.100pct.png')
for j in range(4):band.crop((j*1024,0,(j+1)*1024,600)).save(S/f'qa/north-{j+1}.100pct.png')
print(json.dumps({'guide':str(g),'globalNativeBox':box}))
