from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
b=Path(__file__).resolve().parents[1];q=b/'extension-20261011/geometry/north-seams/new-core-seams'
notes={
'r05-cross-tile-r2-native.png':('PASS','Actual center seam is continuous across pillar foot, paving and lantern crossbar; faint old guide texture boundary offset115px was flagged for broader halo review.'),
'r05_c11-h-p24-p34-native.png':('PASS','Red lantern body, gold foot, tassels, wood and plaster continue.'),
'r05_c11-v-p33-p34-native.png':('PASS','Main wood post, stone plinth and paving geometry continuous.'),
'r05_c11-h-p22-p32-native.png':('PASS','Blue net and timber continue at row join.'),
'r05_c11-h-p23-p33-native.png':('PASS','Net, warm timber and plaster continue at row join.'),
'r05_c11-v-p32-p33-native.png':('REPAIR_REVIEW_REQUIRED','Straight vertical tonal edge at strip x140, approx tile x1932, offset from actual core boundary. Ground shadow and stone texture change. Assigned owner for candidate halo review.')}
items=[{'file':str(q/f),'sha256':hashlib.sha256((q/f).read_bytes()).hexdigest(),'status':s,'note':n,'viewedNative':True} for f,(s,n) in notes.items()]
(b/'extension-20261011/root-incremental-review-2.json').write_text(json.dumps({'reviewedAt':datetime.now(timezone.utc).isoformat(),'stage':'selected cores before final repairs','items':items,'formalAccepted':False},indent=2)+'\n',encoding='utf-8')
print('Saved six actual native reviews')

