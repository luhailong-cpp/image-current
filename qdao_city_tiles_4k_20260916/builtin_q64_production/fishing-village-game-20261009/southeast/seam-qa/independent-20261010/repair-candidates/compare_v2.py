import json,hashlib
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=HERE/'east-deck-v2-input-100pct.png';new=HERE/'east-deck-joint-v2.png'
before=Image.open(old).convert('RGB');repair=Image.open(new).convert('RGB')
assert before.size==repair.size==(1254,1254)
qa=before.copy();qa.paste(repair.crop((115,115,1139,1139)),(115,115))
out=HERE/'v2-adoption-preview';out.mkdir(exist_ok=True)
qa.save(out/'central-1024-adoption-preview.png')
boxes={'left':[0,0,230,1254],'right':[1024,0,1254,1254],'top':[0,0,1254,230],'bottom':[0,1024,1254,1254]}
records=[]
for name,b in boxes.items():
 p=out/(name+'.png');qa.crop(b).save(p);records.append({'edge':name,'file':str(p),'sha256':sha(p),'sourceCrop':b,'seamInCrop':115})
(out/'manifest.json').write_text(json.dumps({'classification':'QA only, never adopted','input':str(old),'inputSha256':sha(old),'repair':str(new),'repairSha256':sha(new),'globalBox':[32200,37888,33454,39142],'proposedNativeAdoption':[115,115,1139,1139],'operation':'exact integer paste for perimeter inspection only; no scaling, blending, blur or source modification','records':records},indent=2)+'\n')
print(str(out))
