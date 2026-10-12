from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W))
from workflow import prepare,request
D=json.loads((W/'details.json').read_text(encoding='utf-8-sig'))
for pair in sys.argv[1:]:
 r,c=map(int,pair.split(','));k=f's{r:02d}_s{c:02d}';p=W/'prompts'/('detail-'+k+'.txt');p.write_text(D[k],encoding='utf-8');prepare(r,c,1);request(r,c,1,p)
