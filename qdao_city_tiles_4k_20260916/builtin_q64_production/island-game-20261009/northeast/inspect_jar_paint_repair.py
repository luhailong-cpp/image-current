from native_work import *
ident='r04_c12_cross_01_02_jar_paint_repair';g=read(ZONE/'guides'/f'{ident}.png.derivation.json');can=Image.new('RGB',(4096,8192))
for s in g['sources']:can.paste(Image.open(s['file']).crop(s['sourceCrop']),s['canvasPaste'])
# Include already-passed neighboring jar foot overlay when inspecting contact edge.
other=read(ZONE/'qa/r04_c12_cross_01_03_jar_repair.overlay.json');can.paste(Image.open(other['source']).crop(other['coreCrop']),(other['tileLocalPaste'][0],4096+other['tileLocalPaste'][1]))
src=ZONE/'native'/f'{ident}.png';can.paste(Image.open(src).crop((115,115,1139,1139)),(1536,4096))
edges={}
for n,b in {'top':(1536,3996,2560,4196),'bottom':(1536,5020,2560,5220),'left':(1436,4096,1636,5120),'right':(2460,4096,2660,5120)}.items():
 p=ZONE/'qa'/f'{ident}.{n}-100pct.png';can.crop(b).save(p);edges[n]=p.as_posix()
can.crop((1024,3584,3072,5632)).save(ZONE/'qa'/f'{ident}.candidate-context.png')
q={'id':ident,'source':src.as_posix(),'sha256':sha(src),'generationRecord':src.with_suffix('.png.generation.json').as_posix(),'coreCrop':[115,115,1139,1139],'tileLocalPaste':[1536,0],'coreWorldBox':g['coreWorldBox'],'operation':'exact native1024 core overlay no resampling/feathering','review':'pending','edges':edges,'actualModel':None,'actualQuality':None}
write(ZONE/'qa'/f'{ident}.overlay.json',q);print(json.dumps(edges))

