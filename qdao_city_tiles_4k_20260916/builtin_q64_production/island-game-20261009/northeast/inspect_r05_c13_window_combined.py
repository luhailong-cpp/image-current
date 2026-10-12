from native_work import *
id='r05_c13_cross_03_window_repair_v2'; p=ZONE/'native'/f'{id}.png';rec=read(p.with_suffix('.png.generation.json'))
base=ZONE/'qa/r05_c13-window-v1-composite-native.png';out=Image.open(base).convert('RGB');out.paste(Image.open(p).crop((115,115,1139,1139)),(2443,2048))
out.save(ZONE/'qa/r05_c13-window-combined-native.png')
for name,box in dict(top=[2443,1662,3467,1918],bottom=[2443,2944,3467,3200],left=[2315,1790,2571,3072],right=[3339,1790,3595,3072],middle=[2443,1920,3467,2176]).items():out.crop(box).save(ZONE/'qa'/f'{id}-{name}-100pct.png')
write(ZONE/'qa'/f'{id}.overlay.json',dict(operation='exact native1024 repair core overlay; no scaling or feathering',source=p.as_posix(),sha256=sha(p),generationRecord=p.with_suffix('.png.generation.json').as_posix(),coreCrop=rec['coreCrop'],tileLocalPaste=[2443,2048],worldPaste=rec['coreWorldBox'][:2],review='pending_combined_perimeter_visual',baseFile=base.as_posix(),baseSha256=sha(base)))

