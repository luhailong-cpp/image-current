"""Exact native crop/paste guide for AI seam reconstruction, no painting."""
from pathlib import Path
from PIL import Image
import hashlib,json
Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=Z/'native/r06_c12_p11-v2.png'
b=Z/'native/r06_c12_p12-v6.png'
i=Image.open(a).crop((512,0,1139,1254))
j=Image.open(b).crop((115,0,742,1254))
out=Image.new('RGB',(1254,1254))
out.paste(i,(0,0));out.paste(j,(627,0))
p=Z/'guides/r06_c12_p11-p12.bridge-edit-target.png'
out.save(p)
data={'file':str(p),'sha256':sha(p),'purpose':'AI edit target for native seam geometry repair; NOT accepted game art',
 'nativeGlobalBox':[45453,20365,46707,21619], 'pixels':[1254,1254], 'joinLocalX':627,
 'operations':'Native 1:1 crop/paste only, no resampling, drawing, feathering or blending',
 'derivedFrom':[{'path':str(a),'sha256':sha(a),'sourceBox':[512,0,1139,1254],'targetBox':[0,0,627,1254], 'generationRecord':str(a)+'.generation.json'},
 {'path':str(b),'sha256':sha(b),'sourceBox':[115,0,742,1254],'targetBox':[627,0,1254,1254], 'generationRecord':str(b)+'.generation.json'}]}
p.with_name(p.name+'.derived.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(p))
