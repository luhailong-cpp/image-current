import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=Path(__file__).resolve().parent;OUT=HERE/'roof-row-merge-v1';OUT.mkdir(exist_ok=True)
basefile=ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-945fa7bcbb42.png';base=np.array(Image.open(basefile).convert('RGB'))[2400:3654,1695:4096]
a=np.array(Image.open(HERE/'roof-row01/raw-v1.png').convert('RGB'));b=np.array(Image.open(HERE/'roof-row02/raw-v1.png').convert('RGB'));gen=np.empty((1254,2401,3),np.uint8);gen[:,:1254]=a;gen[:,1147:]=b
seam=p.minimum_seam(a[430:830,1147:],b[430:830,:107]);seam=np.pad(seam,(430,424),mode='edge');yy,xx=np.indices((1254,2401));idx=np.ones((1254,2401),np.uint8);idx[:,1147:]=2
for y in range(1254):
 k=1147+seam[y];gen[y,1147:k]=a[y,1147:k];idx[y,1147:k]=1
top=p.minimum_seam(base[420:490].transpose(1,0,2),gen[420:490].transpose(1,0,2))+420
bottom=p.minimum_seam(base[785:840].transpose(1,0,2),gen[785:840].transpose(1,0,2))+785
def s(v,a,b):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
w=s(yy,top[None,:]-12,top[None,:]+12)*(1-s(yy,bottom[None,:]-12,bottom[None,:]+12))*s(xx,180,210)
# Preserve the already reviewed solid golden curl at identical coordinates.
gold=(base[:,:,0]>140)&(base[:,:,1]>85)&(base[:,:,2]<130)&(base[:,:,0]>base[:,:,2]*1.4)
w[gold]=0
alpha=np.rint(w*255).astype('uint8');out=((base.astype('uint32')*(255-alpha[...,None])+gen.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
p.save_png(OUT/'derived-strip.png',Image.fromarray(out));p.save_png(OUT/'alpha.png',Image.fromarray(alpha));p.save_png(OUT/'source-index.png',Image.fromarray(idx))
p.put_json(OUT/'derivation.json',{'baseFile':str(basefile),'baseSHA256':p.sha(basefile),'tileBox':[1695,2400,4096,3654],'sources':[p.reference(HERE/'roof-row01/raw-v1.png','source1,strip x0'),p.reference(HERE/'roof-row02/raw-v1.png','source2,strip x1147')],'sourceIndex':p.reference(OUT/'source-index.png','native source ID'),'alpha':p.reference(OUT/'alpha.png','native-coordinate alpha'),'topPath':top.tolist(),'bottomPath':bottom.tolist(),'formula':'(base*(255-alpha)+gen*alpha+127)//255; preserve original golden pixels via explicit color mask; 24px smoothstep return, no spatial filtering','resampled':False,'formalAccepted':False})
for i,(l,r) in enumerate([(130,950),(900,1650),(1600,2401)],1):
 p.save_png(OUT/f'qa-middle-{i}.png',Image.fromarray(out).crop((l,470,r,740)));p.save_png(OUT/f'qa-bottom-{i}.png',Image.fromarray(out).crop((l,730,r,910)))
p.save_png(OUT/'qa-source-join.png',Image.fromarray(out).crop((1030,420,1340,860)))
print(OUT)

