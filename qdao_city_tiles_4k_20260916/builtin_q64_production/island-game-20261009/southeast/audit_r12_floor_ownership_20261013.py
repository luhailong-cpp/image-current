from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;Q=R/'qa/r12_c13-floor-ownership-20261013';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bp=R/'tiles/r12_c13.candidate-sol-20261012-v02.png';fp=R/'native/r12_c13_floor_end_joint_whole_v01.png';b=Image.open(bp).convert('RGB');f=Image.open(fp).convert('RGB');old=b.crop((397,1421,1651,2675));oa=np.asarray(old);fa=np.asarray(f)
profiles=[]
for x in [115,400,500,550,575,600,627,650,700,800,1000,1138]:
 profiles.append({'nativeX':x,'oldDarkYs':np.where(oa[580:1100,x].astype(int).sum(1)<100)[0].astype(int).tolist(),'newDarkYs':np.where(fa[580:1100,x].astype(int).sum(1)<100)[0].astype(int).tolist()})
for p in profiles:
 p['oldDarkYs']=[v+580 for v in p['oldDarkYs']];p['newDarkYs']=[v+580 for v in p['newDarkYs']]
write(Q/'registered-profile-audit.json',{'old':{'file':str(bp),'sha256':sha(bp),'crop':[397,1421,1651,2675]},'repair':{'file':str(fp),'sha256':sha(fp),'origin':[397,1421]},'profiles':profiles})
print(json.dumps(profiles))
# QA-only binary source ownership trial. RGB pixels copied unchanged from native originals.
mask=Image.new('L',(1254,1254));draw=ImageDraw.Draw(mask)
poly=[(540,650),(1139,650),(1139,1010),(710,1010),(690,943),(565,710),(540,680)]
draw.polygon(poly,fill=255);out=old.copy();out.paste(f,(0,0),mask);out.save(Q/'trial-physical-joint-source-cut-v01.png');mask.save(Q/'trial-physical-joint-source-cut-v01.mask.png')
write(Q/'trial-physical-joint-source-cut-v01.json',{'trialOnly':True,'notAdopted':True,'sourceRepair':str(fp),'sourceSha256':sha(fp),'tileOrigin':[397,1421],'resampled':False,'RGBModified':False,'blended':False,'binaryPolygonNativeCoordinates':poly,'maskSha256':sha(Q/'trial-physical-joint-source-cut-v01.mask.png')})
out.crop((480,620,850,1040)).save(Q/'trial-physical-joint-source-cut-v01-joint.png')
