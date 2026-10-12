from native_work import *
ident='r04_c12_cross_01_02_jar_paint_repair_v2';g=read(ZONE/'guides'/f'{ident}.png.derivation.json');can=Image.new('RGB',(4096,8192))
for s in g['sources']:can.paste(Image.open(s['file']).crop(s['sourceCrop']),s['canvasPaste'])
other=read(ZONE/'qa/r04_c12_cross_01_03_jar_repair.overlay.json');can.paste(Image.open(other['source']).crop(other['coreCrop']),(other['tileLocalPaste'][0],4096+other['tileLocalPaste'][1]))
src=ZONE/'native'/f'{ident}.png';can.paste(Image.open(src).crop((115,115,1139,1139)),(1536,3840))
edges={}
for n,b in {'top':(1536,3740,2560,3940),'bottom':(1536,4764,2560,4964),'left':(1436,3840,1636,4864),'right':(2460,3840,2660,4864),'actual-tile-boundary':(1536,3996,2560,4196)}.items():
 p=ZONE/'qa'/f'{ident}.{n}-100pct.png';can.crop(b).save(p);edges[n]=p.as_posix()
can.crop((1024,3328,3072,5376)).save(ZONE/'qa'/f'{ident}.candidate-context.png')
base={'source':src.as_posix(),'sha256':sha(src),'generationRecord':src.with_suffix('.png.generation.json').as_posix(),'nativeCoreCrop':[115,115,1139,1139],'operation':'two exact rectangular subcrops partition the same1024native repair core across an existing4K boundary, no scale or feather','review':'pending','edges':edges,'pairedRepair':ident,'actualModel':None,'actualQuality':None}
lo={**base,'id':ident,'coreCrop':[115,371,1139,1139],'tileLocalPaste':[1536,0],'coreWorldBox':[46592,12288,47616,13056],'pairedOverlay':'r03_c12_cross_04_02_jar_paint_bridge'}
up={**base,'id':'r03_c12_cross_04_02_jar_paint_bridge','coreCrop':[115,115,1139,371],'tileLocalPaste':[1536,3840],'coreWorldBox':[46592,12032,47616,12288],'pairedOverlay':ident}
write(ZONE/'qa'/f'{ident}.overlay.json',lo);write(ZONE/'qa/r03_c12_cross_04_02_jar_paint_bridge.overlay.json',up)
print(json.dumps({'sha256':sha(src),'edges':edges}))

