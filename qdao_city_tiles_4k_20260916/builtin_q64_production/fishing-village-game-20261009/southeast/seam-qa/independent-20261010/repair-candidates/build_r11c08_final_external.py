from pathlib import Path
import sys,json
from datetime import datetime,timezone
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast');sys.path.insert(0,str(Z))
from review_external_seams import Sources,write_evidence
P=Z/'seam-qa/independent-20261010/r11_c08-final-external'
P.mkdir(exist_ok=True);s=Sources();records=[];cross=set()
for edge,seam,start,axis in [('north',40960,28672,'y'),('east',32768,40960,'x')]:
 for i in range(4):
  p=start+i*1024;box=[p,seam-256,p+1024,seam+256] if axis=='y' else [seam-256,p,seam+256,p+1024]
  records.append(write_evidence(s,P,edge+'-segment-'+str(i+1),box,{'axis':axis,'coordinate':seam,'coordinateInImage':256}))
 for i in range(5):cross.add((start+i*1024,seam) if axis=='y' else (seam,start+i*1024))
for x,y in sorted(cross):
 records.append(write_evidence(s,P,f'intersection-x{x}-y{y}',[x-384,y-384,x+384,y+384],{'intersectionGlobal':[x,y],'intersectionInImage':[384,384]}))
(P/'manifest.json').write_text(json.dumps({'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r11_c08','candidateSha256':'140b429fd9b1397ccec721ee43e74ff3b05327c62facd890ee051e5cb6f4ff3d','records':records,'formalAccepted':False},indent=2)+'\n')
print(json.dumps({'complete':sum(r['sourceComplete'] for r in records),'pendingMissing':[r['id'] for r in records if not r['sourceComplete']],'newEvidence':[r['id'] for r in records if r['sourceComplete']]}))

