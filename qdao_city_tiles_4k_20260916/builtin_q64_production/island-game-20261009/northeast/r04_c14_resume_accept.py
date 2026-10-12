from pathlib import Path
import sys,json,hashlib,re
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
ident=sys.argv[1]
assert ident.startswith('r04_c14_')
now=datetime.now(timezone.utc).isoformat()
p=Z/'native'/f'{ident}.png.generation.json';d=read(p)
d.update(status='passed_native_and_adjacent_1to1_review',internalSeams='passed_existing_top_left_and_cross',reviewedAtUtc=now,reviewer='root/south_resume')
if ident=='r04_c14_p03_01':
 d['evidence']['fields']=['recovered_saved_output_path','saved_prompt','matching_exact_native_anchors']
 d['evidence']['recoveryNote']='Original tool response not available; recovered matching completed file from prior south_tile session.'
write(p,d)
for prefix in sys.argv[2:]:
 p=Z/'qa'/f'{prefix}.json';s=read(p);s.update(status='passed_visual_review_candidate',reviewedAtUtc=now,review={'scale':'1:1','reviewer':'root/south_resume','finding':'Native material strokes, object contours and foliage continuous across exact core cuts; no pasted straight color boundaries or blur.'});write(p,s)
p=Z/'selection-r04_c14.json';s=read(p);m=re.search(r'_p(\d+)_(\d+)',ident);s['cores'][int(m[1])-1][int(m[2])-1]=ident;s['updatedAtUtc']=now;write(p,s)
p=Z/'receipts'/f'{ident}.tool.json';r=read(p);r['promptSha256']=hashlib.sha256(Path(d['prompt']).read_bytes()).hexdigest();r['orderedReferences']=d['references'];write(p,r)
print(ident,'selected')

