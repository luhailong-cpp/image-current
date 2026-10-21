from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parent;Z=B.parents[1]
source=Z/'r05_c03/candidate/r05_c03-candidate-hard-80982c249bee.png';evidence=Z/'r06_c03/repair-batches/north-glaze-material-01/edit-target.png'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert sha(source)=='8705aba979d280b2e3e90767b54882b8d867027f1242de4a452a214db0a61053'
orig=Image.open(source).convert('RGB');ev=Image.open(evidence).convert('RGB')
crop=orig.crop((1900,3469,3154,4096));other=ev.crop((0,0,1254,627));identical=np.array_equal(np.array(crop),np.array(other));assert identical
crop.save(B/'evidence-upper-original-native.png');orig.crop((1900,3469,2196,4096)).save(B/'evidence-seam-native.png')
frame=orig.crop((1421,2842,2675,4096));frame.save(B/'edit-target.png')
(B/'derivation.json').write_text(json.dumps({'source':str(source),'sourceSha256':sha(source),'tileBox':[8192,16384,12288,20480],'targetTileCrop':[1421,2842,2675,4096],'worldBox':[9613,19226,10867,20480],'target':str(B/'edit-target.png'),'targetSha256':sha(B/'edit-target.png'),'size':[1254,1254],'internalSeamNativeX':627,'nativePixelScale':1,'resampled':False,'recolored':False,'newEvidence':str(evidence),'newEvidenceSha256':sha(evidence),'evidenceTopCrop':[0,0,1254,627],'originalFinalCrop':[1900,3469,3154,4096],'evidenceEqualsOriginalFinalPixels':identical},indent=2),encoding='utf-8')
(B/'reopened-current-status.json').write_text(json.dumps({'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r05_c03','status':'reopened_unpassed_internal_seam','sourceSha256':sha(source),'issue':'Gold ornament and teal roof courses have a vertical discontinuity at tile x2048 in lower segment. Newly exposed evidence is pixel-identical to prior final.','evidenceActuallyViewed':True,'evidencePixelIdentical':True,'currentDeliverability':'pending repair and reintegration QA','historicalArchives':'preserved unchanged; historical acceptance is not current pass','oldCandidateModified':False,'oldAcceptanceModified':False,'oldArchivesModified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print({'pixelIdentical':identical,'targetSha':sha(B/'edit-target.png')})

