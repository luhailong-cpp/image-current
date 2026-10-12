from pathlib import Path
from PIL import Image
from native_work import *
src=read(ZONE/'reference-audit.json')['references'][0]['file']
im=Image.open(src).crop((1110,205,1205,280))
p=ZONE/'qa'/'lantern-fixture-layout-study.png';im.resize((950,750),Image.Resampling.NEAREST).save(p)
write(p.with_suffix('.png.derivation.json'),{'source':src,'sha256':sha(src),'sourceCrop':[1110,205,1205,280],'operation':'10x nearest enlargement only for blurred-source structure inspection','finalArt':False})

