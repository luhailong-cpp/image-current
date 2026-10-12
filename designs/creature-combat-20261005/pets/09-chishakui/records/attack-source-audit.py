import json
from pathlib import Path
root=Path(r'D:/work/image/designs/creature-combat-20261005/pets/09-chishakui')
accepted=[]
for d,count in [('E',12),('W',8)]:
 for n in range(1,count+1):
  p=root/'runtime'/'attack'/d/f'{n:02}.png.generation.json'
  r=json.loads(p.read_text(encoding='utf-8'))
  accepted.append({'file':r['file'],'sha256':r['sha256'],'nativeSource':r['derivedFrom'],'receipt':r['evidence']['receipt'],'prompt':r['prompt']})
rejected=[]
for suffix,reason in [('01','left-hand hammer swap'),('02','camera reversed to other shoulder')]:
 p=root/'records'/f'attack-W-07-rejected{suffix}.generation.json'
 r=json.loads(p.read_text(encoding='utf-8'))
 r['disposition']='rejected; no longer present at former runtime output path'
 r['rejectionReason']=reason
 r['supersededBy']='runtime/attack/W/07.png.generation.json'
 r['formerOutputPath']=r['file']
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
 rejected.append({'historicalRecord':str(p.relative_to(root)).replace('\\','/'),'formerOutputSHA256':r['sha256'],'nativeSource':r['derivedFrom'],'receipt':r['evidence']['receipt'],'prompt':r['prompt'],'reason':reason,'replacedBy':'runtime/attack/W/07.png.generation.json'})
out={'scope':'attack E01..12 W01..08','accepted':accepted,'rejected':rejected,'failedNoOutput':['records/attack-W-05-attempt01.error.json'],'cleanup':'All accepted native sources and rejected native images may be deleted by root after final reference/preview verification. Preserve source/receipt/prompt/SHA text evidence. Do not delete original shared E/W identity or style references. No images deleted by this audit.'}
(root/'records'/'attack-source-chain.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(accepted)} accepted source chains; {len(rejected)} rejected source chains; one failed-with-no-output request recorded.')

