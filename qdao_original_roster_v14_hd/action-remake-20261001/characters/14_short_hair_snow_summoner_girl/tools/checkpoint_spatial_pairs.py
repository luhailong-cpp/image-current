"""Keep pending review records truthful after latest clarified pair sequence."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'audit/final-visual-review.json';x=read(p)
x['status']='reopened_four_spatial_pairs_per_support_foot'
x['latestUserRequirement']=read(R/'audit/spatial-contact-requirement.json')
save(p,x)
p=R/'review.json';x=read(p)
for key,row in x.items():
 if key.startswith('run/') and row.get('visualStatus')!='passed':
  row['visualStatus']='pending_four_spatial_pairs_review'
  row['latestRequirement']='audit/spatial-contact-requirement.json'
save(p,x)
print('Latest clarified four-pair requirement recorded; no artwork marked passed.')
