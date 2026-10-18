from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
import json,hashlib,os
T=Path(__file__).resolve().parent;Q=T/'qa'/'complete-20261013-v1';F=T/'qa'/'external-20261013-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
selp=T/'selected-patches.json';sel=read(selp);proof=read(Q/'independent-replay-proof.json');m=read(Q/'manifest.json')
assert len(sel['patches'])==16
for p in proof['records']:assert sha(p['native'])==p['sha256']
issues=[
 dict(id='water-density-horizontal',status='pending',severity='material_nonblocking_layout',location='internal horizontal joins y54272, y55296, y56320; strongest p31/p41, p32/p42, p33/p43',description='Small caustic loops and bright glints change density across some horizontal core joins. Geometry and water continuity remain valid, but uniform final water surface is not yet accepted.'),
 dict(id='water-density-vertical',status='pending',severity='material_nonblocking_layout',location='p12/p13 and some lower-row vertical joins',description='Local caustic scale and saturation transitions remain visible at native scale; preserve all current sources for later bounded polish.'),
 dict(id='external-west-material',status='pending',severity='material_nonblocking_layout',location='r14_c10/r14_c11 four segments plus y54272,y55296,y56320 crossings',description='No shoreline or object discontinuity; small water pattern/density differences remain. West material acceptance is pending.'),
 dict(id='external-north-east',status='pending_missing_sources',description='North r13_c11 and east r14_c12 lack selected neighboring cores in this snapshot; south is canvas boundary and needs no r15.')]
observations=[]
for ev in m['evidence']:
 name=Path(ev['file']).stem
 observations.append(dict(id=name,file=ev['file'],sha256=sha(ev['file']),review='geometry_checked_material_pending',reviewBasis='nine cross crops visually checked in exact unscaled row-major 1536 contact' if name.startswith('cross') else 'native quick edge viewed earlier; independent replay proved identical pixels and stable source hashes',structuralBlocker=False))
external_reused=[]
for i,pid in enumerate(['p11','p21','p31','p41'],1):
 a=F/f'west-segment-{i}-100pct.png';b=T/'qa'/f'quick-{pid}-v1'/'west.png'
 assert ImageChops.difference(Image.open(a).convert('RGB'),Image.open(b).convert('RGB')).getbbox() is None
 e=read(F/f'west-segment-{i}.qa.json')
 for p in e['sourcePixelSignature']:assert sha(p['file'])==p['sha256']
 external_reused.append(dict(file=str(a),prior=str(b),pixelIdentical=True,review='material_pending'))
review=dict(tile='r14_c11',createdAt=datetime.now(timezone.utc).isoformat(),status='complete_native_candidate_internal_material_pending',candidate=str(Q/'candidate-4096.png'),candidateSha256=proof['candidateSha256'],nativePatchCount=16,coreCount=16,actualModel=None,exactRawReplayProof=str(Q/'independent-replay-proof.json'),exactRawReplayProofSha256=sha(Q/'independent-replay-proof.json'),internalEvidenceCount=33,internalSeamsReused=24,internalCrossesVisuallyChecked=9,observations=observations,externalWestSegmentsReused=external_reused,externalWestCrossesVisuallyChecked=[str(F/f'intersection-x40960-y{y}-100pct.png') for y in (54272,55296,56320)],layoutReady=True,internalReady=False,formalAccepted=False,materialPending=True,pendingIssues=issues,policy='Preserve complete candidate; continue independent assigned missing tile. No material acceptance is claimed.')
rp=Q/'visual-review.json';assert not rp.exists();write(rp,review)
backup=T/'selected-patches.before-complete-20261013-v1.json';assert not backup.exists();backup.write_bytes(selp.read_bytes())
sel.update(status=review['status'],candidate=review['candidate'],candidateSha256=review['candidateSha256'],internalReady=False,formalAccepted=False,materialPending=True,internalReview=str(rp),pendingIssues=issues,updatedAt=review['createdAt'],nativeCoreCount=16)
temp=T/'selected-patches.complete-20261013.tmp.json';write(temp,sel);os.replace(temp,selp)
write(Q/'selection-metadata-transition.json',dict(before=str(backup),beforeSha256=sha(backup),after=str(selp),afterSha256=sha(selp),patchMappingUnchanged=read(backup)['patches']==sel['patches'],note='Metadata-only final review transition after raw replay; exact source hashes in replay remain current.'))
print(json.dumps(dict(tile='r14_c11',completeCandidates=1,internalReady=0,formalAccepted=0,selectedCores=16,review=str(rp),candidateSha256=review['candidateSha256'])))

