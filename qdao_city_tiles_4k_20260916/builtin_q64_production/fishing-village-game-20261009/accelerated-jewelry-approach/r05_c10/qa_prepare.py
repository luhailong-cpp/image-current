from pathlib import Path
from PIL import Image
import json,hashlib
d=Path(__file__).parent
im=Image.open(d/'candidate/r05_c10-4096-candidate-v1.png').convert('RGB')
q=d/'qa'
for a in [1024,2048,3072]:
 v=Image.new('RGB',(1024,1024));h=Image.new('RGB',(1024,1024))
 for i in range(4):
  v.paste(Image.open(q/f'vertical-x{a}-y{i*1024}.png'),(i*256,0))
  h.paste(Image.open(q/f'horizontal-y{a}-x{i*1024}.png'),(0,i*256))
 v.save(q/f'vertical-x{a}-native-atlas.png');h.save(q/f'horizontal-y{a}-native-atlas.png')
north=Image.open(d.parent/'r04_c10/candidate/r04_c10-4096-candidate-v2.png').convert('RGB')
for i in range(4):
 c=Image.new('RGB',(1024,256));c.paste(north.crop((i*1024,3968,(i+1)*1024,4096)),(0,0));c.paste(im.crop((i*1024,0,(i+1)*1024,128)),(0,128));c.save(q/f'north-seam-{i+1}-native.png')
rd=d/'repairs/post-net-connection-v1';rd.mkdir(parents=True,exist_ok=True)
box=[1480,0,2734,1254];target=im.crop(box);target.save(rd/'before-native.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
(rd/'before-native.derivation.json').write_text(json.dumps({'source':str(d/'candidate/r05_c10-4096-candidate-v1.png'),'sourceSha256':sha(d/'candidate/r05_c10-4096-candidate-v1.png'),'cropTileBox':box,'cropGlobalBox':[38344,16384,39598,17638],'dimensions':[1254,1254],'nativePixelsResized':False,'sha256':sha(rd/'before-native.png')},indent=2)+'\n')
print('Native seam atlases and repair target saved')

