from native_work import *
id='r05_c13_cross_left_p01_beam_repair';src=ZONE/'native'/f'{id}.png'
out=Image.new('RGB',(2048,3072));sources=[]
for tid,sc,at in [('r04_c12',[3072,3072,4096,4096],[0,0]),('r04_c13',[0,3072,1024,4096],[1024,0]),('r05_c13',[0,0,1024,2048],[1024,1024])]:
 p=ZONE/'tiles'/f'{tid}.png';out.paste(Image.open(p).crop(sc),at);sources.append(dict(file=p.as_posix(),sha256=sha(p),crop=sc,paste=at))
for row in [1,2]:
 p=ZONE/'native'/f'r05_c12_p0{row}_04.png';out.paste(Image.open(p).crop((115,115,1139,1139)),(0,row*1024));sources.append(dict(file=p.as_posix(),sha256=sha(p),crop=[115,115,1139,1139],paste=[0,row*1024]))
base=ZONE/'qa'/f'{id}-surrounding-native.png';out.save(base)
out.paste(Image.open(src).crop((115,115,1139,1139)),(512,1024))
out.save(ZONE/'qa'/f'{id}-composite-native.png')
for name,box in dict(top=[512,896,1536,1152],bottom=[512,1920,1536,2176],left=[384,1024,640,2048],right=[1408,1024,1664,2048],join=[896,1024,1152,2048]).items():out.crop(box).save(ZONE/'qa'/f'{id}-{name}-100pct.png')
for tile,crop,at,world in [('r05_c12',[115,115,627,1139],[3584,0],[48640,16384]),('r05_c13',[627,115,1139,1139],[0,0],[49152,16384])]:
 write(ZONE/'qa'/f'{id}-{tile}.overlay.json',dict(operation='exact512x1024 partition of shared native1024 repair core; no scale or feather',sharedRepairId=id,source=src.as_posix(),sha256=sha(src),generationRecord=src.with_suffix('.png.generation.json').as_posix(),coreCrop=crop,tileLocalPaste=at,worldPaste=world,worldBox=[world[0],world[1],world[0]+512,world[1]+1024],review='pending_shared_full_surrounding_review',baseSources=sources))
write(ZONE/'qa'/f'{id}.surrounding.json',dict(sources=sources,source=src.as_posix(),sha256=sha(src),baseWorldBox=[48128,15360,50176,18432]))

