from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
from datetime import datetime,timezone
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast')
OUT=Z/'seam-qa/independent-20261010'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=json.loads((Z/'r12_c10/qa/weststairs-v2-preview/manifest.json').read_text())
for item in manifest:
 assert sha(item['file'])==item['sha256']
 for s in item['sources']:assert sha(s['path'])==s['sha256']
for pid in ['p11','p21']:
 selected=Z/'r12_c10/processed'/f'{pid}-eaststairs-v3.png'
 preview=Z/'r12_c10/processed/weststairs-v2-preview'/f'{pid}-weststairs-v2-candidate.png'
 assert np.array_equal(np.asarray(Image.open(selected))[:,0:1139],np.asarray(Image.open(preview))[:,0:1139])
extras=[]
for n in ['bottom-cut-100pct','p14-p24-100pct','p24-p34-100pct']:
 p=Z/'r12_c09/processed/joint-stairs'/f'{n}.png';extras.append({'file':str(p),'sha256':sha(p)})
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'seam_resume independent','status':'native_geometry_pass_for_common_candidate','formalAccepted':False,'evidence':manifest+extras,'allEvidenceAndSourceHashesVerified':True,'c10CurrentSelectedWestPixelsEqualReviewedPreview':True,'findings':{'top':'Landing edges and tread joints continue across top adoption. No silhouette step seen.','left':'Wood post, stone rail sockets and step terminations are coherent at full native scale.','right':'All three riser silhouettes and tread seams align. Mild material/tone discontinuities remain for bounded color matching.','bottomLeft':'Board edges and grain remain continuous through adopted p34 strip and p24/p34 core boundary.','sharedCore':'The three stair risers and treads cross c09/c10 boundary without geometric jumps.','c09Internal':'p14/p24 and p24/p34 core seam previews show continuous native silhouettes.'},'remaining':['c09 provisional candidate has not yet been installed in selected-patches.json; owner must adopt same exact pixels before declaring this cross-tile edge solved','c10 full 16-patch tile not complete; full south edge and full tile QA remain','material color differences require bounded non-geometric color workflow'], 'c09ProvisionalSelection':str(Z/'r12_c09/processed/joint-stairs/provisional-selection.json')}
(OUT/'r12_c09-c10-weststairs-v2-independent.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'evidenceCount':len(report['evidence']),'sourceHashesVerified':True}))

