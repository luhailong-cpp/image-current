import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent.parent))
from review_external_seams import Sources,write_evidence
folder=HERE/'east-deck-focus';folder.mkdir(exist_ok=True)
s=Sources();records=[]
for name,b in {'orphan-seam-focus':[32512,38580,33100,38870],'full-joint-input':[32200,38150,33454,39404]}.items():
 records.append(write_evidence(s,folder,name,b,{'actualTileEdgeGlobalX':32768}))
(folder/'manifest.json').write_text(json.dumps({'results':records},indent=2)+'\n')
