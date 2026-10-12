from PIL import Image,ImageDraw
import numpy as np,json
from production import W,read,write,sha
D=W/'assembly-v2';D.mkdir(exist_ok=True)
ap=W/'assembly/r02_c04.assembly.json';m=read(ap);a=np.asarray(Image.open(W/'assembly/r02_c04.with-halo.png')).copy();ids=np.asarray(Image.open(W/'assembly/r02_c04.with-halo.source-id.png')).copy();sources=m['sources']
patches=[
 ('r02_c04_rail_span_left_v01',[(165,280),(335,280),(1090,630),(1100,1100),(800,1130),(200,800),(150,600)]),
 ('r02_c04_rail_span_right_v01',[(210,300),(400,280),(1235,660),(1245,1253),(1030,1253),(400,1100),(210,900)])
]
for n,poly in patches:
 p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');b=g['globalNativeBox'];x=b[0]-12173;y=b[1]-3981
 z=Image.new('L',(1254,1254));ImageDraw.Draw(z).polygon(poly,fill=255);mask=np.asarray(z)>0;src=np.asarray(Image.open(p));k=max(s['sourceId'] for s in sources)+1
 a[y:y+1254,x:x+1254][mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=k;z.save(D/(n+'.hard-mask.png'))
 sources.append({'sourceId':k,'file':str(p),'sha256':sha(p),'globalNativeBox':b,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'actualModel':None,'actualQuality':None})
Image.fromarray(a).save(D/'r02_c04.with-halo.png');Image.fromarray(ids).save(D/'r02_c04.with-halo.source-id.png')
Image.fromarray(a[115:4211,115:4211]).save(D/'r02_c04.candidate.png');Image.fromarray(ids[115:4211,115:4211]).save(D/'r02_c04.source-id.png')
m.update({'file':str(D/'r02_c04.candidate.png'),'sha256':sha(D/'r02_c04.candidate.png'),'sourceIdMap':{'file':str(D/'r02_c04.source-id.png'),'sha256':sha(D/'r02_c04.source-id.png')},'sources':sources,'status':'bridge-patches-qa-pending','baseAssembly':str(ap)})
write(D/'r02_c04.assembly.json',m)
Image.fromarray(a[115:4211,115:4211]).resize((1024,1024),Image.Resampling.LANCZOS).save(W/'qa/r02_c04.v2.preview-only.png')
for n,g in [('rail-left',[13373,6581,14627,7835]),('rail-right',[14673,7001,15927,8255])]:
 Image.fromarray(a).crop((g[0]-12173,g[1]-3981,g[2]-12173,g[3]-3981)).save(W/'qa'/(n+'.v2.100pct.png'))
# Full-height shifted right beam/post-span frame to show the entire low beam connection.
p=W/'guides/rail-span-right-v02.target.png';Image.fromarray(a).crop((2500,3159,3754,4413)).save(p)
write(str(p)+'.derivation.json',{'guideOnly':True,'globalNativeBox':[14673,7140,15927,8394],'baseAssembly':str(D/'r02_c04.assembly.json'),'note':'lower 87px beyond halo filled later from exact current south context'})

