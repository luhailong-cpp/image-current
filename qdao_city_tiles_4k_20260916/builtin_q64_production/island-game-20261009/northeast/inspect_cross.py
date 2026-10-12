from native_work import *
import sys
ids=sys.argv[1:5]
boxes=[(883,883,1139,1139),(115,883,371,1139),(883,115,1139,371),(115,115,371,371)]
out=Image.new('RGB',(512,512)); sources=[]
for i,ident in enumerate(ids):
    p=ZONE/'native'/f'{ident}.png'; out.paste(Image.open(p).crop(boxes[i]),((i%2)*256,(i//2)*256)); sources.append({'file':p.as_posix(),'sha256':sha(p),'crop':list(boxes[i])})
name='cross_'+ids[-1]; dest=ZONE/'qa'/f'{name}.png'; out.save(dest)
write(dest.with_suffix('.json'),{'sources':sources,'operation':'exact native crops, no resizing or blending','inspectionScale':1,'status':'pending_visual_review'})
print(dest)
