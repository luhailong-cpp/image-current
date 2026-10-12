from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
timing={'frameMs':75,'frameDurationsMs':[75]*16,'cycleMs':1200,'slowFrameMs':300,'slowCycleMs':4800,'availableNormalCycleMs':[1200],'clientTimingConfirmed':False,'uniformFrames':True,'extraLoopPauseMs':0,'updatedAtUtc':now}
for p in (ROOT/'review-parts').glob('*.json'):
 d=read(p);changed=False
 for row in d.get('sequences',[]):
  key=row.get('sequence') or (str(row.get('action'))+'/'+str(row.get('direction')))
  if not key.startswith('run/'):continue
  direction=key.split('/')[1]
  for k in ['trialCycleMs','trialLoopMs','defaultTrialCycleMs','oldBaselineMs','normalTrialCycleMs','normalTrialFrameMs','slowTrialCycleMs','normalPreview','slowPreview','previews','normalSizePreviews','timingDecision']:row.pop(k,None)
  row['currentTiming']=timing
  row['previews']={'normal':f'preview/qa/run-{direction}-normal.apng','slow':f'preview/qa/run-{direction}-slow.apng','interactive':'preview/index.html'}
  row['historicalEvidenceNote']='Earlier reviewer text may mention old preview durations; currentTiming supersedes timing only, without altering its visual observations or approval.'
  changed=True
 if changed:
  if 'timing' in d:d['timing']=timing
  d['currentTiming']=timing;write(p,d)
for rel in ['provenance/run-north/timing-current.json','provenance/run-south/current-timing.json','provenance/run-SW/current-timing.json']:
 write(ROOT/rel,{**timing,'currentPreview':'preview/index.html','note':'Latest user request: exactly16 frames at75ms; old fast options removed. Subsequent four-contact grounding repairs are tracked separately from historical acceptance.'})
accepted=read(ROOT/'accepted-version.json')
changed=[{'file':row['file'],'historicalSha256':row['sha256'],'currentSha256':hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest()} for row in accepted['frames'] if hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest()!=row['sha256']]
write(ROOT/'audit/run-timing-1200-update.json',{'atUtc':now,'sourceThreadId':'01a0f76f-0056-7c23-a688-10733b6b89e3','request':'1200ms整圈、16帧均匀75ms；正式预览删除480/640/720/800档，保留慢放和逐帧。','timing':timing,'historicallyAcceptedImagesUnchanged':len(accepted['frames'])-len(changed),'historicalImageSetSha256':accepted['imageSetSha256'],'subsequentGroundingRepairs':changed,'historicalAcceptanceRewritten':False,'clientModified':False,'visualDynamicApproval':False})
for rel in ['manifest.json','preview/data.js']:
 p=ROOT/rel;raw=p.read_text(encoding='utf-8-sig')
 d=json.loads(raw.removeprefix('window.BAMBOO_PREVIEW = ').strip().removesuffix(';')) if p.suffix=='.js' else json.loads(raw)
 for seq in d['sequences']:
  if seq['action']=='run':
   seq['ms']=75;seq['comparisonCycleMs']=[1200];seq['timingStatus']='offline_default_1200ms_client_unconfirmed';seq['clientTimingConfirmed']=False
  else:assert seq['ms']=={'hit':40,'attack':30,'cast':45}[seq['action']]
 if p.suffix=='.js':p.write_text('window.BAMBOO_PREVIEW = '+json.dumps(d,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
 else:write(p,d)
print(f'Current review timing updated; {len(changed)} subsequent grounding repairs recorded without rewriting historical acceptance.')
