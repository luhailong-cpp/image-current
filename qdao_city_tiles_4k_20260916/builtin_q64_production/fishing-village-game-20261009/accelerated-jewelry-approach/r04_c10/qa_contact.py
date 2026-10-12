from pathlib import Path
from PIL import Image
import json, hashlib, numpy as np
d=Path(__file__).parent
im=Image.open(d/'candidate/r04_c10-4096-candidate-v1.png').convert('RGB')
qa=d/'qa'
for a in [1024,2048,3072]:
 v=Image.new('RGB',(1024,1024));h=Image.new('RGB',(1024,1024))
 for i in range(4):
  v.paste(Image.open(qa/f'vertical-x{a}-y{i*1024}.png'),(i*256,0))
  h.paste(Image.open(qa/f'horizontal-y{a}-x{i*1024}.png'),(0,i*256))
 v.save(qa/f'vertical-x{a}-native-atlas.png');h.save(qa/f'horizontal-y{a}-native-atlas.png')
north=Image.open(d.parent/'r03_c10/candidate/r03_c10-4096-candidate-v1.png').convert('RGB')
for i in range(4):
 c=Image.new('RGB',(1024,256))
 c.paste(north.crop((i*1024,3968,(i+1)*1024,4096)),(0,0))
 c.paste(im.crop((i*1024,0,(i+1)*1024,128)),(0,128))
 c.save(qa/f'north-seam-{i+1}-native.png')
print('Created 6 unscaled 1024-square atlases of all 24 internal seam crops, and 4 north seam crops.')

