from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent.parent
notes={
 'r07_c04_s02_02_a01':{'top':'pass','right':'pass'},
 'r07_c04_s02_04_a02':{'top':'pass','left':'pass'},
 'r07_c04_s03_02_a01':{'top':'pending_local_repair'},
 'r07_c04_s03_04_a01':{'top':'pass'}
}
out=[]
for stem,status in notes.items():
 p=Z/'qa'/f'{stem}_quick_native_v1/index.json';d=json.loads(p.read_text())
 for item in d['items']:
  item['visualStatus']=status[item['direction']]
  item['reviewNote']='Viewed actual native join crop at 1:1: leaf contours, stone silhouette and broad grout geometry continue without a major boundary offset.' if item['visualStatus']=='pass' else 'Small carved flower contour and diagonal incised band discontinuity near local y256 in top native join; keep pending for full-tile repair. Local interior issue does not affect current southern continuation edge.'
 out.extend(d['items'])
record={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/right_continuation','rawNativeImagesViewed':list(notes),'items':out,'internalClosurePassed':False,'formalAccepted':False,'status':'quick_layout_and_adjacent_edge_review_only','noPixelEdits':True}
p=Z/'qa/right_wave_01_review_20261013.json'
with p.open('x',encoding='utf8') as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps({'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
