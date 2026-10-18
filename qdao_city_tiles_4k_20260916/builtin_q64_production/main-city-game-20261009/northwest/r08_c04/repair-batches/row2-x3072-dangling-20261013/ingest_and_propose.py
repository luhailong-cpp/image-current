from pathlib import Path
from PIL import Image
import hashlib,json,shutil,numpy as np
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/row2-x3072-dangling-20261013');sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
host=Path(r'C:/Users/luyua/.codex/generated_images/01a12075-f5cf-7c30-9edc-ceb79ed8cfbd/exec-c943c914-f9bb-453c-a0bb-3e9efaf881b1.png')
native=D/'native.png';assert not native.exists();shutil.copyfile(host,native);assert sha(host)==sha(native)
im=Image.open(native);assert im.size==(1254,1254) and ('A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255))
world=[14733,29581,15987,30835];origin=[2445,909]
(D/'generation.json').write_text(json.dumps({'tool':'image_gen__imagegen','hostPath':str(host),'nativePath':str(native),'sha256':sha(native),'hostByteIdentical':True,'size':list(im.size),'actualModel':None,'actualQuality':None,'sourceWorldBox':world,'fullOutputAdopted':False},indent=2),encoding='utf-8')
base=Image.open(D/'edit-target.png').convert('RGB');im=im.convert('RGB');roi=[485,620,735,825];x0,y0,x1,y1=roi
trial=base.copy();trial.paste(im.crop(roi),roi[:2]);trial.save(D/'roi-trial.png')
mask=np.zeros((1254,1254),np.uint8);mask[y0:y1,x0:x1]=255;Image.fromarray(mask).save(D/'selection-mask.png')
a=np.array(base);out=np.array(trial);s=np.array(im);assert np.array_equal(out[mask==0],a[mask==0]);assert np.array_equal(out[mask==255],s[mask==255])
for name,box in [('detail',[x0-50,y0-40,x1+50,y1+40]),('north',[x0-25,y0-30,x1+25,y0+30]),('south',[x0-25,y1-30,x1+25,y1+30]),('west',[x0-30,y0-25,x0+30,y1+25]),('east',[x1-30,y0-25,x1+30,y1+25])]:trial.crop(box).save(D/(name+'.png'))
(D/'adoption-proposal.json').write_text(json.dumps({'status':'pending_visual_review','source':str(native),'sourceSha256':sha(native),'sourceWorldBox':world,'sourceOriginInTile':origin,'sameWorldNativeROI':roi,'targetTileROI':[x0+origin[0],y0+origin[1],x1+origin[0],y1+origin[1]],'mask':str(D/'selection-mask.png'),'maskSha256':sha(D/'selection-mask.png'),'maskMode':'L binary 0/255','selectedPixelCount':int((mask==255).sum()),'resampled':False,'blended':False,'outsideMaskPixelIdentical':True,'insideMaskNativePixelIdentical':True,'trial':str(D/'roi-trial.png'),'trialSha256':sha(D/'roi-trial.png'),'formalAccepted':False},indent=2),encoding='utf-8')
print({'sourceSha256':sha(native),'selectedPixelCount':int((mask==255).sum())})

