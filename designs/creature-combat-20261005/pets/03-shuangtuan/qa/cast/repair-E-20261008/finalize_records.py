from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
BASE=Path('D:/work/image/designs/creature-combat-20261005/pets/03-shuangtuan')
SRC=(BASE/'source/cast/E/repair-20261008').resolve()
REC=BASE/'records/cast/E';QA=BASE/'qa/cast/repair-E-20261008'
now=datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cleanup=[]
for p in sorted(SRC.glob('*.png')):
    resolved=p.resolve()
    assert resolved.parent==SRC
    cleanup.append({'file':p.relative_to(BASE).as_posix(),'absolutePath':str(resolved),'sha256':sha(p),'reason':'accepted derivative is in runtime; native/edit candidate or rejected candidate no longer needed'})
rejected={'05.repair-20261008-a1.generation.json':'Rejected: corrected far hind was added but wrong chest-ground paw remained, yielding five paws.', '13.repair-20261008-a1.generation.json':'Rejected: support anatomy corrected but unwanted frost effect carried into recovery frame.'}
for p in sorted(REC.glob('*.repair-20261008-a*.generation.json')):
    r=json.loads(p.read_text(encoding='utf-8'))
    if p.name in rejected:
        r['visualStatus']=rejected[p.name];r['accepted']=False
        r['fileDeletedAfterReview']=True
    else:
        r['accepted']=True
        r['visualInspection']='qa/cast/repair-E-20261008/review.md'
        r['visualStatus']='Full-frame and final 16-frame contact inspection completed; rear limb continuity repaired; live playback delegated to root, not claimed here.'
    r['sourceRetentionPolicy']='2026-09-23 user policy: keep runtime finals and textual provenance; delete native, rejected and intermediate images after export verification.'
    r['derivedFrom']['deleted']=True;r['derivedFrom']['deletedAt']=now;r['derivedFrom']['cleanupRecord']='qa/cast/repair-E-20261008/cleanup.json'
    for ref in r.get('references',[]):
        q=Path(ref['path'])
        if q.resolve().parent==SRC:
            ref.update({'deleted':True,'deletedAt':now,'cleanupRecord':'qa/cast/repair-E-20261008/cleanup.json'})
        elif '/runtime/cast/E/' in q.as_posix():
            if q.exists() and sha(q)!=ref['sha256']:
                ref['supersededAtPath']=True
                ref['historicalGenerationRecord']=f'records/cast/E/{q.stem}.before-repair-20261008.generation.json'
    p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    if r.get('accepted'):
        (REC/f"{r['frame']:02d}.generation.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
(QA/'cleanup.json').write_text(json.dumps({'recordedAt':now,'status':'deletion-planned-after-final-export-SHA-verified','files':cleanup,'scope':'Only source/cast/E/repair-20261008; external identity and style references untouched; host generated cache is outside this subtask write scope.'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sourcePngs':len(cleanup),'acceptedFrames':11,'rejectedAttempts':2}))
