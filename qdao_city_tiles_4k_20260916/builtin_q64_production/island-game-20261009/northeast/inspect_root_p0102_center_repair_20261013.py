from native_work import *
ident='r03_c09_cross_p0102_right_repair';guide=ZONE/'guides'/f'{ident}.png';d=read(guide.with_suffix('.png.derivation.json'));src=ZONE/'native'/f'{ident}.png';n=read(src.with_suffix('.png.generation.json'))
assert sha(src)==n['sha256']
qa=ZONE/'qa'/f'{ident}-inspection';assert not qa.exists();qa.mkdir()
out=Image.open(guide).convert('RGB');out.paste(Image.open(src).crop((115,115,1139,1139)),(115,115));out.save(qa/'local-composite-native.png')
boxes={'left':[0,115,230,1139],'right':[1024,115,1254,1139],'top-halo-context':[115,0,1139,230],'bottom-halo-context':[115,1024,1139,1254],'upper-left':[0,0,371,371],'upper-right':[883,0,1254,371],'lower-left':[0,883,371,1254],'lower-right':[883,883,1254,1254]}
entries=[]
for name,box in boxes.items():
 p=qa/f'{name}-100pct.png';out.crop(tuple(box)).save(p);entries.append({'file':str(p),'sha256':sha(p),'crop':box,'inspectionScale':1,'status':'pending_visual_review'})
write(qa/'inspection.json',{'id':ident,'source':str(src),'sha256':sha(src),'guide':str(guide),'guideSha256':sha(guide),'coreCrop':[115,115,1139,1139],'tileLocalPaste':[1536,0],'inspectionImages':entries,'status':'pending_visual_review','scope':'Native overlay crop against exact source canvas; top/bottom halo context is not adjacent full-tile acceptance','formalAccepted':False})
print(str(qa))

