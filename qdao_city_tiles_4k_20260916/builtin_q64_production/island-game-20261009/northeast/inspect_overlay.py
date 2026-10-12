from native_work import *
import sys
ident=sys.argv[1]; p=ZONE/'native'/f'{ident}.png'; rec=read(p.with_suffix('.png.generation.json')); x=rec['coreWorldBox'][0]-45056; y=rec['coreWorldBox'][1]-8192
out=Image.open(ZONE/'tiles/r03_c12.png').convert('RGB'); out.paste(Image.open(p).crop(tuple(rec['coreCrop'])),(x,y))
for side,box in {'top':[x,y-128,x+1024,y+128],'bottom':[x,y+896,x+1024,y+1152],'left':[x-128,y,x+128,y+1024],'right':[x+896,y,x+1152,y+1024]}.items(): out.crop(tuple(box)).save(ZONE/'qa'/f'{ident}-{side}-100pct.png')
write(ZONE/'qa'/f'{ident}.overlay.json',{'operation':'exact native1024 repair core overlay; no feathering or scaling','source':p.as_posix(),'sha256':sha(p),'generationRecord':p.with_suffix('.png.generation.json').as_posix(),'coreCrop':rec['coreCrop'],'tileLocalPaste':[x,y],'worldPaste':rec['coreWorldBox'][:2],'review':'pending four-edge inspection'})
out.resize((1536,1536),Image.Resampling.LANCZOS).save(ZONE/'qa'/f'{ident}-preview.png')
print('Overlay candidate and 100% perimeter crops saved.')
