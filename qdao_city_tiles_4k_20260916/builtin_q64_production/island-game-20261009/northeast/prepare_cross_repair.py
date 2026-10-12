from native_work import *
ids=[['r03_c12_p01_01','r03_c12_p01_02_v2','r03_c12_p01_03'],['r03_c12_p02_01_v2','r03_c12_p02_02_v2','r03_c12_p02_03'],['r03_c12_p03_01','r03_c12_p03_02','r03_c12_p03_03_v2']]
mosaic=Image.new('RGB',(3072,3072)); sources=[]
for r,row in enumerate(ids):
    for c,ident in enumerate(row):
        p=ZONE/'native'/f'{ident}.png'; mosaic.paste(Image.open(p).crop((115,115,1139,1139)),(c*1024,r*1024)); sources.append({'file':p.as_posix(),'sha256':sha(p),'generationRecord':p.with_suffix('.png.generation.json').as_posix(),'crop':[115,115,1139,1139],'paste':[c*1024,r*1024]})
mp=ZONE/'qa/r03_c12-three-quarter-native.png'; mosaic.save(mp)
preview=mosaic.copy(); preview.thumbnail((1536,1536)); preview.save(ZONE/'qa/r03_c12-three-quarter-preview.png')
ident='r03_c12_cross_02_02_repair'; box=[1421,1421,2675,2675]
dest=ZONE/'guides'/f'{ident}.png'; mosaic.crop(box).save(dest)
write(dest.with_suffix('.png.derivation.json'),{'operation':'exact unscaled source core assembly followed by native crop for joint geometry repair','sources':sources,'tileLocalBox':box,'nativeWorldBox':[45056+box[0],8192+box[1],45056+box[2],8192+box[3]],'coreWorldBox':[45056+1536,8192+1536,45056+2560,8192+2560],'coreCrop':[115,115,1139,1139],'finalArt':False})
refs=[{'file':dest.as_posix(),'sha256':sha(dest),'role':'edit target: exact four-way mosaic native crop, shared wall-base geometry repair across two lower cores','derivationRecord':dest.with_suffix('.png.derivation.json').as_posix()},*read(ZONE/'reference-audit.json')['references']]
write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
print(dest.as_posix())
