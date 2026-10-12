from pathlib import Path
import json,hashlib,shutil
b=Path(r'D:/work/image/designs/creature-combat-20261005/pets/03-shuangtuan')
s=b/'source/attack/repair-20261008';r=b/'records/attack/W/repair-20261008';s.mkdir(parents=True,exist_ok=True);r.mkdir(parents=True,exist_ok=True)
for n in ['10','11','12']:
 target=b/'runtime/attack/W'/f'{n}.png';before=s/f'W-{n}-before.png'
 if not before.exists():shutil.copy2(target,before)
 for kind in ['request','receipt','generation']:
  src=b/'records/attack/W'/f'{n}.{kind}.json';dst=r/f'{n}.previous.{kind}.json'
  if not dst.exists():shutil.copy2(src,dst)
 recp=r/f'{n}.previous.generation.json';rec=json.loads(recp.read_text(encoding='utf-8-sig'))
 rec['formerFile']=f'runtime/attack/W/{n}.png';rec['file']=before.relative_to(b).as_posix();rec['status']='superseded-pending-local-RH-repair'
 for ref in rec['references']:
  p=Path(ref['path'])
  if p.exists():ref['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  if p.name in ['10.png','11.png','12.png'] and str(p.parent).replace('\\','/').endswith('runtime/attack/W'):
   ref['historicalRuntimePath']=ref['path'];ref['path']=(s/f'W-{p.stem}-before.png').as_posix()
 rec['evidence']=[f'records/attack/W/repair-20261008/{n}.previous.receipt.json',f'records/attack/W/repair-20261008/{n}.previous.request.json']
 recp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'frame':n,'oldSha256':hashlib.sha256(before.read_bytes()).hexdigest(),'oldImageCopy':str(before)}))

