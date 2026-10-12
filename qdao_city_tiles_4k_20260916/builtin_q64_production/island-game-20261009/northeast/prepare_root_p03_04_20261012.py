from native_work import *
from types import SimpleNamespace
ids=['r03_c10_p01_04','r03_c11_p01_01','r03_c10_p02_04_v2','r03_c11_p02_01']
boxes=[(883,883,1139,1139),(115,883,371,1139),(883,115,1139,371),(115,115,371,371)]
dest=ZONE/'qa/root-resume-20261012-p02_04_v2-cross.png'
if not dest.exists():
 out=Image.new('RGB',(512,512));sources=[]
 for i,ident in enumerate(ids):
  p=ZONE/'native'/f'{ident}.png';out.paste(Image.open(p).crop(boxes[i]),((i%2)*256,(i//2)*256));sources.append({'file':str(p),'sha256':sha(p),'crop':list(boxes[i])})
 out.save(dest);write(dest.with_suffix('.json'),{'sources':sources,'inspectionScale':1,'status':'pending_visual_review','operation':'exact native crops without scaling'})
ident='r03_c10_p03_04'
assert not (ZONE/'guides'/f'{ident}.anchored-layout-only.png').exists()
guide(SimpleNamespace(id=ident,neighbor=['r03_c10_p02_04_v2','r03_c11_p03_01'],base=None))
inp=ZONE/'prompts'/f'{ident}.inputs.json';refs=read(inp);refs[1]['role']='native neighbor reference plate: left=UPPER neighbor, right=RIGHT neighbor; both1254-square unscaled';write(inp,refs)
print(str(dest))
