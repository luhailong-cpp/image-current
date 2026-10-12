from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(BASE/'manifest.json');review=read(BASE/'qa/visual-review-final.json')
assert manifest['summary']['completeTechnicalPass']
assert review['status']=='reviewed_and_accepted_for_art_delivery'
assert len(review['frames'])==68
assert all(sha(BASE/x['file'])==x['sha256'] for x in review['frames'])
previews=read(BASE/'previews/manifest.json')
assert len(previews)==12 and all(sha(BASE/x['file'])==x['sha256'] for x in previews)
assert all(sha(BASE/s['file'])==s['sha256'] for x in previews for s in x['sources'])
files=list((BASE/'qa').glob('edge-*.png'))+list((BASE/'provenance/attack').glob('static-review-*.png'))+list((BASE/'provenance/attack').glob('continuity-repair*.png'))
candidate=BASE/'provenance/cast/W/12-repair-candidate.png'
if candidate.exists():files.append(candidate)
records=[]
for p in files:
    resolved=p.resolve();assert resolved.is_relative_to(BASE.resolve())
    records.append({'file':p.relative_to(BASE).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'reason':'superseded by final post-registration contact sheets and playback review','deleted':True})
for p in files:p.unlink()
for p in [BASE/'provenance/cast/W/12.generation.json',BASE/'provenance/cast/W/12-repair-candidate.generation.json']:
    r=read(p)
    r['localCandidate']={'file':'provenance/cast/W/12-repair-candidate.png','sha256':'3a4fb1fc40fdf9851aadfc51e5d2cc22105715a3eb5ce016a016e5c97484ed54','retained':False,'cleanupRecord':'cleanup.json','reason':'final registered output verified'}
    p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
if (BASE/'cleanup.json').exists():records=read(BASE/'cleanup.json').get('deletedImages',[])+records
(BASE/'cleanup.json').write_text(json.dumps({'performedAt':datetime.now(timezone.utc).isoformat(),'scope':'this pet directory only','finalRuntimeFramesRetained':68,'historicalTextAndHashesRetained':True,'identityAndSharedStyleReferences':'untouched','externalBuiltinGenerationCache':'not manually modified by primary agent; outside exclusive task write directory','deletedImages':records},ensure_ascii=False,indent=2),encoding='utf8')
print('Removed',len(records),'superseded project preview images; kept textual evidence')
