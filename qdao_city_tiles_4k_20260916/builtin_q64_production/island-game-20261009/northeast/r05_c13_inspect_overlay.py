from native_work import *
import sys
id=sys.argv[1]
p=ZONE/'native'/f'{id}.png';r=read(p.with_suffix('.png.generation.json'));x=r['coreWorldBox'][0]-49152;y=r['coreWorldBox'][1]-16384
base=ZONE/'tiles/r05_c13.png';out=Image.open(base).convert('RGB');out.paste(Image.open(p).crop(tuple(r['coreCrop'])),(x,y))
for name,box in dict(top=[x,y-128,x+1024,y+128],bottom=[x,y+896,x+1024,y+1152],left=[x-128,y,x+128,y+1024],right=[x+896,y,x+1152,y+1024]).items():out.crop(box).save(ZONE/'qa'/f'{id}-{name}-100pct.png')
write(ZONE/'qa'/f'{id}.overlay.json',dict(operation='exact native1024 repair core overlay; no scaling or feathering',source=p.as_posix(),sha256=sha(p),generationRecord=p.with_suffix('.png.generation.json').as_posix(),coreCrop=r['coreCrop'],tileLocalPaste=[x,y],worldPaste=r['coreWorldBox'][:2],review='pending_four_perimeter_visual',baseFile=base.as_posix(),baseSha256=sha(base)))
out.resize((1536,1536),Image.Resampling.LANCZOS).save(ZONE/'qa'/f'{id}-preview.png')

