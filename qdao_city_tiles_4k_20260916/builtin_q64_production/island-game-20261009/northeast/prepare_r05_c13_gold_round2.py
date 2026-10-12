from native_work import *
id='r05_c13_cross_02_03_gold_repair'
a='r05_c13_p02_03_v3';b='r05_c13_p02_04_v2'
pa=ZONE/'native'/f'{a}.png';pb=ZONE/'native'/f'{b}.png'
ia=Image.open(pa);ib=Image.open(pb)
im=Image.new('RGB',(1254,1254));im.paste(ia.crop((512,0,1139,1254)),(0,0));im.paste(ib.crop((115,0,742,1254)),(627,0))
p=ZONE/'guides'/f'{id}.png';im.save(p)
write(p.with_suffix('.png.derivation.json'),dict(operation='exact native crops straddling shared gold beam join, no resampling',sources=[dict(file=pa.as_posix(),sha256=sha(pa),crop=[512,0,1139,1254],paste=[0,0]),dict(file=pb.as_posix(),sha256=sha(pb),crop=[115,0,742,1254],paste=[627,0])],nativeWorldBox=[51597,17293,52851,18547],coreWorldBox=[51712,17408,52736,18432],coreCrop=[115,115,1139,1139],tileLocalPaste=[2560,1024],finalArt=False))
write(ZONE/'prompts'/f'{id}.inputs.json',[dict(file=p.as_posix(),sha256=sha(p),role='native edit target; repair only center gold-beam edge steps; preserve outer200px')])

