from native_work import *
import sys
ident='r05_c14_cross_floor_tone_repair'; x,y=0,2700
src=ZONE/'native'/f'{ident}.png'; rec=read(src.with_suffix('.png.generation.json')); base=ZONE/'tiles/r05_c14.png'
out=Image.open(base).convert('RGB'); out.paste(Image.open(src).crop((115,115,1139,1139)),(x,y))
left=Image.open(ZONE/'tiles/r05_c13.png').convert('RGB')
for side,box in {'top':[x,y-128,x+1024,y+128],'bottom':[x,y+896,x+1024,y+1152],'right':[x+896,y,x+1152,y+1024]}.items():
    dest=ZONE/'qa'/f'{ident}-{side}-100pct.png'; assert not dest.exists(); out.crop(tuple(box)).save(dest)
joined=Image.new('RGB',(256,1024)); joined.paste(left.crop((3968,y,4096,y+1024)),(0,0)); joined.paste(out.crop((0,y,128,y+1024)),(128,0))
dest=ZONE/'qa'/f'{ident}-left-100pct.png'; assert not dest.exists(); joined.save(dest)
write(ZONE/'qa'/f'{ident}.overlay.json',{'operation':'exact1024 native core repair, no scaling/blending','source':src.as_posix(),'sha256':sha(src),'generationRecord':src.with_suffix('.png.generation.json').as_posix(),'coreCrop':[115,115,1139,1139],'tileLocalPaste':[x,y],'worldPaste':rec['coreWorldBox'][:2],'review':'pending native and four-edge inspection','baseFile':base.as_posix(),'baseSha256':sha(base)})

