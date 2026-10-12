from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
old=Z/'guides/r07_c13-westfascia-A2.native-target.png';new=Z/'native/r07_c13-westfascia-A2-v1.png'
a,b=Image.open(old),Image.open(new);out=b.copy();bands=[(0,0,1254,170),(0,1084,1254,1254),(0,0,170,1254),(1084,0,1254,1254)]
for box in bands:out.paste(a.crop(box),box)
p=Z/'guides/r07_c13-westfascia-A3.native-target.png';out.save(p)
r={**ref(p),'nativeGlobalBox':[48525,25900,49779,27154],'nativeSize':[1254,1254],'operation':'Native A2-v1 interior plus exact original170px four outer anchor bands; crop/paste only, no paint/resize','sources':[ref(old),ref(new)],'originalBorderCropBoxes':bands}
Path(str(p)+'.derived.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({**r,'provenanceRecord':ref(Path(str(p)+'.derived.json'))}))
