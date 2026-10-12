from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parents[1];s='cross_r04r05_c03c04_lantern_body_a01'
old=Z/'native'/f'{s}.png.generation.json';data=json.loads(old.read_text(encoding='utf8'))
prompt=Z/'prompts'/f'{s}.prompt.txt';receipt=json.loads((Z/'receipts'/f'{s}.receipt.json').read_text(encoding='utf8'))
assert hashlib.sha256(prompt.read_bytes()).hexdigest()==data['promptSha256']
assert prompt.read_text(encoding='utf8')==receipt['submitted']['promptText']
assert Path(receipt['submitted']['promptFile']).resolve()==prompt.resolve()
data['prompt']=str(prompt.resolve())
data['generationEvidenceCorrection']=dict(originalRecord=dict(path=str(old),sha256=hashlib.sha256(old.read_bytes()).hexdigest()),reason='workflow ingest recorded a zone-relative prompt path; preserve old record and resolve the same exact submitted prompt file to its absolute path',imageBytesChanged=False,promptBytesChanged=False)
out=Z/'native'/f'{s}.png.generation-evidence-v2.json'
with out.open('x',encoding='utf8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
print(out)
