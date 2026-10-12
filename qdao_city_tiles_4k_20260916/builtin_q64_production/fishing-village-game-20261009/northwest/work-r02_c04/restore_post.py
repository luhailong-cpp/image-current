from PIL import Image,ImageDraw
import numpy as np
from production import W,read,write,sha
m=read(W/'joint-v2/joint.assembly.json');a=np.asarray(Image.open(m['file'])).copy();ids=np.asarray(Image.open(m['sourceIdMap'])).copy()
p=W/'native/r02_c04_r03_c04_fence_post_whole_bridge_v01.png';src=np.asarray(Image.open(p));s=next(s for s in m['sources'] if s['sha256']==sha(p));x=3072;y=7453-3981
im=Image.new('L',(1254,1254));ImageDraw.Draw(im).polygon([(552,180),(564,120),(621,87),(730,85),(790,120),(812,177),(811,1050),(780,1175),(600,1165),(551,1070)],fill=255);mask=np.asarray(im)>0;a[y:y+1254,x:x+1254][mask]=src[mask];ids[y:y+1254,x:x+1254][mask]=s['sourceId']
D=W/'joint-v3';D.mkdir(exist_ok=True);im.save(D/'whole-post-object.mask.png');Image.fromarray(a).save(D/'joint.context.png');Image.fromarray(ids).save(D/'joint.source-id.png');m.update(file=str(D/'joint.context.png'),sourceIdMap=str(D/'joint.source-id.png'),baseAssembly=str(W/'joint-v2/joint.assembly.json'));write(D/'joint.assembly.json',m)
for n,b in [('hedge-post-foot-v01',[15245,7870,16499,9124]),('west-fence-span-v01',[12173,5700,13427,6954])]:
 p=W/'guides'/(n+'.target.png');Image.fromarray(a).crop((b[0]-12173,b[1]-3981,b[2]-12173,b[3]-3981)).save(p);write(str(p)+'.derivation.json',{'guideOnly':True,'globalNativeBox':b,'sourceAssembly':str(D/'joint.assembly.json'),'nativeScaleResampled':False})

