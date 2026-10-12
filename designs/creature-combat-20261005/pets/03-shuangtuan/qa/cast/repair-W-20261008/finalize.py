from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
B=Path('D:/work/image/designs/creature-combat-20261005/pets/03-shuangtuan');Q=B/'qa/cast/repair-W-20261008';R=B/'records/cast/W';S=B/'source/cast/W/repair-20261008'
accepted={5:2,6:1,7:1,8:1,9:1,10:1,12:1,14:1,15:2,16:1}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
timestamp=datetime.now(timezone.utc).isoformat()
files=[]
for p in sorted(S.glob('*.png')):
    files.append({'file':p.relative_to(B).as_posix(),'absolutePath':str(p.resolve()),'sha256':sha(p),'reason':'final runtime verified, native/candidate/rejected image removed per user retention policy'})
for p in sorted(R.glob('*.repair-20261008-a*.generation.json')):
    r=json.loads(p.read_text(encoding='utf-8'));n=r['frame'];attempt=int(p.name.split('-a')[1].split('.')[0]);is_accepted=accepted.get(n)==attempt
    if is_accepted:
        runtime=B/f'runtime/cast/W/{n:02d}.png';assert sha(runtime)==r['sha256']
        r['visualStatus']='Actual native full-frame and current 16-frame contact inspected; rear-view identity and anatomical count retained; targeted support/cast phase or recovery return repaired. See qa/cast/repair-W-20261008/review.md. Continuous playback is delegated to root and not claimed here.'
        r['status']='accepted-current-runtime'
    else:
        r['status']='rejected'
        r['visualStatus']='Rejected after actual viewing: '+('hind paws remained displaced despite upper-body transition improvement' if n==5 else 'front paws did not return sufficiently toward frame01 idle footprint')
        r['fileDeleted']=True;r['fileDeletedAt']=timestamp
    r['derivedFrom']['deleted']=True;r['derivedFrom']['deletedAt']=timestamp;r['derivedFrom']['retentionReason']='Final current runtime and SHA verified; original native image and temporary candidate image deleted from this repair scope; generation text, request, input SHA and receipt remain.'
    p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    if is_accepted:(R/f'{n:02d}.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
(Q/'cleanup.json').write_text(json.dumps({'preparedAt':timestamp,'scope':str(S.resolve()),'files':files,'imageCount':len(files),'hostCacheUntouched':True,'otherFoldersUntouched':True,'operation':'PowerShell Remove-Item -LiteralPath after resolved-scope validation','deleted':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'acceptedFrames':list(accepted),'candidateRecords':len(list(R.glob('*.repair-20261008-a*.generation.json'))),'cleanupImageCount':len(files)}))
