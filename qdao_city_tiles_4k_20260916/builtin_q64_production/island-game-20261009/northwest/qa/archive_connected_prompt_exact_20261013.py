"""Preserve actual submitted prompt bytes in new evidence; retain initial records."""
from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1];stem='r06_c04_rail_east_foot_a01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rp=Z/'receipts'/f'{stem}.receipt.json';gp=Z/'native'/f'{stem}.png.generation.json'
r=json.loads(rp.read_text());g=json.loads(gp.read_text())
pp=Z/'prompts'/f'{stem}.submitted-exact.prompt.txt'
with pp.open('x',encoding='utf-8',newline='') as f:f.write(r['submitted']['promptText'])
assert pp.read_text()==r['submitted']['promptText']
r['submitted']['promptFile']=pp.as_posix()
r['supersedesPromptPathOnly']={'path':rp.as_posix(),'sha256':sha(rp),'reason':'Original saved prompt had an extra final newline; this version pins exact actually submitted text without changing the request.'}
rp2=Z/'receipts'/f'{stem}.receipt-v2.json'
with rp2.open('x',encoding='utf-8') as f:json.dump(r,f,indent=2)
g['prompt']=pp.as_posix();g['promptSha256']=sha(pp);g['evidence']['receipt']=rp2.as_posix()
g['evidenceCorrection']={'originalRecord':gp.as_posix(),'sha256':sha(gp),'change':'Pins the exact submitted prompt bytes and corresponding preserved receipt v2.'}
gp2=Z/'native'/f'{stem}.png.generation-evidence-v2.json'
with gp2.open('x',encoding='utf-8') as f:json.dump(g,f,indent=2)
print(json.dumps({'prompt':str(pp),'receipt':str(rp2),'generation':str(gp2)}))
