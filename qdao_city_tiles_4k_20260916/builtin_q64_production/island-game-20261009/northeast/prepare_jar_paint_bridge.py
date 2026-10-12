from native_work import *
ident='r04_c12_cross_01_02_jar_paint_repair_v2'
old=read(ZONE/'guides/r04_c12_cross_01_02_jar_paint_repair.png.derivation.json')
can=Image.new('RGB',(4096,8192))
for s in old['sources']:can.paste(Image.open(s['file']).crop(s['sourceCrop']),s['canvasPaste'])
guide=ZONE/'guides'/f'{ident}.png';assert not guide.exists();box=[1421,3725,2675,4979];can.crop(box).save(guide)
context=ZONE/'guides'/f'{ident}.context.png';can.crop((1024,3072,3072,5120)).save(context)
d={'operation':'exact crop across true4Ktile boundary, no scale or feather','sources':old['sources'],'sourceCropInCanvas':box,'nativeWorldBox':[45056+1421,12288-371,45056+2675,12288+883],'coreWorldBox':[45056+1536,12288-256,45056+2560,12288+768],'coreCrop':[115,115,1139,1139],'tileLocalPaste':[1536,-256],'finalArt':False}
write(guide.with_suffix('.png.derivation.json'),d);write(context.with_suffix('.png.derivation.json'),{'operation':'exact2048native context','sources':old['sources'],'sourceCropInCanvas':[1024,3072,3072,5120],'finalArt':False})
refs=[{'file':guide.as_posix(),'sha256':sha(guide),'role':'native exact edit target crossing actual4K boundary at imagey371','derivationRecord':guide.with_suffix('.png.derivation.json').as_posix()},{'file':context.as_posix(),'sha256':sha(context),'role':'native context only','derivationRecord':context.with_suffix('.png.derivation.json').as_posix()},*current_references()]
write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
q=read(ZONE/'qa/r04_c12_cross_01_02_jar_paint_repair.overlay.json');q.update(review='failed_top_attachment_color_band',notes='Do not select. Repair needs to straddle actual4K boundary instead of stopping there.');write(ZONE/'qa/r04_c12_cross_01_02_jar_paint_repair.overlay.json',q)
r=read(ZONE/'native/r04_c12_cross_01_02_jar_paint_repair.png.generation.json');r.update(status='rejected_attachment_color_band',internalSeams='failed_top');write(ZONE/'native/r04_c12_cross_01_02_jar_paint_repair.png.generation.json',r)
print(json.dumps([r['file'] for r in refs]))

