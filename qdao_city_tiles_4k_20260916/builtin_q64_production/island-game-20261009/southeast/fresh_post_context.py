from workflow import *
from PIL import Image
pid='r09_c13_p32';version='v03';p=patch(pid);base=ROOT/'guides'/f'{pid}.layout-only.png';im=Image.open(base).convert('RGB');parts=[]
for name,crop,dest in [('r09_c13_p31_v01.png',[1024,0,1254,1254],[0,0]),('r09_c13_p33_v03.png',[115,0,230,1254],[1139,0]),('r09_c13_p42_v01.png',[0,0,1254,230],[0,1024])]:
 src=ROOT/'native'/name;im.paste(Image.open(src).convert('RGB').crop(crop),dest);parts.append({'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':dest,'note':'Exact native world-coordinate overlap, no resize or shift'})
out=ROOT/'guides'/f'{pid}.native-context-{version}.png';assert not out.exists();im.save(out);write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'layoutBase':str(base),'layoutBaseSha256':sha(base),'placements':parts,'operation':'Exact crop/paste of real adjacent native overlap onto coordinate-only layout guide; side anchor reduced to outer115 to avoid propagating rejected old post contour','usableAsFinalArt':False,'nativeGlobalBox':p['nativeGlobalBox']})
d=read(ROOT/'progress.json');d.update({'status':'fresh_context_post_rebuild','currentTile':'r09_c13','generatedNativeCount':0,'assignedPatches':['32','22'],'updatedAt':now()});write(ROOT/'progress-helper-r09_c13.json',d)
print(str(out))

