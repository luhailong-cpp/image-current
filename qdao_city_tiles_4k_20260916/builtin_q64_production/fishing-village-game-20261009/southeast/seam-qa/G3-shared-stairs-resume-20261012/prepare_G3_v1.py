"""Extract current selected native cores only; all writes local."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,importlib.util
from PIL import Image
D=Path(__file__).resolve().parent;BASE=D.parent.parent
FRAME=[36060,46592,37314,47846]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj):
    assert not p.exists(),p
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('native_core_sources',BASE/'review_external_seams.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
s=m.Sources()
image,pieces,missing=s.extract(FRAME);assert not missing,missing
assert image.size==(1254,1254)
guide=D/'G3-bottom-conditioned-v1-guide-native1254.png';assert not guide.exists();image.save(guide)
targetbox=[36317,47019,37179,47419]
local=[targetbox[0]-FRAME[0],targetbox[1]-FRAME[1],targetbox[2]-FRAME[0],targetbox[3]-FRAME[1]]
target=D/'G3-bottom-conditioned-v1-target-native.png';assert not target.exists();image.crop(local).save(target)
snapshot=[]
for tile,patch in [('r12_c09','p24'),('r12_c09','p34'),('r12_c10','p21'),('r12_c10','p31')]:
    source,error=s.source(tile,patch);assert not error,error
    snapshot.append(source)
provenance={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'guide':str(guide),'guideSha256':sha(guide),'nativeSize':[1254,1254],'frameWorld':FRAME,
 'sourcePieces':pieces,'nativePatchSources':snapshot,
 'target':str(target),'targetSha256':sha(target),'targetWorldBox':targetbox,'targetGuideBox':local,
 'G3HorizontalBoundaryWorldY':47219,'G3HorizontalBoundaryGuideY':47219-FRAME[1],
 'canonicalBoundaryWorldX':36864,'canonicalBoundaryGuideX':36864-FRAME[0],
 'selectionMutated':False,'resampling':False,'syntheticGeometry':False,'paidApiUsed':False}
save(D/'G3-bottom-conditioned-v1-guide-provenance.json',provenance)
print(json.dumps({'guide':str(guide),'target':str(target),'actualSourcePatches':[(p['tile'],p['patch']) for p in snapshot]}))
