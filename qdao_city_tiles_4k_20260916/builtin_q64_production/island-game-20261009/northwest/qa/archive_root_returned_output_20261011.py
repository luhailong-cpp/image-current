from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1]
stem='r06_c03_s04_03_a01'
d=json.loads((Z/'qa/root-migration-recovery-receipt-input.json').read_text(encoding='utf-8'))
refs=json.loads((Z/'guides'/f'{stem}.references.json').read_text(encoding='utf-8-sig'))
d['submitted']['referenced_image_paths']=[r['path'] for r in refs]
d['submitted']['promptText']=(Z/'prompts'/f'{stem}.prompt.txt').read_text(encoding='utf-8').rstrip('\n')
d['recoveredSourceSha256']=hashlib.sha256(Path(d['generatedFile']).read_bytes()).hexdigest()
p=Z/'receipts'/f'{stem}.receipt.json'
if p.exists(): assert json.loads(p.read_text(encoding='utf-8'))['generatedFile']==d['generatedFile']
else: p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'receipt':p.as_posix(),'sourceSha256':d['recoveredSourceSha256']}))
