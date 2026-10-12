from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
before_doc=read(ROOT/'audit/video-axis-revision-before.json')
before={r['file']:r['sha256'] for r in before_doc['beforeFrames']}
manual=read(ROOT/'audit/video-axis-root-repair-review.json')
inspected={r['slot']:r for r in manual['frames']}
assert set(inspected)=={'run/N/12','run/SW/03','run/SW/11','run/SW/12','run/W/07'}
all_current=[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted((ROOT/'runtime').rglob('*.png'))]
assert len(all_current)==196
changed=[r for r in all_current if r['sha256']!=before[r['file']]]
assert {r['file'][8:-4] for r in changed}==set(inspected)
for r in changed:
 slot=r['file'][8:-4];m=inspected[slot]
 assert m['beforeSha256']==before[r['file']] and m['sha256']==r['sha256'],slot
 assert m['staticCorrectionReviewed'] is True and m['dynamicVisualAcceptance'] is False
files={'E':'audit/video-axis-E-NE-N-review.json','NE':'audit/video-axis-E-NE-N-review.json','N':'audit/video-axis-E-NE-N-review.json','S':'audit/video-axis-S-SE-review.json','SE':'audit/video-axis-S-SE-review.json','W':'audit/video-axis-W-NW-SW-review.json','NW':'audit/video-axis-W-NW-SW-review.json','SW':'audit/video-axis-W-NW-SW-review.json'}
for rel in set(files.values()):assert (ROOT/rel).exists(),rel
reviewed_before=set()
def check_before_rows(value):
 if isinstance(value,dict):
  name=value.get('file','')
  digest=value.get('beforeSha256') or value.get('sha256')
  if name.startswith('runtime/run/') and digest:
   assert before[name]==digest,(name,'before review mismatch')
   reviewed_before.add(name)
  for child in value.values():check_before_rows(child)
 elif isinstance(value,list):
  for child in value:check_before_rows(child)
for rel in set(files.values()):check_before_rows(read(ROOT/rel))
assert len(reviewed_before)==128,len(reviewed_before)
archive=ROOT/'audit/video-axis-pre-repair-paired-reviews.json'
if not archive.exists():
 write(archive,{'archivedAtUtc':now,'historicalOnly':True,'reviews':{d:read(ROOT/f'audit/run-{d}-paired-ground-review.json') for d in files}})
for d in files:
 path=ROOT/f'audit/run-{d}-paired-ground-review.json';review=read(path)
 for row in review['frames']:
  n=int(row.get('frame') or row['slot'].split('/')[-1]);slot=f'run/{d}/{n:02d}'
  current=sha(ROOT/f'runtime/{slot}.png')
  row['videoAxisInspection']={'beforeReview':files[d],'beforeSha256':before[f'runtime/{slot}.png'],'retained':slot not in inspected}
  if slot in inspected:
   m=inspected[slot];row['sha256']=current
   row['evidence']=m['afterEvidence']
   row['footOrientation']=m['afterEvidence']
   row['videoAxisInspection'].update({'repairReview':'audit/video-axis-root-repair-review.json','confirmedIssue':m['confirmedIssue'],'staticCorrectionReviewed':True})
  else:assert row['sha256']==current,slot
 review['latestVideoAxisRevision']={'reviewedAtUtc':now,'repairSlots':[s for s in inspected if s.startswith(f'run/{d}/')],'beforeReview':files[d],'currentRepairReview':'audit/video-axis-root-repair-review.json','dynamicVisualAcceptance':False}
 if d=='W':
  review['historicalPriorPassImageChanges']=review.pop('currentImageChanges',None)
  review['currentVideoPassImageChanges']=1
  review['evidence']['hands']='W07再次作小腿局部修订后，独立原图检查仍保留已修正的右空手前摆及左手持弓。历史W07 SHA已归档，不作为当前图引用。'
  review['evidence']['swing060708']=inspected['run/W/07']['afterEvidence']
 write(path,review)
rows=[]
for r in all_current:
 slot=r['file'][8:-4]
 if not slot.startswith('run/'):continue
 rows.append({**r,'slot':slot,'beforeSha256':before[r['file']],'beforeReview':files[slot.split('/')[1]],'retained':slot not in inspected,'repair':inspected.get(slot)})
write(ROOT/'audit/video-axis-current-closeout.json',{'completedAtUtc':now,'feedback':before_doc['feedback'],'beforeSnapshot':'audit/video-axis-revision-before.json','referenceExtraction':'audit/video-reference-20261004/extraction.json','referenceScope':'Motion only; same approved bamboo-girl identity and style retained','reviewedRunFrames':128,'totalRuntimeFrames':196,'changedFrames':[inspected[s] for s in sorted(inspected)],'retainedFrames':196-len(changed),'battleFramesUnchanged':all(r['sha256']==before[r['file']] for r in all_current if not r['file'].startswith('runtime/run/')),'timing':{'frames':16,'frameMs':75,'cycleMs':1200,'framesPerPosition':2},'dynamicVisualAcceptance':False,'clientIntegration':'not_integrated','reviews':[{'file':p,'sha256':sha(ROOT/p)} for p in sorted(set(files.values()))],'remainingLimits':['Reference actor is small and sometimes occluded; only visible motion judged','Actual browser playback and engine ground/displacement acceptance remain unverified','E/W hip-root identity is occluded; static foot inspection does not certify same anatomical hip tracking'],'frames':rows})
p=ROOT/'preview/index.html';html=p.read_text(encoding='utf-8')
html=html.replace('20261004-ground-pairs-final','20261004-video-axis-final')
p.write_text(html,encoding='utf-8')
write(ROOT/'audit/live-work-state.json',{'updatedAtUtc':now,'state':'video_reference_corrections_saved_verification_pending','writeBoundary':'This character directory only','correctedSlots':sorted(inspected),'dynamicVisualAcceptance':False,'clientIntegrated':False})
print(json.dumps({'changedFrames':len(changed),'retainedFrames':196-len(changed),'reviewedRunFrames':128,'dynamicVisualAcceptance':False}))
