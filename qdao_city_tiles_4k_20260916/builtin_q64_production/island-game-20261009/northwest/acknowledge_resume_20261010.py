from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
Z=Path(__file__).resolve().parent;B=Z.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
release=B/'resume-production-20261010/production-resume.json';contract=Z.parent/'production-contract.json'
r=read(release);c=read(contract);assert r['newArtworkGenerationAllowed'] and c['newArtworkGenerationAllowed']
style=Path(c['primaryStyleReference']);assert sha(style)==c['primaryStyleSha256']
old=read(Z/'references.json');oldstyle=old[-1];new=list(old)
new[-1]=dict(path=style.as_posix(),role='primary user-provided approved Daoist Q painting style; no UI/characters/night lighting',sha256=sha(style),nativeSize=list(Image.open(style).size),previousReferenceForHistoricalRecordsOnly=oldstyle['path'],sourceAuthority=dict(path=release.as_posix(),sha256=sha(release)))
write(Z/'references.json',new)
now=datetime.now(timezone.utc).isoformat()
ack=dict(schemaVersion=1,resumed=True,resumedAtUtc=now,zone='northwest',release=dict(path=release.as_posix(),sha256=sha(release)),contract=dict(path=contract.as_posix(),sha256=sha(contract)),target4kCount=49,newImageGenerationAllowed=True,builtinOnly=True,paidApiAllowed=False,styleReference=new[-1],historicalGenerationEvidenceUnchanged=True,currentCoordinates=dict(completeNative4k='r03_c03',partiallyGenerated=['r03_c04','r04_c03','r03_c02'],nextMissing='r04_c04 when top/left anchors ready'),priorityNeighborhood=['r03_c03','r03_c04','r04_c03','r04_c04'],nextStep='Continue missing native coordinates and flagged local repairs, close same-coordinate shared boundaries and four-tile junction, then continue remaining49 zone tiles.',worldSizeApproved=False,capacity5000Validated=False,globalArtHoldReleased=True,runtimePendingBlocksArtwork=False,generatedNativeCount=len(list((Z/'native').glob('*.png'))),fullyCovered4kCount=1,internalPassed4kCount=1,externalPassed4kCount=0,formalAcceptedCount=0)
write(Z/'resume-ack-20261010.json',ack)
p=read(Z/'progress.json');p.update(status='resumed_native_production_connected_2x2',generationHold=False,resumeControl=release.as_posix(),resumeAck='resume-ack-20261010.json',nextStep=ack['nextStep'],updatedAtUtc=now,lastError=None,historicalReferenceAvailability='Old mail PNG remains absent. New calls use approved original mail JPG; old generation evidence unchanged.')
write(Z/'progress.json',p)
print(json.dumps(dict(resumed=True,newReference=style.as_posix(),nativeCount=ack['generatedNativeCount'])))
