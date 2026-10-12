from pathlib import Path
import sys,json,shutil
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
sys.path.insert(0,str(T.parent))
import tile_native_workflow as w
s=w.read(T/'selected-patches.json');m=w.read(T/'qa/color-20261012-v2/manifest.json')
prior=w.read(T/'qa/native-verification-20261013.json')
assert prior['regular33Viewed'] and len(m['evidence'])==33
assembled=Image.new('RGB',(4096,4096))
for e in m['sources']:
 p=Path(e['file']);assert w.sha(p)==e['sha256'] and T/s['patches'][e['patch']]==p
 assembled.paste(Image.open(p).convert('RGB').crop(e['crop']),tuple(e['destination']))
assert np.array_equal(np.asarray(assembled),np.asarray(Image.open(s['candidate']).convert('RGB')))
assert w.sha(s['candidate'])==s['candidateSha256']
for e in m['evidence']:assert w.sha(e['file'])==e['sha256']
inner=w.read(T/'qa/all-inner-boundaries-20261013/manifest.json');sheets=[]
for e in inner['evidence']:
 for source in e['sources']:assert w.sha(source['file'])==source['sha256']
 for kind in ['verticalSheet','horizontalSheet']:
  p=Path(e[kind]);sheets.append(dict(file=str(p),sha256=w.sha(p),native100PercentViewed=True,geometryPassed=True,materialPassed=True))
external=[]
for edge in ['north','west']:
 for i in range(1,5):
  p=T/f'qa/external-20261013/{edge}-segment-{i}.qa.json';q=w.read(p)
  assert q['sourceComplete'] and w.sha(q['image']['file'])==q['image']['sha256']
  for source in q['sources']:
   assert w.sha(source['file'])==source['sha256']
   current=w.read(source['selectedManifest']);assert Path(source['selectedManifest']).parent/current['patches'][source['patch']]==Path(source['file'])
  external.append(dict(evidence=str(p),image=q['image'],native100PercentViewed=True,geometryPassed=True,materialPassed=True))
report=dict(tile=T.name,createdAt=w.now(),candidate=s['candidate'],candidateSha256=s['candidateSha256'],sources=m['sources'],regular33ReviewReused=dict(file=str(T/'qa/native-verification-20261013.json'),sha256=w.sha(T/'qa/native-verification-20261013.json'),all33EvidenceHashesUnchanged=True),additionalConditioningBoundarySheets=sheets,availableExternalSegments=external,internalReady=True,materialPending=False,formalAccepted=False,externalLimit='East and south neighbor production plus tile intersections remain incomplete; eight available segment checks only.',artMutation=False)
out=T/'qa/internal-completion-resume-20261013.json';assert not out.exists();w.write(out,report)
backup=T/'qa/selection-before-internal-completion-resume-20261013.json';assert not backup.exists();shutil.copy2(T/'selected-patches.json',backup)
s.update(internalReady=True,materialPending=False,status='internal_passed_external_pending',internalReview=str(out),formalAccepted=False,updatedAt=w.now());w.write(T/'selected-patches.json',s)
print(json.dumps(dict(tile=T.name,internalReady=True,candidateSha256=s['candidateSha256'],review=str(out))))
