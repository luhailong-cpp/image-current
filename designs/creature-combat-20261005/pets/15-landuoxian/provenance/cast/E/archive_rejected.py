from pathlib import Path
import json,sys
p=Path('D:/work/image/designs/creature-combat-20261005/pets/15-landuoxian/provenance/cast/E')
n=sys.argv[1];label=sys.argv[2];reason=sys.argv[3]
for ext in ('prompt.txt','receipt.json','generation.json'):
    (p/f'{n}.{ext}').rename(p/f'{n}.{label}.{ext}')
native=p/'_inprogress'/f'{n}.png';dest=p/'_inprogress'/f'{n}.{label}.png';native.rename(dest)
j=json.loads((p/f'{n}.{label}.generation.json').read_text(encoding='utf8'))
j.update({'file':None,'retentionState':'rejected; replacement pending','prompt':str(p/f'{n}.{label}.prompt.txt')})
j['derivedFrom']['nativeFile']=str(dest);j['evidence']['receipt']=str(p/f'{n}.{label}.receipt.json');j['visualQA']['accepted']=False;j['visualQA']['rejectionReason']=reason
(p/f'{n}.{label}.generation.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
print(str(dest))
