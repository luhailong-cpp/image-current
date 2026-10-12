from native_work import *
id='r05_c13_cross_03_window_repair'
base=ZONE/'tiles/r05_c13.png'
box=[2328,1675,3582,2929]
p=ZONE/'guides'/f'{id}.png'
Image.open(base).crop(box).save(p)
core=[2443,1790,3467,2814]
write(p.with_suffix('.png.derivation.json'),dict(operation='exact1254 crop from assembled native tile, no scale',source=base.as_posix(),sha256=sha(base),tileCrop=box,nativeWorldBox=[box[0]+49152,box[1]+16384,box[2]+49152,box[3]+16384],coreWorldBox=[core[0]+49152,core[1]+16384,core[2]+49152,core[3]+16384],coreCrop=[115,115,1139,1139]))
write(ZONE/'prompts'/f'{id}.inputs.json',[dict(file=p.as_posix(),sha256=sha(p),role='edit target exact1254 native tile crop; repair only tiny straight cut in window foliage, keep all surrounding geometry and pixels')])
print(p)

