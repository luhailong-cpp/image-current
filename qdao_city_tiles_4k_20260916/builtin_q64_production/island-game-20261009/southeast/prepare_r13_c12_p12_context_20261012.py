from workflow import *
from PIL import Image
pid='r13_c12_p12';v='v01';layout=ROOT/'guides'/f'{pid}.layout-only.png';im=Image.open(layout).convert('RGB');parts=[{'file':str(layout),'sha256':sha(layout),'role':'layout only'}]
for nn,crop,dest in [('r13_c12_p11_v02.png',[1024,0,1254,1254],[0,0]),('r12_c12_p42_v01.png',[0,1024,1254,1254],[0,0]),('r12_c12_lower_deck_joint_v01.png',[512,1024,1139,1254],[0,0])]:
 f=ROOT/'native'/nn;im.paste(Image.open(f).convert('RGB').crop(crop),dest);parts.append({'file':str(f),'sha256':sha(f),'sourceCrop':crop,'destination':dest})
g=ROOT/'guides'/f'{pid}.native-context-{v}.png';assert not g.exists();im.save(g)
write(Path(str(g)+'.generation.json'),{'file':str(g),'sha256':sha(g),'nativeGlobalBox':patch(pid)['nativeGlobalBox'],'operation':'exact unscaled native north and west strips, accepted overlay north ownership preserved','usableAsFinalArt':False,'sources':parts})
print(g)
