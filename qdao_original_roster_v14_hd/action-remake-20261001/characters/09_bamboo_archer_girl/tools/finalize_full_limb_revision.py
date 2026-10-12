from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
baseline=read(ROOT/'audit/full-limb-revision-before.json')
before={r['file']:r['sha256'] for r in baseline['beforeFrames']}
manual=read(ROOT/'audit/full-limb-root-repair-review.json')
inspected={r['slot']:r for r in manual['frames']}
assert set(inspected)=={'run/NE/11','run/NW/15','run/W/04','run/W/14','run/S/08','run/SE/08'}
reports=['audit/full-limb-run-N-NE-E-NW-review.json','audit/full-limb-run-S-SE-SW-W-review.json','audit/full-limb-combat-E-review.json','audit/full-limb-combat-W-review.json']
reviewed={}
for rel in reports:
 for r in read(ROOT/rel)['frames']:
  file=r['file'];digest=r.get('reviewedSha256') or r.get('beforeSha256') or r.get('sha256')
  assert before[file]==digest,(rel,file,'baseline mismatch')
  assert file not in reviewed,file
  reviewed[file]=rel
assert set(reviewed)==set(before) and len(reviewed)==196
current=[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted((ROOT/'runtime').rglob('*.png'))]
assert len(current)==196
changed=[r for r in current if r['sha256']!=before[r['file']]]
assert {r['file'][8:-4] for r in changed}==set(inspected)
for r in changed:
 m=inspected[r['file'][8:-4]]
 assert m['beforeSha256']==before[r['file']] and m['sha256']==r['sha256']
 assert m['staticCorrectionReviewed'] is True and m['dynamicVisualAcceptance'] is False
dirs=['N','NE','E','SE','S','SW','W','NW']
archive=ROOT/'audit/full-limb-pre-repair-paired-reviews.json'
if not archive.exists():
 write(archive,{'archivedAtUtc':now,'historicalOnly':True,'reviews':{d:read(ROOT/f'audit/run-{d}-paired-ground-review.json') for d in dirs}})
for direction in dirs:
 p=ROOT/f'audit/run-{direction}-paired-ground-review.json';d=read(p)
 for row in d['frames']:
  n=int(row.get('frame') or row['slot'].split('/')[-1])
  slot=f'run/{direction}/{n:02d}';file=f'runtime/{slot}.png'
  digest=sha(ROOT/file)
  limb={'beforeReview':reviewed[file],'beforeSha256':before[file],'retained':slot not in inspected,'dynamicVisualAcceptance':False}
  if slot in inspected:
   m=inspected[slot]
   assert row['sha256'] in [before[file],digest],slot
   row['sha256']=digest
   limb.update({'repairReview':'audit/full-limb-root-repair-review.json','confirmedIssue':m['confirmedIssue'],'afterEvidence':m['afterEvidence'],'staticCorrectionReviewed':True,'footPoseRetention':'Legs and boot axes visually rechecked after arm repair; prior foot observation retained, not a claim of identical pixels.'})
  else:assert row['sha256']==digest,slot
  row['fullLimbInspection']=limb
 d['latestFullLimbRevision']={'reviewedAtUtc':now,'currentRepairReview':'audit/full-limb-root-repair-review.json','repairSlots':[s for s in sorted(inspected) if s.startswith(f'run/{direction}/')],'dynamicVisualAcceptance':False}
 if direction=='NW':
  d['fullSupportChainReview']={'file':'audit/NW-full-support-chain-review.json','sha256':sha(ROOT/'audit/NW-full-support-chain-review.json'),'conclusion':'Visible thigh/knee/boot overlap supports continuity; screen-side changes do not establish a support-leg swap. Hip roots remain occluded; full anatomical identity is not confirmed. Legs retained; NW15 arm-only repair visually rechecked.'}
  if 'sameAnatomicalFootConfirmed' in d:d['historicalSameAnatomicalFootConfirmed']=d['sameAnatomicalFootConfirmed']
  d['sameAnatomicalFootConfirmed']=False
 write(p,d)
rows=[]
for r in current:
 slot=r['file'][8:-4]
 rows.append({**r,'slot':slot,'beforeSha256':before[r['file']],'beforeReview':reviewed[r['file']],'retained':slot not in inspected,'repair':inspected.get(slot)})
timing=read(ROOT/'animation-timing.json')['run']
write(ROOT/'audit/full-limb-current-closeout.json',{'completedAtUtc':now,'scope':'All 196 current frames, shoulders/elbows/wrists/grips and hips/knees/ankles/boot orientation','beforeSnapshot':'audit/full-limb-revision-before.json','reviewedRuntimeFrames':196,'reviewedRunFrames':128,'reviewedBattleFrames':68,'totalRuntimeFrames':196,'changedFrames':[inspected[s] for s in sorted(inspected)],'retainedFrames':196-len(changed),'battleFramesUnchanged':all(r['sha256']==before[r['file']] for r in current if not r['file'].startswith('runtime/run/')),'timing':timing,'dynamicVisualAcceptance':False,'clientIntegration':'not_integrated','reviews':[{'file':p,'sha256':sha(ROOT/p)} for p in reports],'NWFullSupportChainReview':{'file':'audit/NW-full-support-chain-review.json','sha256':sha(ROOT/'audit/NW-full-support-chain-review.json')},'remainingLimits':['Real-time browser and game-engine grounding/displacement acceptance not verified','E/W/NW hip roots have occlusion; screen-side labels do not prove full anatomical leg identity'],'frames':rows})
print(json.dumps({'changedFrames':len(changed),'retainedFrames':196-len(changed),'reviewedRuntimeFrames':len(reviewed),'dynamicVisualAcceptance':False}))
