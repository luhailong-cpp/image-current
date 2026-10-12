from native_work import *
import sys
name=sys.argv[1];ids=sys.argv[2:6]
boxes=[(883,883,1139,1139),(115,883,371,1139),(883,115,1139,371),(115,115,371,371)]
dest=ZONE/'qa'/f'{name}.png';assert not dest.exists()
out=Image.new('RGB',(512,512));sources=[]
for i,ident in enumerate(ids):
 p=ZONE/'native'/f'{ident}.png';out.paste(Image.open(p).crop(boxes[i]),((i%2)*256,(i//2)*256));sources.append({'file':str(p),'sha256':sha(p),'crop':list(boxes[i])})
out.save(dest);write(dest.with_suffix('.json'),{'sources':sources,'operation':'exact native crops without resampling or blending','inspectionScale':1,'status':'pending_visual_review'})
print(str(dest))
