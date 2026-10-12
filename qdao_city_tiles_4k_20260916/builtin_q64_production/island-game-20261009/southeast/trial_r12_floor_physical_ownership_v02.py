from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;Q=R/'qa/r12_c13-floor-ownership-20261013'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
bp=R/'tiles/r12_c13.candidate-sol-20261012-v02.png';fp=R/'native/r12_c13_floor_end_joint_whole_v01.png';b=Image.open(bp).convert('RGB');f=Image.open(fp).convert('RGB');old=b.crop((397,1421,1651,2675));fa=np.asarray(f);oa=np.asarray(old);dark=fa.astype(int).sum(2)<110
mask=np.zeros((1254,1254),dtype=np.uint8);bounds=[]
for x in range(571,1140):
 up=int(round(863-0.26*x));lo=int(round(1151-.277*x))
 a=np.where(dark[max(0,up-12):up+13,x])[0]+max(0,up-12);c=np.where(dark[lo-12:lo+13,x])[0]+lo-12
 if len(a):up=int(a.min())
 if len(c):lo=int(c.max())
 for y in range(up,lo+1):
  # The left source cut lies inside the actual diagonal black end joint.
  jt=575+(y-716)*.498
  if y<711 or x>=max(571,jt-3):mask[y,x]=255
 bounds.append([x,up,lo])
out=oa.copy();out[mask!=0]=fa[mask!=0];im=Image.fromarray(out);im.save(Q/'trial-physical-joint-source-cut-v02.png');Image.fromarray(mask).save(Q/'trial-physical-joint-source-cut-v02.mask.png');im.crop((480,620,850,1040)).save(Q/'trial-physical-joint-source-cut-v02-joint.png')
(Q/'trial-physical-joint-source-cut-v02.json').write_text(json.dumps({'trialOnly':True,'notAdopted':True,'sources':[{'file':str(bp),'sha256':sha(bp),'crop':[397,1421,1651,2675]},{'file':str(fp),'sha256':sha(fp),'tileOrigin':[397,1421]}],'ownership':'binary source assignment only; new right-hand complete plank between native original black upper/lower gaps and diagonal end joint','resampled':False,'blended':False,'RGBModified':False,'maskSha256':sha(Q/'trial-physical-joint-source-cut-v02.mask.png'),'newPixels':int(np.count_nonzero(mask)),'columnBounds':bounds},indent=2),encoding='utf-8')
print(json.dumps({'newPixels':int(np.count_nonzero(mask)),'file':str(Q/'trial-physical-joint-source-cut-v02.png')}))
