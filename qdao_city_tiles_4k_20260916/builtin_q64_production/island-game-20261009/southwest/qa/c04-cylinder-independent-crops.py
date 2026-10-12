from pathlib import Path
import json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
QA=ROOT/'qa'
a=Image.open(QA/'c04-wall-join-v02-r09_c04-candidate-4096.png')
b=Image.open(QA/'c04-cylinder-join-v01-r09_c04-candidate-4096.png')
boxes={'target':[340,460,660,820],'ground-join':[410,630,940,930],
       'top-corner':[290,300,890,530],'lower-boundary':[280,770,860,950]}
for name,box in boxes.items():
    local=[box[j]+[1950,2440][j%2] for j in range(4)]
    first,second=a.crop(local),b.crop(local)
    pair=Image.new('RGB',(first.width*2,first.height))
    pair.paste(first,(0,0));pair.paste(second,(first.width,0))
    pair.save(QA/('c04-cylinder-v01-'+name+'-base-left-candidate-right-100pct.png'))
b.crop((1950,2440,3204,3694)).save(QA/'c04-cylinder-v01-candidate-patch-100pct.png')
oldids=np.array(Image.open(QA/'c04-wall-join-v02-r09_c04-source-id-mask.png'))
newids=np.array(Image.open(QA/'c04-cylinder-join-v01-r09_c04-source-id-mask.png'))
aa,bb=np.array(a),np.array(b)
proof={}
for sid, name in ((17,'boundary'),(18,'bamboo'),(19,'wall')):
    select=oldids==sid
    assert np.array_equal(select,newids==sid)
    assert np.array_equal(aa[select],bb[select])
    proof[name]={'sourceId':sid,'pixelCount':int(select.sum()),'selectionExactUnchanged':True,'artExactUnchanged':True}
(QA/'c04-cylinder-v01-prior-repairs-preserved.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof))
