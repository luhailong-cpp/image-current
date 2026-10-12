from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
P=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/seam-qa/independent-20261010/r12_c08')
notes={'p24--p34':'Rock fissures, small leaves and shrub silhouette continue across horizontal core cut.','p31--p41':'Water caustics and small foam shapes continue across horizontal core cut without hard cutoff.','p33--p34':'Rounded boulder, cracks and shore foam continue across vertical core cut.','cross-r2-c3':'Four-way rock fissures and crevice plants remain continuous; mild warm/cool stone-tone difference only.'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for n,note in notes.items():
 p=P/(n+'.qa.json');r=json.loads(p.read_text());assert sha(r['image']['file'])==r['image']['sha256']
 for s in r['sources']:assert sha(s['file'])==s['sha256']
 r['visualReview']={'status':'reviewed_native_geometry_pass','reviewer':'seam_resume','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'structuralBlockers':[],'colorOnlyRisks':['Modest native material-tone variation; bounded color pending'] if n=='cross-r2-c3' else [],'candidateUsable':True,'formalAccepted':False,'observations':[note]}
 p.write_text(json.dumps(r,indent=2)+'\n')
m=json.loads((P/'manifest.json').read_text());records=[]
for item in m['results']:
 p=Path(item['report']);r=json.loads(p.read_text())
 item['visualReview']=r['visualReview']
 if r['sourceComplete'] and r['visualReview']['status'].startswith('reviewed'):
  records.append({'id':r['id'],'evidenceSha256':r['image']['sha256'],'status':r['visualReview']['status']})
(P/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
report={'tile':'r12_c08','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'partial_native_geometry_pass','selectedPositions':12,'reviewedSeams':16,'reviewedCrossings':5,'totalPlannedEvidence':33,'evidence':records,'formalAccepted':False,'internalReady':False,'remaining':'12 unavailable evidence items depend on missing selected p14,p42,p43,p44; p14-v2 remains unselected with independent G4/G5 structural issues outside rail-v4 narrow adoption.'}
(P/'partial-independent-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'reviewed':len(records),'seams':16,'crossings':5,'selectedPositions':12}))

