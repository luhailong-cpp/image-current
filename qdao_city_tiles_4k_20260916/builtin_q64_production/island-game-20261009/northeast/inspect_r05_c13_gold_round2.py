from native_work import *
id='r05_c13_cross_02_03_gold_repair_v2'
p=ZONE/'native'/f'{id}.png';r=read(p.with_suffix('.png.generation.json'))
out=Image.open(ZONE/'guides/r05_c13_cross_02_03_gold_repair.png');out.paste(Image.open(p).crop((115,115,1139,1139)),(115,115))
for name,box in dict(top=[115,15,1139,215],bottom=[115,1039,1139,1239],left=[15,115,215,1139],right=[1039,115,1239,1139]).items():out.crop(box).save(ZONE/'qa'/f'{id}-{name}-100pct.png')
write(ZONE/'qa'/f'{id}.overlay.json',dict(operation='exact1024 native crop overlay, no scaling or blending',source=p.as_posix(),sha256=sha(p),generationRecord=p.with_suffix('.png.generation.json').as_posix(),coreCrop=[115,115,1139,1139],tileLocalPaste=[2560,1024],worldPaste=[51712,17408],review='pending four perimeter visual; top and bottom full tile QA still required'))

