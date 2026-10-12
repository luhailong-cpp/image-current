from pathlib import Path
import json,sys
p=Path('D:/work/image/designs/creature-combat-20261005/pets/15-landuoxian/provenance/cast/E')
n=sys.argv[1]
for ext in ('prompt.txt','receipt.json','generation.json'):
    src=p/f'{n}.{ext}';dst=p/f'{n}.pre-chimefix.{ext}'
    if not dst.exists(): src.rename(dst)
native=p/'_inprogress'/f'{n}.png';dest=p/'_inprogress'/f'{n}.pre-chimefix.png'
if not dest.exists(): native.rename(dest)
j=json.loads((p/f'{n}.pre-chimefix.generation.json').read_text(encoding='utf8'))
j.update({'file':None,'retentionState':'superseded due to incorrect short right chime silhouette','prompt':str(p/f'{n}.pre-chimefix.prompt.txt')})
j['derivedFrom']['nativeFile']=str(dest);j['evidence']['receipt']=str(p/f'{n}.pre-chimefix.receipt.json');j['visualQA']['accepted']=False;j['visualQA']['rejectionReason']='Rightmost shortest flared chime morphed into elongated rectangle'
(p/f'{n}.pre-chimefix.generation.json').write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf8')
print(str(dest))
