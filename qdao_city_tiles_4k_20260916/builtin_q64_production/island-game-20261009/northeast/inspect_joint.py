"""Inspect native repair core against exact source mosaic, no feathering."""
from native_work import *
import sys
ident=sys.argv[1];guide=ZONE/'guides'/f'{ident}.png';der=read(guide.with_suffix('.png.derivation.json'));src=ZONE/'native'/f'{ident}.png';rec=read(src.with_suffix('.png.generation.json'));assert sha(src)==rec['sha256']
im=Image.open(src).convert('RGB');assert im.size==(1254,1254)
context=Image.open(ZONE/'guides'/f'{ident}.context.png').convert('RGB')
out=context.copy();out.paste(im.crop((115,115,1139,1139)),(512,512));out.save(ZONE/'qa'/f'{ident}.applied-context.png')
edges={}
for name,box in {'top':(512,384,1536,640),'bottom':(512,1408,1536,1664),'left':(384,512,640,1536),'right':(1408,512,1664,1536)}.items():
 path=ZONE/'qa'/f'{ident}.edge-{name}.png';out.crop(box).save(path);edges[name]=path.as_posix()
write(ZONE/'qa'/f'{ident}.overlay.json',{'id':ident,'source':src.as_posix(),'sha256':sha(src),'generationRecord':src.with_suffix('.png.generation.json').as_posix(),'coreCrop':[115,115,1139,1139],'tileLocalPaste':der['tileLocalPaste'],'coreWorldBox':der['coreWorldBox'],'operation':'exact native1024repair core overlay, no scaling, no feather','edges':edges,'review':'pending_visual_review','sourceMosaic':der['sources'],'actualModel':None,'actualQuality':None})
print(json.dumps({'overlay':ident,'edges':edges}))

