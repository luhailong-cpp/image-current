from pathlib import Path
import json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
QA=ROOT/'qa'
a=Image.open(QA/'c04-bamboo-join-v02-r09_c04-candidate-4096.png')
b=Image.open(QA/'c04-wall-join-v01-r09_c04-candidate-4096.png')
boxes={'target':[450,415,770,790],'upper-right-perimeter':[700,380,900,650],
       'upper-wall-perimeter':[250,380,820,540],'lower-poster-perimeter':[250,1110,850,1290]}
for name,box in boxes.items():
    local=[box[j]+[423,1000][j%2] for j in range(4)]
    first,second=a.crop(local),b.crop(local)
    pair=Image.new('RGB',(first.width*2,first.height))
    pair.paste(first,(0,0));pair.paste(second,(first.width,0))
    pair.save(QA/('c04-wall-v01-'+name+'-base-left-candidate-right-100pct.png'))
b.crop((423,1000,1677,2254)).save(QA/'c04-wall-v01-candidate-patch-100pct.png')
mask=np.array(Image.open(QA/'c04-wall-join-v01-repair-local-selection-mask.png'))
assert not mask[172:,:213].any()
local=[423,1172,636,2254]
assert np.array_equal(np.array(a.crop(local)),np.array(b.crop(local)))
oldids=np.array(Image.open(QA/'c04-bamboo-join-v02-r09_c04-source-id-mask.png'))
newids=np.array(Image.open(QA/'c04-wall-join-v01-r09_c04-source-id-mask.png'))
assert np.array_equal(oldids==17,newids==17)
assert np.array_equal(oldids==18,newids==18)
proof={'protectedRepairBox':[0,172,213,1254],
       'protectedTileLocalBox':local,'protectedPixels':213*(1254-172),
       'protectedSelectionPixels':0,'protectedArtExactUnchanged':True,
       'boundarySource17SelectionExactUnchanged':True,'bambooSource18SelectionExactUnchanged':True}
(QA/'c04-wall-v01-protected-region-check.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof))
