from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from PIL import Image
T=Path(__file__).resolve().parent
D=T/'qa/restart-saved-integration-20261013'
D.mkdir(parents=True,exist_ok=True)
def ref(f): return {'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
def save(im,f):
    assert not f.exists(),str(f)
    im.save(f)
micro=T/'repair-batches/shared-west-micro-01'
base=Image.open(micro/'edit-target.png').convert('RGB')
n=Image.open(micro/'native.png').convert('RGB')
trial=base.copy()
rois=[[617,382,639,408],[617,1077,639,1103]]
for b in rois: trial.paste(n.crop(b),b[:2])
save(trial,D/'micro-trial-native-1254.png')
qa=[]
for y in [395,1090]:
    box=[577,y-60,677,y+60]
    for kind,im in [('before',base),('after',trial)]:
        f=D/f'micro-y{y}-{kind}-context.png';save(im.crop(box),f);qa.append({**ref(f),'nativeCropLTRB':box,'nativePixelScale':1})
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':ref(micro/'native.png'),'generation':ref(micro/'generation.json'),'base':ref(micro/'edit-target.png'),'trial':ref(D/'micro-trial-native-1254.png'),'sourceROIs':rois,'nativeWorldBox':[19853,26776,21107,28030],'r07_c06TileOriginXY':[-627,2200],'r07_c05TileOriginXY':[3469,2200],'qa':qa,'pureNativeSelection':True,'sourceResampled':False,'blended':False,'recolored':False,'formalAccepted':False}
(D/'micro-trial.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
G=T/'repair-batches/c3c4-upper-gap-02'
before=Image.open(G/'edit-target.png').crop((495,450,765,750));save(before,D/'c3c4-before-context.png')
print(json.dumps(record,ensure_ascii=False))
