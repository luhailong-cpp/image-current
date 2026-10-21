import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
z=Path(__file__).resolve().parent.parent;repo=z.parents[3]
for rel,expected in [('AGENTS.md','57f1ad4f81fdb2256b843923d862308be228130917b99cfced375db256aff01a'),('docs/MAP_PARALLEL_SPLIT_20261013.json','a7cab49b89974586a1a0375baeadc5d4a7aa12dce6e782bcc8f9b52b777b3c8f')]:
 data=(repo/rel).read_bytes();assert hashlib.sha256(data).hexdigest()==expected,'Rules changed; reread'
r=json.loads((z/'native/r12_c05_p04_04_v1.request.json').read_text(encoding='utf-8-sig'))
r['stem']='r12_c05_p04_04_v2';r['references']=[{'path':(z/'native/r12_c05_p04_04_v1.png').as_posix(),'role':'edit target: remove added flowers and restore calm native continuity'},r['references'][0],*r['references'][1:4]]
r['revisionReason']='v1 introduced unrequested plants, changed top stone geometry and foam scale; restore original north band and calmer water before further propagation'
p=z/'native/r12_c05_p04_04_v2.request.json';assert not p.exists();p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(p)
