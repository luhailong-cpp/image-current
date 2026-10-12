import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT));import production as p
f=ROOT/'prompts/r10_c04_s04_01_v01.request.json';r=p.load(f)
r['references'][1]=p.metadata(ROOT/'native/r10_c03_s04_04_v01.png','actual LEFT native roof context; TOP and RIGHT in target guide')
p.dump(f,r);print(json.dumps(r))

