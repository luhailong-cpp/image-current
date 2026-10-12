from native_work import *
tile=Image.open(ZONE/'tiles/r03_c12.png').convert('RGB'); manifest=read(ZONE/'tiles/r03_c12.png.derivation.json')
for ident,x,y in [('r03_c12_cross_01_01_repair',512,512),('r03_c12_cross_01_02_repair',1536,512)]:
    box=[x-115,y-115,x+1139,y+1139]; dest=ZONE/'guides'/f'{ident}.png'; tile.crop(tuple(box)).save(dest)
    write(dest.with_suffix('.png.derivation.json'),{'operation':'exact native16-core assembled crop with prior recorded overlay; no resampling','sources':manifest['sources'],'priorOverlays':manifest['requiredOverlays'],'tileLocalBox':box,'nativeWorldBox':[45056+box[0],8192+box[1],45056+box[2],8192+box[3]],'coreWorldBox':[45056+x,8192+y,45056+x+1024,8192+y+1024],'coreCrop':[115,115,1139,1139],'finalArt':False})
    refs=[{'file':dest.as_posix(),'sha256':sha(dest),'role':'edit target: exact native assembled finishing crop','derivationRecord':dest.with_suffix('.png.derivation.json').as_posix()},*read(ZONE/'reference-audit.json')['references']]
    write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
print('Two joint finishing windows prepared at native scale.')
