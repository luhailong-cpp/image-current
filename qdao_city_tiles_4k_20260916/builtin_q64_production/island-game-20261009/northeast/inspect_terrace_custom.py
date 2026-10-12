from native_work import *
ident='r03_c13_cross_terrace_repair'
g=read(ZONE/'guides'/f'{ident}.png.derivation.json')
src=ZONE/'native'/f'{ident}.png'
rec=read(src.with_suffix('.png.generation.json'))
base=Image.open(g['source']['file']).convert('RGB')
x,y=g['tileLocalPaste']; base.paste(Image.open(src).crop((115,115,1139,1139)),(x,y))
base.save(ZONE/'qa'/f'{ident}.candidate4k.png')
base.resize((1536,1536)).save(ZONE/'qa'/f'{ident}.preview.png')
edges={}
for name,b in {'top':(x,y-100,x+1024,y+100),'bottom':(x,y+924,x+1024,y+1124),'left':(x-100,y,x+100,y+1024),'right':(x+924,y,x+1124,y+1024)}.items():
 p=ZONE/'qa'/f'{ident}.edge-{name}.png';base.crop(b).save(p);edges[name]=p.as_posix()
q={'id':ident,'source':src.as_posix(),'sha256':sha(src),'generationRecord':src.with_suffix('.png.generation.json').as_posix(),'coreCrop':[115,115,1139,1139],'tileLocalPaste':[x,y],'coreWorldBox':rec['coreWorldBox'],'operation':'exact native1024 repair core overlay, no scaling, no feather','edges':edges,'review':'pending','sourceMosaic':g['source'],'actualModel':None,'actualQuality':None}
write(ZONE/'qa'/f'{ident}.overlay.json',q)
print(json.dumps(edges))

