from native_work import *
id='r05_c13_cross_03_window_repair_v3'
base=ZONE/'tiles/r05_c13.png';box=[2445,1933,3699,3187];p=ZONE/'guides'/f'{id}.png'
Image.open(base).crop(box).save(p)
write(p.with_suffix('.png.derivation.json'),dict(operation='exact1254 crop from assembled native tile; no scale',source=base.as_posix(),sha256=sha(base),tileCrop=box,nativeWorldBox=[box[0]+49152,box[1]+16384,box[2]+49152,box[3]+16384],coreWorldBox=[51712,18432,52736,19456],coreCrop=[115,115,1139,1139]))
write(ZONE/'prompts'/f'{id}.inputs.json',[dict(file=p.as_posix(),sha256=sha(p),role='edit target; remove central compositing seam and smaller leaf cut without altering anywhere outside narrow center band')])

