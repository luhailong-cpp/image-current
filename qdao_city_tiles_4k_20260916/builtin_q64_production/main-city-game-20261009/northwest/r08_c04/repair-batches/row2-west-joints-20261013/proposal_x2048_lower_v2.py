from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent/'joint-x2048-01';sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
base=Image.open(D/'edit-target.png').convert('RGB');src=Image.open(D/'native.png').convert('RGB');a=np.array(base);b=np.array(src)
mask=np.zeros(a.shape[:2],dtype=np.uint8);mask[928:1102,566:684]=255
red=lambda q:(q[:,:,0]>q[:,:,1]*1.5)&(q[:,:,0]>q[:,:,2]*1.5)&(q[:,:,0]>95)
wood=red(a)|red(b);wood[:,580:]=False;mask[wood]=0
m=Image.fromarray(mask);m.save(D/'lower-selection-mask-v2.png');trial=Image.composite(src,base,m);trial.save(D/'lower-masked-trial-v2.png')
proof=np.array(trial);assert np.array_equal(proof[mask==0],a[mask==0]);assert np.array_equal(proof[mask==255],b[mask==255])
for tag,crop in [('detail',[516,888,734,1142]),('north',[541,898,709,958]),('south',[541,1072,709,1132]),('west',[536,903,596,1127]),('east',[654,903,714,1127])]:trial.crop(crop).save(D/('lower-masked-v2-'+tag+'.png'))
(D/'lower-adoption-proposal-v2.json').write_text(json.dumps({'status':'pending_final_masked_visual_review','source':str(D/'native.png'),'sourceSha256':sha(D/'native.png'),'sourceWorldBox':[13709,29581,14963,30835],'sourceOriginInTile':[1421,909],'sameWorldNativeROI':[566,928,684,1102],'targetTileROI':[1987,1837,2105,2011],'mask':str(D/'lower-selection-mask-v2.png'),'maskSha256':sha(D/'lower-selection-mask-v2.png'),'maskMode':'L binary 0/255','maskSemantics':'255 exact same-world native source pixel; 0 original pixel','redPostExcluded':True,'selectedPixelCount':int((mask==255).sum()),'resampled':False,'blended':False,'outsideMaskPixelIdentical':True,'insideMaskNativePixelIdentical':True,'trial':str(D/'lower-masked-trial-v2.png'),'trialSha256':sha(D/'lower-masked-trial-v2.png'),'formalAccepted':False},indent=2),encoding='utf-8')

