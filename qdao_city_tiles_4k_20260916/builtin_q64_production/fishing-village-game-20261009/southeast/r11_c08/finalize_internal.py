from pathlib import Path
from datetime import datetime,timezone
import json,shutil,hashlib
T=Path(__file__).resolve().parent;Z=T.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
snap=T/'selected-before-shadow-final.json'
if not snap.exists():shutil.copy2(T/'selected-patches.json',snap)
s=read(T/'joint-edge-color-v1-selected.json')
candidate=Path(s['candidate'])
dest=Z/'ready-for-edge-QA/r11_c08.png';dest.parent.mkdir(exist_ok=True);shutil.copy2(candidate,dest)
deriv=read(T/'qa/shadow-final/candidate-4096.png.derivation.json');deriv['file']=str(dest);deriv['sha256']=sha(dest);deriv['sourceCandidate']=str(candidate)
write(str(dest)+'.derivation.json',deriv)
review=dict(tile='r11_c08',reviewedAt=datetime.now(timezone.utc).isoformat(),internalReady=True,formalAccepted=False,
basis=['Root viewed all24 native seams and9crossings','Independent color-full geometry review 24+9, exact color field replay max18','S1/S2 original native AI repair rectangles reviewed, all8 final adoption edges viewed unscaled','Audit joint fields exact replay; cumulative delta18 from original native plus raw generated geometry regions'],
shadowRepairs=[dict(id='S1',box=[30605,41605,31135,42500],status='adopted; shadow softened obliquely through hull, original grain and plank geometry preserved'),dict(id='S2',box=[32520,42740,32768,43360],status='adopted; straight guide-strip shadow replaced with continuous cast shadow over stone')],
candidate=str(candidate),candidateSha256=sha(candidate),deliveryCandidate=str(dest),externalStatus='North/east pending final cross-tile review; north C2 belongs to r10c08 adoption shadow and remains open',maxColorDelta=18)
write(T/'qa/internal-review-final.json',review)
selection=dict(tile='r11_c08',patches=s['patches'],candidate=str(candidate),candidateSha256=sha(candidate),internalReady=True,formalAccepted=False,status='internal_ready_external_seams_pending',internalReview='qa/internal-review-final.json',updatedAt=review['reviewedAt'])
write(T/'selected-patches.json',selection)
print(json.dumps(dict(tile='r11_c08',candidate=str(dest),sha256=sha(dest),internalReady=True,formalAccepted=False)))

