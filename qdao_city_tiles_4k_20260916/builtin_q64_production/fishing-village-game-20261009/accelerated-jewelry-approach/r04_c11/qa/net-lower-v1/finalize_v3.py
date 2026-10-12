from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil,numpy as np
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach')
T=R/'r04_c11';D=T/'repairs/net-lower-v1';Q=T/'qa/net-lower-v1';P=T/'candidate/r04_c11-4096-candidate-v3.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not P.exists();shutil.copy2(Q/'candidate-v3-trial.png',P)
plan=read(D/'composite-plan.json');g=read(D/'native-result.generation.json')
g.update({'status':'selected_native_alpha_composite_passed_local_QA','contributesFinalPixels':True})
write(D/'native-result.generation.json',g)
base=Image.open(plan['baseCandidate']['file']).convert('RGB');out=Image.open(P).convert('RGB')
bottom={'baseRowRawRGBSha256':hashlib.sha256(base.crop((0,4095,4096,4096)).tobytes()).hexdigest(),'v3RowRawRGBSha256':hashlib.sha256(out.crop((0,4095,4096,4096)).tobytes()).hexdigest(),'changedXRangeInclusive':plan['bottomRowChangedXRangeInclusive'],'externalNeighborInspected':False}
review={'file':str(P),'sha256':sha(P),'status':'upper and lower net repairs pass local original-scale visual review','formalAccepted':False,'inspectionScale':'native 1:1','nativeRepairDimensions':[1254,1254],'evidence':['after-native-1254x1139.png','top-transition-native.png','left-fold-transition-native.png','right-mesh-transition-native.png','bottom-boundary-native.png'],
'findings':['Former abrupt vertical splice at tile x1139 has been replaced by a smoothly curving draped mesh fold.','Diamond cells and cord paths are continuous across the reconstructed strip.','No visibly doubled right-side strands or new hard mask boundary observed in native crop.','Top repaired gold rope, left gold hem loop and right wooden post retain their v2 placement and appearance.','Top transition preserves existing upper net; no rope modification or new severed end.'],
'invariants':{'unscaledSourcePixels':True,'alphaCompositeOnly':True,'nativeDimensions':[1254,1254],'sourceReferenceHaloBelowTileRows':[1139,1254],'haloContributedToFinalPixels':False,'actualChangedBox':plan['actualChangedBoxTile'],'upperPixelsBeforeTileY3287ByteIdentical':True,'rightPixelsX1594OnwardByteIdentical':True},
'externalBottomBoundary':bottom,'remainingRequirements':['Review the changed bottom edge against a future native tile below the assigned 2x2 area; no formal outer-boundary acceptance is granted.'],
'supersedes':'The lower-net defect and mixed-grid transition documented for net-joint-v2 are resolved in this v3 local review.',
'reviewedAt':datetime.now(timezone.utc).isoformat()}
write(Q/'findings.json',review)
manifest={'file':str(P),'sha256':sha(P),'dimensions':[4096,4096],'classification':'native alpha composite over verified 4096 core/repair candidate; not single-native4K generation','baseCandidate':plan['baseCandidate'],'baseCandidateManifest':rec(T/'candidate/r04_c11-4096-candidate-v2.manifest.json'),'nativeRepair':{**rec(D/'native-result.png'),'nativeDimensions':[1254,1254],'generationRecord':rec(D/'native-result.generation.json'),'actualModel':None,'actualQuality':None,'unknownReason':'Builtin tool receipt does not disclose verified model/quality.'},'target':plan['target'],'targetDerivation':plan['targetDerivation'],'prompt':rec(D/'prompt.txt'),'request':rec(D/'request.json'),'receipt':rec(D/'receipt.json'),'compositing':plan,'qa':rec(Q/'findings.json'),'nativePixelsResized':False,'externalBottomBoundaryChanged':True,'externalBottomBoundary':bottom,'externalSeamsChecked':False,'formalAccepted':False,'status':'local_rope_and_net_geometry_QA_passed_external_bottom_pending','createdAt':datetime.now(timezone.utc).isoformat()}
write(P.with_suffix('.manifest.json'),manifest)
preview=out.copy();preview.thumbnail((1024,1024));preview.save(Q/'candidate-v3-preview-only.png')
print(json.dumps({'candidate':str(P),'sha256':sha(P),'localQA':'pass','externalBottomChanged':bottom['changedXRangeInclusive']}))

