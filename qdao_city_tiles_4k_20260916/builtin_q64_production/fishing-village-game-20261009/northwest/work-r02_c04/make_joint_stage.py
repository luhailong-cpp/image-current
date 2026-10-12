from PIL import Image,ImageDraw
import numpy as np,json
from production import W,B,read,write,sha
D=W/'joint-stage';D.mkdir(exist_ok=True)
m=read(W/'assembly-v2/r02_c04.assembly.json');sources=m['sources'];rgb=np.zeros((5350,4326,3),np.uint8);ids=np.zeros((5350,4326),np.uint16)
rgb[:4326]=np.asarray(Image.open(W/'assembly-v2/r02_c04.with-halo.png'));ids[:4326]=np.asarray(Image.open(W/'assembly-v2/r02_c04.with-halo.source-id.png'))
rgb[4326:]=np.asarray(Image.open(W/'guides/current-r03-north-context-post-candidate.png'))[230:]
ap=B/'delivery-2x2/stage-v3/r03_c04.assembly.json';a=read(ap);si=np.asarray(Image.open(a['sourceIdMap']['file']))
gy,gx=np.indices((1024,4326));gy+=8307;gx+=12173
ids[4326:]=si[np.clip(gy-8192,0,4095),np.clip(gx-12288,0,4095)]
p=W/'selected/s04s04-post-south.source-id.png';ids[4326:,3072:]=np.asarray(Image.open(p))[1254:]
existing={s['sourceId'] for s in sources}
for s in read(W/'selected/s04s04-post-south.assembly.json')['sources']:
 if s['sourceId'] not in existing:sources.append(s)
n='r02_c04_rail_span_right_v02';p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');gb=g['globalNativeBox'];x=gb[0]-12173;y=gb[1]-3981;k=max(s['sourceId'] for s in sources)+1
maskim=Image.new('L',(1254,1254));ImageDraw.Draw(maskim).polygon([(220,490),(390,510),(1234,1020),(1245,1253),(1010,1253),(400,1020),(210,840)],fill=255);mask=np.asarray(maskim)>0;src=np.asarray(Image.open(p));rgb[y:y+1254,x:x+1254][mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=k;maskim.save(D/(n+'.hard-mask.png'))
sources.append({'sourceId':k,'file':str(p),'sha256':sha(p),'globalNativeBox':gb,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'actualModel':None,'actualQuality':None})
Image.fromarray(rgb).save(D/'joint.context.png');Image.fromarray(ids).save(D/'joint.source-id.png');write(D/'joint.assembly.json',{'globalBox':[12173,3981,16499,9331],'file':str(D/'joint.context.png'),'sourceIdMap':str(D/'joint.source-id.png'),'sources':sources,'baseAssembly':str(ap),'status':'all-cells-covered-joins-under-review','formalAccepted':False})
for name,b in [('paving-south-west-v01',[12173,7500,13427,8754]),('paving-south-mid-v01',[13197,7500,14451,8754]),('paving-south-east-v01',[14221,7650,15475,8904])]:
 p=W/'guides'/(name+'.target.png');Image.fromarray(rgb).crop((b[0]-12173,b[1]-3981,b[2]-12173,b[3]-3981)).save(p);write(str(p)+'.derivation.json',{'guideOnly':True,'globalNativeBox':b,'sourceAssembly':str(D/'joint.assembly.json'),'nativeScaleResampled':False})
Image.fromarray(rgb).crop((2500,3159,3754,4413)).save(W/'qa/right-span-complete.100pct.png')

