from native_work import *
ident='r03_c10_cross_native_material_repair';base=ZONE/'tiles/r03_c10-native-v1-20261012.png'
qa=ZONE/'qa'/f'{ident}-inspection';assert not qa.exists();qa.mkdir()
source=ZONE/'native'/f'{ident}.png';r=read(source.with_suffix('.png.generation.json'));assert sha(source)==r['sha256']
out=Image.open(base).convert('RGB');out.paste(Image.open(source).crop((115,115,1139,1139)),(2560,1024))
composite=qa/'local-composite-native.png';out.save(composite)
boxes={'center':[2560,1024,3584,2048],'left':[2432,1024,2688,2048],'right':[3456,1024,3712,2048],'top':[2560,896,3584,1152],'bottom':[2560,1920,3584,2176],'upper-left':[2304,768,2816,1280],'upper-right':[3328,768,3840,1280],'lower-left':[2304,1792,2816,2304],'lower-right':[3328,1792,3840,2304]}
entries=[]
for name,box in boxes.items():
 p=qa/f'{name}-100pct.png';out.crop(tuple(box)).save(p);entries.append({'file':p.as_posix(),'sha256':sha(p),'sourceCrop':box,'inspectionScale':1,'resized':False,'status':'pending_visual_review'})
write(qa/'inspection.json',{'id':ident,'source':source.as_posix(),'sha256':sha(source),'base':base.as_posix(),'baseSha256':sha(base),'operation':'exact1024 native crop paste without resize, blend or feather','tileLocalPaste':[2560,1024],'coreCrop':[115,115,1139,1139],'inspectionImages':entries,'status':'pending_visual_review','formalAccepted':False})
print(json.dumps({'qa':qa.as_posix(),'inspectionCount':len(entries)}))
