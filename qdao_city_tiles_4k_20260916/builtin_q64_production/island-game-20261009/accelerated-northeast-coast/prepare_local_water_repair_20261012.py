from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import sys,json
import coast_work as c
B=Path(__file__).resolve().parent
ident,sourceid=sys.argv[1:]
src=B/'native'/f'{sourceid}.png'
assert not (B/'native'/f'{ident}.png').exists()
original=Image.open(src).convert('RGB')
box=(145,850,450,1110)
blur=original.filter(ImageFilter.GaussianBlur(24))
mask=Image.new('L',original.size)
ImageDraw.Draw(mask).rectangle((165,870,430,1090),fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(10))
# Restrict to core-interior band so real join rows/columns remain sharp.
limit=Image.new('L',original.size)
ImageDraw.Draw(limit).rectangle(box,fill=255)
from PIL import ImageChops
mask=ImageChops.multiply(mask,limit)
guide=Image.composite(blur,original,mask)
dest=B/'guides'/f'{ident}.local-repaint-guide.png'
assert not dest.exists()
guide.save(dest)
c.write(dest.with_suffix('.png.derivation.json'),{
 'operation':'mechanical softening of recorded defect for GUIDE ONLY; final must be builtin-redrawn crisp artwork',
 'source':src.as_posix(),'sourceSha256':c.sha(src),'box':box,'finalPixels':False,
 'trueCoreJoinPreservedAtNativeX':115,'trueCoreJoinPreservedAtNativeY':1139})
c.prepare(ident,[],str(dest))
refs=c.read(B/'prompts'/f'{ident}.inputs.json')
refs.insert(1,c.ref(src,'original native edit reference: keep outside local repaint region and true edge joins'))
c.write(B/'prompts'/f'{ident}.inputs.json',refs)

