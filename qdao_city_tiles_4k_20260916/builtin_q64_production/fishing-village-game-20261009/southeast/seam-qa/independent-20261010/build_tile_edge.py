import sys,json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;BASE=HERE.parent.parent
sys.path.insert(0,str(BASE))
from review_external_seams import Sources,write_evidence
tile,edge=sys.argv[1:3];r,c=int(tile[1:3]),int(tile[5:7]);x,y=(c-1)*4096,(r-1)*4096
vertical=edge in ('east','west');seam=x+(4096 if edge=='east' else 0) if vertical else y+(4096 if edge=='south' else 0);start=y if vertical else x
folder=HERE/(tile+'-'+edge);folder.mkdir(exist_ok=True);s=Sources();records=[]
for i in range(4):
 lo=start+i*1024;hi=lo+1024;box=[seam-256,lo,seam+256,hi] if vertical else [lo,seam-256,hi,seam+256]
 records.append(write_evidence(s,folder,f'segment-{i+1}',box,{'seamGlobal':seam,'axis':'x' if vertical else 'y','seamInCrop':256}))
for i in range(1,4):
 cx,cy=(seam,start+i*1024) if vertical else (start+i*1024,seam)
 records.append(write_evidence(s,folder,f'cross-{i}',[cx-256,cy-256,cx+256,cy+256],{'intersectionGlobal':[cx,cy],'intersectionInCrop':[256,256]}))
(folder/'manifest.json').write_text(json.dumps({'tile':tile,'edge':edge,'records':records,'formalAccepted':False,'createdAtUtc':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
print(json.dumps({'folder':str(folder),'complete':sum(r['sourceComplete'] for r in records)}))
