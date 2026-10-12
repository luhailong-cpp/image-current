"""Prepare exact unscaled four-core crossing for native local redraw."""
from native_work import *
import re,sys
tid=sys.argv[1]; row=int(sys.argv[2]); col=int(sys.argv[3]); ident=f'{tid}_cross_{row:02d}_{col:02d}_repair'
trow,tcol=map(int,re.fullmatch(r'r(\d{2})_c(\d{2})',tid).groups()); ox=(tcol-1)*4096;oy=(trow-1)*4096
sel=read(ZONE/f'selection-{tid}.json'); mosaic=Image.new('RGB',(2048,2048)); sources=[]
for dy in range(2):
 for dx in range(2):
  pid=sel['cores'][row-1+dy][col-1+dx];assert pid
  path=ZONE/'native'/f'{pid}.png';rec=read(path.with_suffix('.png.generation.json'));assert sha(path)==rec['sha256']
  mosaic.paste(Image.open(path).crop(tuple(rec['coreCrop'])),(dx*1024,dy*1024))
  sources.append({'file':path.as_posix(),'sha256':sha(path),'generationRecord':path.with_suffix('.png.generation.json').as_posix(),'coreCrop':rec['coreCrop'],'mosaicPaste':[dx*1024,dy*1024]})
guide=ZONE/'guides'/f'{ident}.png';assert not guide.exists();mosaic.crop((397,397,1651,1651)).save(guide)
context=ZONE/'guides'/f'{ident}.context.png';mosaic.save(context)
cx=ox+col*1024;cy=oy+row*1024
der={'operation':'exact four1024 native core assembly and1254crop around joint; no resizing or feathering','sources':sources,'nativeWorldBox':[cx-627,cy-627,cx+627,cy+627],'coreWorldBox':[cx-512,cy-512,cx+512,cy+512],'coreCrop':[115,115,1139,1139],'tileLocalPaste':[col*1024-512,row*1024-512],'mosaicCrop':[397,397,1651,1651],'finalArt':False}
write(guide.with_suffix('.png.derivation.json'),der);write(context.with_suffix('.png.derivation.json'),{'operation':'exact unscaled four1024 native core context mosaic','sources':sources,'finalArt':False})
refs=[{'file':guide.as_posix(),'sha256':sha(guide),'role':'native edit target with joint defect; preserve outer145 and all existing object positions','derivationRecord':guide.with_suffix('.png.derivation.json').as_posix()},{'file':context.as_posix(),'sha256':sha(context),'role':'unscaled surrounding native geometry context; not a new layout','derivationRecord':context.with_suffix('.png.derivation.json').as_posix()},*current_references()]
write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
print(json.dumps({'id':ident,'guide':guide.as_posix(),'tileLocalPaste':der['tileLocalPaste']}))

