import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012';O=H/'d1-merged-v2';O.mkdir(exist_ok=True)
def smooth(v,l,r):
 t=np.clip((v-l)/(r-l),0,1);return t*t*(3-2*t)
def repair(name,region,fade):
 d=H/name;base=np.array(Image.open(d/'edit-guide-native.png').convert('RGB'));gen=np.array(Image.open(d/'raw-native.png').convert('RGB'))
 y,x=np.indices((1254,1254));l,t,r,b=region
 w=smooth(x,l,l+fade)*(1-smooth(x,r-fade,r))*smooth(y,t,t+fade)*(1-smooth(y,b-fade,b))
 protect=(base[:,:,0]>base[:,:,2]*1.28)&(base[:,:,0]>75);w[protect]=0
 alpha=np.rint(w*255).astype('uint8')
 derived=((base.astype('uint32')*(255-alpha[...,None])+gen.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
 p.save_png(O/(name+'-derived.png'),Image.fromarray(derived));p.save_png(O/(name+'-alpha.png'),Image.fromarray(alpha))
 p.put_json(O/(name+'-derivation.json'),{'base':p.reference(d/'edit-guide-native.png','unadopted exact native guide'),'generated':p.reference(d/'raw-native.png','builtin native edit'),'alpha':p.reference(O/(name+'-alpha.png'),'recorded local material alpha'),'region':region,'fade':fade,'formula':'smoothstep fades inside specified rectangle; existing gold/wood protected. (base*(255-alpha)+generated*alpha+127)//255','resampled':False,'spatialBlur':False})
 return derived,alpha
ret,rm=repair('d1-right-return-v1',[50,620,1205,960],20)
west,wm=repair('d1-west-join-v1',[465,330,745,710],16)
a=np.array(Image.open(ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-945fa7bcbb42.png').convert('RGB'));b=np.array(Image.open(ROOT/'r03_c04/candidate/r03_c04-pipeline-fixed-native-contexts-424e41dd0ce0.png').convert('RGB'));ma=np.zeros((4096,4096),bool);mb=ma.copy()
strip=np.array(Image.open(H/'d1-merged-v1/derived-strip.png').convert('RGB'));sm=np.array(Image.open(H/'d1-merged-v1/alpha.png'))>0
a[430:1684,:2354][sm]=strip[sm];ma[430:1684,:2354]|=sm
a[550:1804,1100:2354][rm>0]=ret[rm>0];ma[550:1804,1100:2354]|=rm>0
b[430:1684,3500:][wm[:,:596]>0]=west[:,:596][wm[:,:596]>0];mb[430:1684,3500:]|=wm[:,:596]>0
a[430:1684,:658][wm[:,596:]>0]=west[:,596:][wm[:,596:]>0];ma[430:1684,:658]|=wm[:,596:]>0
for tile,arr,mask in [('r03_c04',b,mb),('r03_c05',a,ma)]:
 p.save_png(O/(tile+'-trial.png'),Image.fromarray(arr));p.save_png(O/(tile+'-support.png'),Image.fromarray(mask.astype('uint8')*255))
for label,box in [('return-left',[1100,1170,1550,1510]),('return-middle',[1500,1170,1950,1510]),('return-right',[1900,1170,2354,1510]),('top-return',[200,610,850,810])]:p.save_png(O/(label+'.png'),Image.fromarray(a).crop(tuple(box)))
cross=np.concatenate([b[760:1150,3936:],a[760:1150,:200]],axis=1)
p.save_png(O/'west-joint.png',Image.fromarray(cross))
print(O)

