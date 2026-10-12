from pathlib import Path
import json
from PIL import Image
from export_review_runtime import edge_counts
B=Path(__file__).resolve().parents[1]
m=json.loads((B/'preview/manifest-preview.json').read_text(encoding='utf-8'))
issues=[]
for s in m['slots']:
 f=s['selected'];p=B/'preview'/f['path']
 with Image.open(p) as im:
  out=im.resize((1024,1024),Image.Resampling.LANCZOS)
  edges=edge_counts(out)
  if any(edges.values()):issues.append({'slot':s['slot'],'source':f['key'],'outputEdges':edges})
(B/'review/export-edge-audit.json').write_text(json.dumps({'checked':196,'issues':issues},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checked':196,'issues':issues}))

