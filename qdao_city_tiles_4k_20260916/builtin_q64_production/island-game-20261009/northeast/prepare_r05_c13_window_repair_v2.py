from native_work import *
id='r05_c13_cross_03_window_repair_v2'
base=ZONE/'tiles/r05_c13.png'; prev=ZONE/'native/r05_c13_cross_03_window_repair.png'
out=Image.open(base).convert('RGB');out.paste(Image.open(prev).crop((115,115,1139,1139)),(2443,1790))
combined=ZONE/'qa/r05_c13-window-v1-composite-native.png';out.save(combined)
box=[2328,1933,3582,3187]; core=[2443,2048,3467,3072]
p=ZONE/'guides'/f'{id}.png';out.crop(box).save(p)
write(p.with_suffix('.png.derivation.json'),dict(operation='exact1254 crop from native composite; no scale',sources=[dict(file=base.as_posix(),sha256=sha(base)),dict(file=prev.as_posix(),sha256=sha(prev),crop=[115,115,1139,1139],paste=[2443,1790])],tileCrop=box,nativeWorldBox=[box[0]+49152,box[1]+16384,box[2]+49152,box[3]+16384],coreWorldBox=[core[0]+49152,core[1]+16384,core[2]+49152,core[3]+16384],coreCrop=[115,115,1139,1139]))
write(ZONE/'prompts'/f'{id}.inputs.json',[dict(file=p.as_posix(),sha256=sha(p),role='edit target exact1254 crop of tile with previous native repair; remove leftover collage seam through counter front and lower bracket')])

