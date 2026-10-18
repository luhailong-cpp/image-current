from workflow import *
from PIL import Image
q=ROOT/'qa'/'r08_c10-wall-recover-20261013-v01'
for r in range(1,5):
 im=Image.new('RGB',(1536,1024))
 for c in range(1,4):im.paste(Image.open(q/f'h{r}{c}.png'),((c-1)*512,0))
 im.save(q/f'contact-h{r}.png')
for r in range(1,4):
 for c0 in [1,3]:
  im=Image.new('RGB',(1024,1024))
  for i in range(2):im.paste(Image.open(q/f'v{r}{c0+i}.png'),(0,i*512))
  im.save(q/f'contact-v{r}{c0}.png')
for r in range(1,4):
 im=Image.new('RGB',(1536,512))
 for c in range(1,4):im.paste(Image.open(q/f'junction_{r}{c}.png'),((c-1)*512,0))
 im.save(q/f'contact-j{r}.png')
print(str(q))
