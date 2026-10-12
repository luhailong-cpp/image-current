from native_work import *
id='r05_c13_cross_left_p01_beam_repair'
ids=['r05_c12_p01_04','r05_c13_p01_01_v2'];out=Image.new('RGB',(1254,1254));sources=[]
for i,pid in enumerate(ids):
 p=ZONE/'native'/f'{pid}.png';crop=[512,0,1139,1254] if i==0 else [115,0,742,1254];at=[i*627,0]
 out.paste(Image.open(p).crop(crop),at);sources.append(dict(file=p.as_posix(),sha256=sha(p),crop=crop,paste=at))
p=ZONE/'guides'/f'{id}.png';out.save(p)
write(p.with_suffix('.png.derivation.json'),dict(operation='exact native side-by-side seam crop; no scale',sources=sources,nativeWorldBox=[48525,16269,49779,17523],coreWorldBox=[48640,16384,49664,17408],coreCrop=[115,115,1139,1139]))
write(ZONE/'prompts'/f'{id}.inputs.json',[dict(file=p.as_posix(),sha256=sha(p),role='edit target native exact cross tile seam; reconcile narrow red trim only preserving all outer geometry')])

