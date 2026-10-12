from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
import local_repairs
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
A=B/'r12_c06/repairs-resume-20261012/V3-roof-rim-v01/integrated/assembly.json';a=read(A);ctx=a['contextOutput'];core=a['output']
for e in [ctx,core]:assert sha(e['file'])==e['sha256']
out=np.array(Image.open(ctx['file']).convert('RGB'));assert np.array_equal(out[115:4211,115:4211],np.array(Image.open(core['file']).convert('RGB')))
step=a['localNativeRepairs'][-1];g=read(step['generationRecord']);assert sha(step['generationRecord'])==step['generationRecordSha256']
assert sha(g['file'])==g['sha256']==sha(g['sourceOutputPath']) and sha(g['evidence']['toolReceipt'])==g['evidence']['toolReceiptSha256']
assert sha(g['inputContext'])==g['inputContextSha256']
base=np.array(Image.open(g['inputContext']).convert('RGB'));native=np.array(Image.open(g['file']).convert('RGB'));l,t,r,b=g['contextBox']
mixed,details=local_repairs.quilt(base[t:b,l:r],native,2);base[t:b,l:r]=mixed
assert np.array_equal(base,out) and details['alphaSha256Uint8RowMajor']==step['quilting']['alphaSha256Uint8RowMajor']
rp=A.parent/'root-full-review.json';report=read(rp);report.update(provenanceVerified=True,compositionReproducedExactly=True,sourceResampling=False,maximumFeatherRadiusPixels=2);atomic_json(rp,report)
cat=read(B/'current-candidates.json');cat['tiles']['r12_c06']={'tile':'r12_c06','source':'current-native-provisional-with-open-QA','assembly':str(A),'candidate':core,'context':ctx,'formalAccepted':False,'internalPassed':False,'review':str(rp)}
cat.update(updatedAtUtc=datetime.now(timezone.utc).isoformat(),complete4kCandidateCount=len(cat['tiles']),formalAcceptedCount=0);atomic_json(B/'current-candidates.json',cat)
print(json.dumps({'provisionalCatalogTiles':len(cat['tiles']),'formalAccepted':False,'compositionVerified':True}))
