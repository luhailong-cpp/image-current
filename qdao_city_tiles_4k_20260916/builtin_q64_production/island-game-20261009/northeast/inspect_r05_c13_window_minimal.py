from native_work import *
id='r05_c13_cross_03_window_repair_v2';p=ZONE/'native'/f'{id}.png';rec=read(p.with_suffix('.png.generation.json'))
base=ZONE/'tiles/r05_c13.png';out=Image.open(base).convert('RGB')
crop=[500,115,900,1139];at=[2828,2048];out.paste(Image.open(p).crop(crop),at)
out.save(ZONE/'qa/r05_c13-window-minimal-composite-native.png')
for name,box in dict(top=[at[0],1920,3228,2176],bottom=[at[0],2944,3228,3200],left=[2700,2048,2956,3072],right=[3100,2048,3356,3072],whole=[2700,1920,3356,3200]).items():out.crop(box).save(ZONE/'qa'/f'{id}-minimal-{name}-100pct.png')
write(ZONE/'qa'/f'{id}-minimal.overlay.json',dict(operation='exact400x1024 subregion of native1024 repair core; hard crop no scaling feathering or blending',source=p.as_posix(),sha256=sha(p),generationRecord=p.with_suffix('.png.generation.json').as_posix(),coreCrop=crop,nativeCoreCrop=[115,115,1139,1139],tileLocalPaste=at,worldPaste=[49152+at[0],16384+at[1]],review='pending_minimal_region_perimeter',baseFile=base.as_posix(),baseSha256=sha(base)))

