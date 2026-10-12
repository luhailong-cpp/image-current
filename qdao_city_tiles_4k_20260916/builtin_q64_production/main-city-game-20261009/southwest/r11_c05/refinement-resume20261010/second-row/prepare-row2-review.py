from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;F=D.parent;T=F.parent
for name in ['inputs','output','qa','prompts','receipts','native']:(D/name).mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGB'))
def saveim(p,a):Image.fromarray(a).save(p,optimize=True);return {'file':str(p),'sha256':sha(p),'pixels':[a.shape[1],a.shape[0]]}
source=T/'pipeline/output/a50210b57293e7dc/r11_c05.partial-p01_01-p02_04.context.png';base=arr(source)
row1=F/'output/v5/r11-p01.repaired.context.png';new=arr(row1);original_first=arr(T/'borders/r11-p01.original.context.png')
assert base.shape==(2278,4326,3);assert np.array_equal(base[:1024],original_first[:1024]);assert np.array_equal(new[1024:],original_first[1024:])
combined=base.copy();combined[:1024]=new[:1024];assert np.array_equal(combined[1024:],base[1024:])
outputs={'context':saveim(D/'output/first-row-v5-plus-original-second-row.context.png',combined),'core':saveim(D/'output/first-row-v5-plus-original-second-row.core.png',combined[115:2163,115:4211])}
core=combined[115:2163,115:4211]
saveim(D/'qa/second-row-full.png',core[1024:])
for x in (1024,2048,3072):saveim(D/'qa'/f'second-row-seam-x{x}.png',core[1024:,x-320:x+320])
saveim(D/'qa/row1-row2-join.png',core[800:1250])
record={'source':{'file':str(source),'sha256':sha(source)},'firstRowOverride':{'file':str(row1),'sha256':sha(row1),'contextBox':[0,0,4326,1024]},'sourceAssembly':{'file':str(source.parent/'assembly.json'),'sha256':sha(source.parent/'assembly.json')},'unchangedContextRowsFrom':1024,'outputs':outputs,'resampled':False,'sourceWorldContextBox':[16269,40845,20595,43123],'coreWorldBox':[16384,40960,20480,43008],'formalAccepted':False}
(D/'output/base-composition.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(record,indent=2))
