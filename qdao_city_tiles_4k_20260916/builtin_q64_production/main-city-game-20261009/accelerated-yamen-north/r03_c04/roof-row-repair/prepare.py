from pathlib import Path
from PIL import Image
import json,hashlib
O=Path(__file__).resolve().parent;T=O.parent
S=T/'candidate/r03_c04-pipeline-minimum-error-5a45bea8726a-ccd4a3.png'
im=Image.open(S).convert('RGB')
assert im.size==(4096,4096)
items=[]
for name,box in [('left',[453,493,1707,1747]),('right',[1433,493,2687,1747])]:
 d=O/name;d.mkdir(exist_ok=True)
 c=im.crop(box);c.save(d/'context-native.png')
 items.append({'name':name,'contextTileBox':box,'contextWorldBox':[box[0]+12288,box[1]+8192,box[2]+12288,box[3]+8192],
 'source':str(S),'sourceSha256':hashlib.sha256(S.read_bytes()).hexdigest(),'guide':str(d/'context-native.png'),
 'guideSha256':hashlib.sha256((d/'context-native.png').read_bytes()).hexdigest(),'nativePixels':[1254,1254]})
(O/'preparation.json').write_text(json.dumps(items,indent=2)+'\n',encoding='utf-8')
print(json.dumps(items))
