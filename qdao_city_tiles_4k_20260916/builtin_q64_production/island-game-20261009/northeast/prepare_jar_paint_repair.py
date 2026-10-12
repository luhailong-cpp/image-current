from native_work import *
ident='r04_c12_cross_01_02_jar_paint_repair'
top=ZONE/'tiles/r03_c12.png';can=Image.new('RGB',(4096,8192));can.paste(Image.open(top),(0,0))
sources=[{'file':top.as_posix(),'sha256':sha(top),'sourceCrop':[0,0,4096,4096],'canvasPaste':[0,0],'derivationRecord':top.with_suffix('.png.derivation.json').as_posix()}]
sel=read(ZONE/'selection-r04_c12.json')
for r in range(2):
 for c in range(4):
  ident0=sel['cores'][r][c];assert ident0;p=ZONE/'native'/f'{ident0}.png';rec=read(p.with_suffix('.png.generation.json'));can.paste(Image.open(p).crop((115,115,1139,1139)),(c*1024,4096+r*1024));sources.append({'file':p.as_posix(),'sha256':sha(p),'sourceCrop':[115,115,1139,1139],'canvasPaste':[c*1024,4096+r*1024],'generationRecord':p.with_suffix('.png.generation.json').as_posix()})
guide=ZONE/'guides'/f'{ident}.png';assert not guide.exists();box=[1421,3981,2675,5235];can.crop(box).save(guide)
context=ZONE/'guides'/f'{ident}.context.png';can.crop((1024,3072,3072,5120)).save(context)
der={'operation':'exact native core composition with existing upper4K,1254 crop only, no resize or feather','sources':sources,'sourceCropInCanvas':box,'nativeWorldBox':[45056+1421,12288-115,45056+2675,12288+1139],'coreWorldBox':[45056+1536,12288,45056+2560,13312],'coreCrop':[115,115,1139,1139],'tileLocalPaste':[1536,0],'finalArt':False}
write(guide.with_suffix('.png.derivation.json'),der);write(context.with_suffix('.png.derivation.json'),{'operation':'exact2048 native context crop','sources':sources,'sourceCropInCanvas':[1024,3072,3072,5120],'finalArt':False})
refs=[{'file':guide.as_posix(),'sha256':sha(guide),'role':'native edit target, brown jar rectangular color band near upper middle; preserve all contours','derivationRecord':guide.with_suffix('.png.derivation.json').as_posix()},{'file':context.as_posix(),'sha256':sha(context),'role':'native registered context only','derivationRecord':context.with_suffix('.png.derivation.json').as_posix()},*current_references()]
write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
can.crop((0,3072,4096,6144)).save(ZONE/'qa'/f'{ident}.before-context.png')
print(json.dumps([r['file'] for r in refs]))

