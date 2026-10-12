from pathlib import Path
from PIL import Image
import pipeline as p
d=p.read(p.ROOT/'delivery-20261011-v1/delivery-manifest.json')
assert d['candidateCount']==4 and d['coveredCoreCoordinates']==64 and d['formalAcceptedCount']==0
for t in d['tiles']:
 assert p.sha(t['candidate'])==t['sha256']==p.sha(t['sourceCandidate'])
 assert Image.open(t['candidate']).size==(4096,4096)
 assert p.sha(t['review'])==t['reviewSHA256']
 for r in t['supplementaryReviews']:assert p.sha(r['file'])==r['sha256']
 assert len(t['selectedNativeOrDerivedPatches'])==16
 assert not t['formalAccepted']
assert p.sha(d['overview']['file'])==p.sha(p.ROOT/'qa-final-fourway-v1/overview-preview-2048.png')
print('Verified: 4 byte-identical delivered 4096x4096 candidates; 64 selected source areas; current report hashes; preview source agreement; formalAccepted=0.')
