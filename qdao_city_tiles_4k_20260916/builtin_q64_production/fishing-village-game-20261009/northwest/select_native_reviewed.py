from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
tile,name,dirs,note=sys.argv[1:5];w=B/('work-'+tile);p=B/'native'/(name+'.png');sr,sc=[int(x[1:]) for x in name.split('_')[2:4]]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s={'file':str(p),'sha256':sha(p),'row':sr,'column':sc,'status':'selected-native-pending-full-tile-joins','visualQA':'qa/'+name+'/visual.json'}
(w/'selections'/f's{sr:02d}_s{sc:02d}.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
q={'native':s,'reviewedAt':datetime.now(timezone.utc).isoformat(),'qaScale':1,'nativeWholeReviewed':True,'cropsReviewed':[d+'-'+str(i) for d in dirs for i in [1,2]],'result':'pass-current-pair-overlaps','notes':[note],'formalAccepted':False}
(w/'qa'/name/'visual.json').write_text(json.dumps(q,indent=2),encoding='utf-8');print(json.dumps({'selected':name,'coordinateCount':len(list((w/'selections').glob('*.json')))}))
