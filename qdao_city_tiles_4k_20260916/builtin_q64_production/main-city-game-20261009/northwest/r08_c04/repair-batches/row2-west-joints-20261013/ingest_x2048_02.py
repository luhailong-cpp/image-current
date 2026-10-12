from pathlib import Path
from PIL import Image
import json,hashlib,shutil,numpy as np
B=Path(__file__).resolve().parent;D=B/'joint-x2048-02';sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
host=Path(r'C:/Users/luyua/.codex/generated_images/01a13608-efaf-7310-8b30-7b4f9396f5ed/exec-9e3c341b-61e8-4290-8283-02b051a7ee9d.png');out=D/'native.png'
assert not out.exists();shutil.copyfile(host,out);assert sha(host)==sha(out)
im=Image.open(out).convert('RGB');base=Image.open(B/'joint-x2048-01/edit-target.png').convert('RGB');assert im.size==(1254,1254)
(D/'generation.json').write_text(json.dumps({'tool':'image_gen__imagegen','nativePath':str(out),'hostPath':str(host),'sha256':sha(out),'hostByteIdentical':True,'size':list(im.size),'actualModel':None,'actualQuality':None,'sourceWorldBox':[13709,29581,14963,30835],'fullOutputAdopted':False},indent=2),encoding='utf-8')
box=[475,255,813,552];trial=base.copy();trial.paste(im.crop(box),box[:2]);trial.save(D/'upper-trial.png');x0,y0,x1,y1=box
for tag,crop in [('detail',[x0-50,y0-40,x1+50,y1+40]),('north',[x0-25,y0-30,x1+25,y0+30]),('south',[x0-25,y1-30,x1+25,y1+30]),('west',[x0-30,y0-25,x0+30,y1+25]),('east',[x1-30,y0-25,x1+30,y1+25])]:trial.crop(crop).save(D/('upper-'+tag+'.png'))
mask=np.zeros((1254,1254),np.uint8);mask[y0:y1,x0:x1]=255;Image.fromarray(mask).save(D/'upper-selection-mask.png')
a=np.array(base);b=np.array(im);t=np.array(trial);assert np.array_equal(t[mask==0],a[mask==0]);assert np.array_equal(t[mask==255],b[mask==255])
(D/'upper-adoption-proposal.json').write_text(json.dumps({'status':'pending_visual_review','source':str(out),'sourceSha256':sha(out),'sourceWorldBox':[13709,29581,14963,30835],'sourceOriginInTile':[1421,909],'sameWorldNativeROI':box,'targetTileROI':[x0+1421,y0+909,x1+1421,y1+909],'mask':str(D/'upper-selection-mask.png'),'maskSha256':sha(D/'upper-selection-mask.png'),'maskMode':'L binary 0/255','selectedPixelCount':int((mask==255).sum()),'resampled':False,'blended':False,'outsideMaskPixelIdentical':True,'insideMaskNativePixelIdentical':True,'trial':str(D/'upper-trial.png'),'trialSha256':sha(D/'upper-trial.png'),'formalAccepted':False},indent=2),encoding='utf-8')
print({'sha':sha(out),'size':im.size})

