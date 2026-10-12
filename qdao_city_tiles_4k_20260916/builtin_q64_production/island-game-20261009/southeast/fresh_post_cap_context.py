from workflow import *
from PIL import Image
pid='r09_c13_p22';version='v03';p=patch(pid);base=ROOT/'guides'/f'{pid}.layout-only.png';im=Image.open(base).convert('RGB');parts=[]
for name,crop,dest in [('r09_c13_p21_v02.png',[1024,0,1254,1254],[0,0]),('r09_c13_p23_v01.png',[115,0,230,1254],[1139,0]),('r09_c13_p12_v01.png',[0,1024,1254,1254],[0,0]),('r09_c13_p32_v03.png',[0,0,1254,230],[0,1024])]:
 src=ROOT/'native'/name;im.paste(Image.open(src).convert('RGB').crop(crop),dest);parts.append({'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':dest,'note':'Exact native global coordinate overlap'})
out=ROOT/'guides'/f'{pid}.native-context-{version}.png';assert not out.exists();im.save(out);write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'layoutBase':str(base),'layoutBaseSha256':sha(base),'placements':parts,'usableAsFinalArt':False,'nativeGlobalBox':p['nativeGlobalBox']})
print(out)

