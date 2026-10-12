from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys
from PIL import Image
import numpy as np

v=Path(sys.argv[1]);source=Path(sys.argv[2])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
with Image.open(source) as im:
    assert im.format=='PNG' and im.size==(1254,1254)
native=v/'native.png';assert not native.exists();shutil.copyfile(source,native)
receipt={'status':'succeeded','tool':'image_gen.imagegen','originalOutput':str(source),'actualModel':None,'actualQuality':None,'savedAtUtc':datetime.now(timezone.utc).isoformat(),'actualDimensions':[1254,1254]}
write(v/'receipt.json',receipt)
write(v/'generation.json',{'status':'succeeded_pending_visual_QA','native':str(native),'sha256':sha(native),'originalOutput':str(source),'originalSha256':sha(source),'actualSize':[1254,1254],'actualModel':None,'actualQuality':None,'tool':'image_gen.imagegen','request':str(v/'request.json'),'requestSha256':sha(v/'request.json'),'preparation':str(v/'preparation.json'),'preparationSha256':sha(v/'preparation.json'),'receipt':str(v/'receipt.json'),'receiptSha256':sha(v/'receipt.json'),'resized':False,'formalAccepted':False})
measurements=[]
for p in [v/'target-native-1254.png',native]:
    a=np.array(Image.open(p).convert('RGB')).astype(float).mean(axis=2)
    rows=[]
    for x in [615,624,625,635,650,700,750,800,850,879]:
        center=int(410-(x-625)*0.617)
        vals=a[center-36:center+37,x-2:x+3].mean(axis=1)
        rows.append({'x':x,'darkJointCenterY':int(center-36+vals.argmin())})
    measurements.append({'file':str(p),'measurements':rows})
write(v/'joint-registration.json',{'method':'Approximate dark-grout centre, no acceptance decision','measurements':measurements})
print(json.dumps({'native':str(native),'sha256':sha(native),'registration':measurements}))
