from workflow import *
from PIL import Image
dest=ROOT/'qa/center-r10c12-external-20261011'
current={'r09_c11':'v04','r09_c12':'v08','r09_c13':'v02','r10_c11':'v04','r10_c12':'v02','r10_c13':'v02','r11_c11':'v02','r11_c12':'v02','r11_c13':'v02'}
out={}
for name,r,c in [('NW',9,11),('NE',9,12),('SW',10,11),('SE',10,12)]:
 im=Image.new('RGB',(512,512));parts=[]
 for dr,dc in [(0,0),(0,1),(1,0),(1,1)]:
  tid=f'r{r+dr:02d}_c{c+dc:02d}';f=ROOT/'tiles'/f'{tid}.candidate-{current[tid]}.png';box=[3840 if dc==0 else 0,3840 if dr==0 else 0,4096 if dc==0 else 256,4096 if dr==0 else 256];im.paste(Image.open(f).convert('RGB').crop(box),(dc*256,dr*256));parts.append({'file':str(f),'sha256':sha(f),'sourceCrop':box,'destination':[dc*256,dr*256]})
 f=dest/f'final-corner-{name}.png';im.save(f);out[name]={'file':str(f),'sha256':sha(f),'sources':parts,'status':'pending_root_native_visual_review'}
write(dest/'final-corners.json',{'createdAt':now(),'operation':'exact crop and paste; no scaling, blending or RGB edits','corners':out})
print('created four exact candidate corners')
