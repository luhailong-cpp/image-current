from pathlib import Path
from PIL import Image
import json,hashlib,shutil
B=Path(__file__).resolve().parent;D=B/'joint-x1024-02'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
host=Path(r'C:/Users/luyua/.codex/generated_images/01a13608-efaf-7310-8b30-7b4f9396f5ed/exec-76d8967b-7509-43a6-bbd0-5d318bc8de14.png');out=D/'native.png'
assert not out.exists();shutil.copyfile(host,out);assert sha(host)==sha(out)
im=Image.open(out).convert('RGB');base=Image.open(B/'joint-x1024-01/edit-target.png').convert('RGB');assert im.size==(1254,1254)
(D/'generation.json').write_text(json.dumps({'tool':'image_gen__imagegen','nativePath':str(out),'hostPath':str(host),'sha256':sha(out),'hostByteIdentical':True,'size':list(im.size),'actualModel':None,'actualQuality':None,'sourceWorldBox':[12685,29581,13939,30835],'fullOutputAdopted':False},indent=2),encoding='utf-8')
rois=[('upper',[612,398,663,452]),('lower',[612,790,663,846])]
for name,box in rois:
 trial=base.copy();trial.paste(im.crop(box),box[:2]);trial.save(D/(name+'-trial.png'))
 x0,y0,x1,y1=box
 for tag,crop in [('detail',[x0-70,y0-65,x1+70,y1+65]),('north',[x0-30,y0-35,x1+30,y0+35]),('south',[x0-30,y1-35,x1+30,y1+35]),('west',[x0-35,y0-30,x0+35,y1+30]),('east',[x1-35,y0-30,x1+35,y1+30])]:
  trial.crop(crop).save(D/(name+'-'+tag+'.png'))
(D/'roi-trial-only.json').write_text(json.dumps(rois,indent=2))
print({'sha':sha(out),'size':im.size})

