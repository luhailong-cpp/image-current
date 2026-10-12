from PIL import Image
import pipeline as p
out=p.ROOT/'qa-final-fourway-v1';out.mkdir(exist_ok=True)
files={'r03_c04':'r03_c04-pipeline-fixed-native-contexts-424e41dd0ce0','r03_c05':'r03_c05-pipeline-minimum-error-ece82fe09771-fbbe92','r04_c04':'r04_c04-pipeline-fixed-native-contexts-71cabb17b21f','r04_c05':'r04_c05-pipeline-minimum-error-e2769dba9467-6e5fcf'}
im=Image.new('RGB',(320,320));sources=[]
for tile,stem in files.items():
 f=p.ROOT/tile/'candidate'/(stem+'.png');r=int(tile[1:3]);c=int(tile[5:7]);box=[3936 if c==4 else 0,3936 if r==3 else 0,4096 if c==4 else 160,4096 if r==3 else 160]
 piece=Image.open(f).crop(box);im.paste(piece,((c-4)*160,(r-3)*160));sources.append({'tile':tile,'file':str(f),'sha256':p.sha(f),'cropBox':box})
info=p.save_png(out/'junction-world-x16384-y12288-native.png',im)
p.put_json(out/'manifest.json',{'image':info,'sources':sources,'nativeScale':1,'worldBox':[16224,12128,16544,12448],'resampled':False,'formalAccepted':False})
