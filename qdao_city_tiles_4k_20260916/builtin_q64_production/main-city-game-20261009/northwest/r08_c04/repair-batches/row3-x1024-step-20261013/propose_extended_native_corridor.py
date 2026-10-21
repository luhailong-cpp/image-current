from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,numpy as np
D=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
base=Image.open(D/'edit-target.png').convert('RGB');im=Image.open(D/'native.png').convert('RGB')
poly=[(0,930),(905,300),(980,355),(980,465),(0,1070)]
mask=Image.new('L',(1254,1254),0);ImageDraw.Draw(mask).polygon(poly,fill=255);mask.save(D/'selection-mask-v2.png')
trial=Image.composite(im,base,mask);trial.save(D/'roi-trial-v2.png')
boxes={'left':[0,900,160,1100],'right':[850,280,1030,485],'mid-upper':[300,575,600,775],'mid-lower':[520,540,820,765],'full-context':[0,270,1080,1110]}
for name,box in boxes.items():trial.crop(box).save(D/('v2-'+name+'.png'))
a=np.array(base);out=np.array(trial);s=np.array(im);m=np.array(mask);assert np.array_equal(out[m==0],a[m==0]);assert np.array_equal(out[m==255],s[m==255])
data=json.loads((D/'adoption-proposal.json').read_text());data.update(status='pending_visual_review',sameWorldNativeROI=list(mask.getbbox()),targetTileROI=[a+b for a,b in zip(mask.getbbox(),[397,1933,397,1933])],mask=str(D/'selection-mask-v2.png'),maskSha256=sha(D/'selection-mask-v2.png'),maskPolygonXY=poly,selectedPixelCount=int((m==255).sum()),trial=str(D/'roi-trial-v2.png'),trialSha256=sha(D/'roi-trial-v2.png'))
(D/'adoption-proposal-v2.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print({'selectedPixelCount':data['selectedPixelCount']})

