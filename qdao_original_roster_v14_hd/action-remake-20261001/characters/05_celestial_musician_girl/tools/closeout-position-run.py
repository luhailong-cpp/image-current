"""Record a promoted, browser-checked position revision. Does not delete images."""
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json, hashlib

ROOT=Path(__file__).resolve().parent.parent
EV='provenance/ground-contact-20261004'
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def save(p,v):(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
promotion=load(EV+'/position-promotion.json')
browser=load(EV+'/position-browser-check.json')
acceptance=load(EV+'/position-acceptance.json')
assert promotion['status']=='complete' and browser['passed'] and acceptance['accepted']
assert browser['finalSelectionSha256']==sha('final-selection.json')
rows=load('final-selection.json');plan=load(EV+'/position-selection-all.json')
assert len(rows)==196 and len(plan)==128
selected_prompts=[]
for r in rows:
    if r['action']!='run':continue
    m=load(r['generationRecord']);g=m['sourceGeneration']
    selected_prompts.append({'file':r['file'],'sha256':r['sha256'],'nativeSha256':r['nativeSha256'],
        'route':g.get('route'),'targetModel':g.get('configSnapshot',{}).get('model'),
        'targetQuality':g.get('configSnapshot',{}).get('quality'),'actualModel':None,'actualQuality':None,
        'prompt':g.get('submittedParameters',{}).get('prompt') or g.get('prompt'),
        'references':g.get('references',[]),'evidence':g.get('evidence',{})})
assert all(x['prompt'] for x in selected_prompts)
save(EV+'/selected-prompt-set.json',{'route':'builtin','frames':selected_prompts})
new_generations={}
for p in (ROOT/'provenance/run').glob('*.generation.json'):
    g=json.loads(p.read_text(encoding='utf-8-sig'))
    if g.get('generatedAt','')>='2026-10-04T04:18:21' and g.get('sha256') and g.get('route')=='builtin':
        new_generations[g['sha256']]=str(p.relative_to(ROOT)).replace('\\','/')
retained=sum('run-correction-20260930' in r['nativeSourceFile'] for r in rows)
now=datetime.now(timezone.utc).isoformat()
status=load('STATUS.json')
status.update(updatedAt=now,status='offline_artwork_complete_client_pending',
    newCurrentCandidateSlots=196-retained,priorRetainedCandidateSlots=retained,
    newSuccessfulGeneratedImages=294+len(new_generations),
    supersededNewImages=294+len(new_generations)-(196-retained),
    latestReferenceReview=EV+'/closeout.json',latestLocalRepairCount=sum(r['sourceFile'].startswith('staging/') for r in plan))
status['groundContactReview'].update(status='offline_artwork_and_browser_review_passed',
    acceptance=EV+'/position-acceptance.json',browserReview=EV+'/position-browser-check.json',
    actualContactFramesByDirection={d:{'RIGHT':list(range(1,9)),'LEFT':list(range(9,17))} for d in ['N','NE','E','SE','S','SW','W','NW']},
    mandatoryCorrectionsRemaining=[],clientValidated=False)
save('STATUS.json',status)
result={'completedAt':now,'status':'offline_artwork_and_browser_complete_client_pending',
    'runFrames':128,'allFinalFrames':196,'independentlyDrawnReplacementSources':status['latestLocalRepairCount'],
    'reusedCorrectSources':128-status['latestLocalRepairCount'],
    'successfulGenerationsThisRevision':len(new_generations),'generationRecords':list(new_generations.values()),
    'acceptance':EV+'/position-acceptance.json','promotion':EV+'/position-promotion.json',
    'browser':EV+'/position-browser-check.json','promptSet':EV+'/selected-prompt-set.json',
    'finalSelectionSha256':sha('final-selection.json'),'frameMs':75,'cycleMs':1200,
    'mandatoryCorrectionsRemaining':[],'clientValidated':False,
    'contactFramesByDirection':status['groundContactReview']['actualContactFramesByDirection']}
save(EV+'/closeout.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ['generationRecords','contactFramesByDirection']},ensure_ascii=False))
