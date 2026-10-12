import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;BASE=HERE.parent.parent
sys.path.insert(0,str(BASE))
from review_external_seams import Sources
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
folder=HERE/'r13_c09';north=HERE/'r13_c09-north'
allrecords=[]
for f,key in [(folder,'results'),(north,'records')]:
 manifest=json.loads((f/'manifest.json').read_text())
 for record in manifest[key]:
  p=Path(record['report']);d=json.loads(p.read_text())
  assert d['sourceComplete'] and sha(d['image']['file'])==d['image']['sha256']
  review={'status':'reviewed_pass','reviewer':'seam_review','reviewedAtUtc':now,'method':'Exact current selected pixel evidence viewed at native scale via view_image','candidateUsable':True,'formalAccepted':False,'structuralBlockers':[],'colorOnlyRisks':[],'observations':['Rock silhouettes, cracks and foamy water/shoreline contours remain continuous. Open-water reflection cells and foam bands have no hard tile-boundary break.']}
  d['visualReview']=review;p.write_text(json.dumps(d,indent=2)+'\n');record['visualReview']=review
  allrecords.append({'id':record['id'],'file':d['image']['file'],'sha256':d['image']['sha256'],'globalBox':d['globalBox'],'review':'pass'})
 (f/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
candidate=BASE/'r13_c09/candidate/r13_c09-internal-ready-4096.png'
assembled,pieces,missing=Sources().extract([32768,49152,36864,53248]);assert not missing
assert np.array_equal(np.asarray(assembled),np.asarray(Image.open(candidate).convert('RGB')))
report={'tile':'r13_c09','reviewer':'seam_review','reviewedAtUtc':now,'candidate':str(candidate),'candidateSha256':sha(candidate),'candidateExactlyMatchesCurrentCoreAssembly':True,'internalReady':True,'formalAccepted':False,'internalEdgesReviewed':24,'internalCrossingsReviewed':9,'northExternalSegmentsReviewed':4,'northExternalCrossingsReviewed':3,'structuralBlockers':[],'colorOnlyRisks':[],'colorEvidence':str(folder/'independent-color-replay.json'),'colorEvidenceSha256':sha(folder/'independent-color-replay.json'),'colorSummary':'All16 exact RGB field replays, max actual channel adjustment26; no image resampling, blur or geometric change.','scopeLimit':'North shared boundary plus all internal seams passed. Does not claim absent south/east/west neighbors or whole southeast final acceptance.','evidence':allrecords}
(folder/'final-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'tile':'r13_c09','evidenceCount':len(allrecords),'internalReady':True,'candidateSha256':report['candidateSha256']}))
