from native_work import *
ident='r03_c13_cross_terrace_repair'
src=ZONE/'tiles/r03_c13.png';r=read(src.with_suffix('.png.derivation.json'));assert sha(src)==r['sha256'];im=Image.open(src)
box=[1421,2842,2675,4096];guide=ZONE/'guides'/f'{ident}.png';assert not guide.exists();im.crop(box).save(guide)
context=ZONE/'guides'/f'{ident}.context.png';im.crop((1024,2048,3072,4096)).save(context)
ox,oy=r['worldBox'][:2];p=[1536,2957]
d={'operation':'exact1254crop from registered current4K native assembly; no scaling or feathering','source':{'file':src.as_posix(),'sha256':sha(src),'derivationRecord':src.with_suffix('.png.derivation.json').as_posix()},'sourceCrop':box,'nativeWorldBox':[ox+box[0],oy+box[1],ox+box[2],oy+box[3]],'coreWorldBox':[ox+p[0],oy+p[1],ox+p[0]+1024,oy+p[1]+1024],'coreCrop':[115,115,1139,1139],'tileLocalPaste':p,'finalArt':False}
write(guide.with_suffix('.png.derivation.json'),d)
write(context.with_suffix('.png.derivation.json'),{'operation':'exact2048context crop, no scaling','source':d['source'],'sourceCrop':[1024,2048,3072,4096],'finalArt':False})
refs=[{'file':guide.as_posix(),'sha256':sha(guide),'role':'native edit target: entire interrupted terrace section and all four attachment edges','derivationRecord':guide.with_suffix('.png.derivation.json').as_posix()},{'file':context.as_posix(),'sha256':sha(context),'role':'unscaled2048square structural context only','derivationRecord':context.with_suffix('.png.derivation.json').as_posix()},*current_references()]
write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
resume=read(ZONE/'resume-ack-20261010.json');resume.update(latestContinuationAtUtc=now(),latestInstruction='User says only draw, no runtime/capacity testing; old AGENTS withdrawn',currentCoordinates=['r03_c13 full-terrace-joint repair','r03_c14 completion','r04_c12 production'],excludedCoordinates=['r01_c13','r01_c14','r02_c13','r02_c14'],exclusionAuthority='acceleration-20261010/assignments.json',nativeCountAtContinuation=len(list((ZONE/'native').glob('*.png'))));write(ZONE/'resume-ack-20261010.json',resume)
print(json.dumps({'guide':guide.as_posix(),'nativeWorldBox':d['nativeWorldBox']}))

