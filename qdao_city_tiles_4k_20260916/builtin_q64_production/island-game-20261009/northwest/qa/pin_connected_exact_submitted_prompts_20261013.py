from pathlib import Path
import json,hashlib,copy
Z=Path(__file__).resolve().parents[1]
info=lambda p:dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
for stem in ('cross_r06_c03c04_rail_west_a01','cross_r05r06_c04_paving_north_a01'):
 oldr=Z/'receipts'/f'{stem}.receipt.json';oldg=Z/'native'/f'{stem}.png.generation.json'
 r=json.loads(oldr.read_text(encoding='utf8'));g=json.loads(oldg.read_text(encoding='utf8'))
 prompt=Z/'prompts'/f'{stem}.submitted.prompt.txt'
 with prompt.open('x',encoding='utf8',newline='') as f:f.write(r['submitted']['promptText'])
 newr=Z/'receipts'/f'{stem}.receipt-evidence-v2.json'
 r['submitted']['promptFile']=prompt.as_posix()
 r['evidenceCorrection']=dict(originalReceipt=info(oldr),reason='Pin the exact actually submitted prompt string, which omits the source prompt file final newline. The original receipt and prompt remain preserved; request text and generation are unchanged.')
 with newr.open('x',encoding='utf8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
 g['prompt']=prompt.as_posix();g['promptSha256']=info(prompt)['sha256'];g['evidence']['receipt']=newr.as_posix()
 g['evidenceCorrection']=dict(originalGenerationRecord=info(oldg),originalReceipt=info(oldr),reason=r['evidenceCorrection']['reason'])
 newg=Z/'native'/f'{stem}.png.generation-evidence-v2.json'
 with newg.open('x',encoding='utf8') as f:json.dump(g,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(stem=stem,exactPrompt=info(prompt),receipt=info(newr),generation=info(newg))))
