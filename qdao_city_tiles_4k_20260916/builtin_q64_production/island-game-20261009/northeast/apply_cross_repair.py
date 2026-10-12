from native_work import *
import numpy as np
ident='r03_c12_cross_02_02_repair'; p=ZONE/'native'/f'{ident}.png'
src=Image.open(ZONE/'qa/r03_c12-three-quarter-native.png').convert('RGB'); repair=Image.open(p).convert('RGB'); assert repair.size==(1254,1254)
src.paste(repair.crop((115,115,1139,1139)),(1536,1536)); dst=ZONE/'qa/r03_c12-three-quarter-repaired-native.png'; src.save(dst)
src.resize((1536,1536),Image.Resampling.LANCZOS).save(ZONE/'qa/r03_c12-three-quarter-repaired-preview.png')
for side,box in {'top':[1536,1408,2560,1664],'bottom':[1536,2432,2560,2688],'left':[1408,1536,1664,2560],'right':[2432,1536,2688,2560]}.items(): src.crop(box).save(ZONE/'qa'/f'{ident}-{side}-100pct.png')
write(ZONE/'qa'/f'{ident}.overlay.json',{'operation':'exact native1024 repair core overlay; no feathering or scaling','source':p.as_posix(),'sha256':sha(p),'generationRecord':p.with_suffix('.png.generation.json').as_posix(),'coreCrop':[115,115,1139,1139],'tileLocalPaste':[1536,1536],'worldPaste':[46592,9728],'repairGeometry':'continuous red wall base and foundation across four original core junction','review':'pending four-edge inspection','targetMosaic':dst.as_posix()})
print('Repair candidate and four100% perimeter crops saved')
