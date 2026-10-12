from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,re
Z=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
ident=sys.argv[1]
if not ident.startswith('r04_c14_'):raise ValueError('scope')
now=datetime.now(timezone.utc).isoformat()
recpath=Z/'native'/f'{ident}.png.generation.json';rec=read(recpath)
rec.update(status='passed_native_and_adjacent_1to1_review',internalSeams='passed_existing_top_left_and_cross',reviewedAtUtc=now)
write(recpath,rec)
for prefix in sys.argv[2:]:
 p=Z/'qa'/f'{prefix}.json';d=read(p);d.update(status='passed_visual_review_candidate',reviewedAtUtc=now,review={'scale':'1:1','reviewer':'root/south_tile','finding':'Material strokes and contours continuous at exact core cut; no broken objects, blur strips or rectangular pasted boundary.'});write(p,d)
p=Z/'selection-r04_c14.json';s=read(p);m=re.search(r'_p(\d+)_(\d+)',ident);s['cores'][int(m[1])-1][int(m[2])-1]=ident;s['updatedAtUtc']=now;write(p,s)
receiptpath=Z/'receipts'/f'{ident}.tool.json';r=read(receiptpath);r['promptSha256']=hashlib.sha256(Path(rec['prompt']).read_bytes()).hexdigest();r['orderedReferences']=rec['references'];write(receiptpath,r)
print(ident,'selected')

