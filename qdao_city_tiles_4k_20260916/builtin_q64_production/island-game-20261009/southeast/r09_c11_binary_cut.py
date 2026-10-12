from pathlib import Path
from PIL import Image
import numpy as np,importlib.util,json
from workflow import ROOT,sha,write
spec=importlib.util.spec_from_file_location('seam','D:/work/image/tianyong_festival_hd_20260910/seam_helpers.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
for name in ['r09_c11_seam-p23-p24_v02','r09_c11_seam-p43-p44_v02']:
 ap=ROOT/'guides'/f'{name}.native-seam-target.png';bp=ROOT/'native'/f'{name}.png';a=np.asarray(Image.open(ap).convert('RGB'));b=np.asarray(Image.open(bp).convert('RGB'))
 lc=mod._minimum_vertical_seam(a[:,115:512],b[:,115:512])+115
 rc=mod._minimum_vertical_seam(a[:,742:1200],b[:,742:1200])+742
 tc=mod._minimum_vertical_seam(a[:230].transpose(1,0,2),b[:230].transpose(1,0,2))
 bc=mod._minimum_vertical_seam(a[1024:].transpose(1,0,2),b[1024:].transpose(1,0,2))+1024
 yy,xx=np.indices((1254,1254));mask=(xx>=lc[:,None])&(xx<rc[:,None])&(yy>=tc[None,:])&(yy<bc[None,:])
 out=np.where(mask[:,:,None],b,a).astype('uint8');p=ROOT/'qa'/f'{name}.binary-native-cut.png';Image.fromarray(out).save(p)
 mp=ROOT/'qa'/f'{name}.binary-native-cut-mask.png';Image.fromarray(mask.astype('uint8')*255).save(mp)
 write(Path(str(p)+'.generation.json'),{'file':p.as_posix(),'sha256':sha(p),'operation':'binary native-pixel source selection along minimum RGB error paths; no feather, resample, warp or color matching','sources':[{'file':x.as_posix(),'sha256':sha(x)} for x in [ap,bp]],'mask':mp.as_posix(),'maskSha256':sha(mp),'paths':{'left':lc.tolist(),'right':rc.tolist(),'top':tc.tolist(),'bottom':bc.tolist()},'selectedRepairPixels':int(mask.sum())})
 print(p)

