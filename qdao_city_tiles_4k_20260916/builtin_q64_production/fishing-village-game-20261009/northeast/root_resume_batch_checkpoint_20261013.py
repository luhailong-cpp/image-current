import json,uuid,hashlib
from pathlib import Path
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):
 p=Path(p);return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,d):
 t=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t.replace(p)
now=datetime.now(timezone.utc).isoformat()
f=Z/'records/resume-batch-checkpoint-20261013-v1.json';assert not f.exists()
s={t:rd(Z/'records'/f'{t}.working-selection.json') for t in ['r03_c12','r04_c12']}
d={'updatedAtUtc':now,'status':'active_art_production','rootSelectedCoreCounts':{k:len(v) for k,v in s.items()},'selectedSources':{t:{k:ref(Z/'native'/v) for k,v in v.items()} for t,v in s.items()},'repeatedRepairsDeferred':['r04_c12_p43','r03_c12_p11'],'pendingPreparedOnly':'r04_c12_p24-v2 guide prepared; v1 guide retained but no request submitted','newIndependentReview':ref(Z/'qa/r07_c14/east-sol-independent-review-20261013.json'),'r05_c14Review':ref(Z/'qa/r05_c14-v4/central-resume-independent-review-20261013.json'),'r05_c14Status':'46/49 visual pass, short water-tone edge remains pending','r06_c11Handoff':ref(Z/'records/west_sol/r06_c11.resume-batch-handoff-20261013.json'),'r06_c11Status':'16/16 best candidate remains unpassed at a contribution material edge; worker continuing r07c11 independent cores','formalAccepted':False,'taskComplete':False,'generationRoute':'builtin','actualModel':None,'modelEvidence':'actual model unreturned','policy':'free/included2.5 preferred; existing built-in2.0 allowed, no paid API','coordinateAllocation':ref(Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json'))}
put(f,d)
a=rd(Z/'records/active-candidates.json');a['tiles']['r07_c14']['reviewStatus']='independent_internal49_and_north_west15_passed_south_pending';a['tiles']['r07_c14']['reviewRecord']=str(Z/'qa/r07_c14/east-sol-independent-review-20261013.json');a['updatedAtUtc']=now
a['activeBlockers']=['r05_c12 west roof tone pending; r05_c14 local water tone pending; r06_c11 contribution boundary pending','Root r04c12p43 and r03c12p11 roof alignment deferred unpassed; remaining exclusive missing cores ongoing']
a['reviewPaths']=list(dict.fromkeys(a['reviewPaths']+['qa/r07_c14/east-sol-independent-review-20261013.json','qa/r05_c14-v4/central-resume-independent-review-20261013.json']))
put(Z/'records/active-candidates.json',a)
p=rd(Z/'progress.json');p['latestBatchCheckpoint']=ref(f);p['currentTile']='r04_c12,r03_c12,r04_c13,r04_c14,r07_c11';p['currentPatch']='Root r04c12 last-column missing cores; central c13 and east c14 northward; west r07c11';p['nextStep']='Complete missing native cores from stable anchors; defer repeated failed local seams with explicit unpassed records';p['generationStopped']=False;p['newArtworkGenerationAllowed']=True;p['updatedAtUtc']=now;put(Z/'progress.json',p)
print(json.dumps({'saved':str(f),'rootSelected':d['rootSelectedCoreCounts'],'totals':'coordinator maintains whole-map totals; no historical rescan performed'}))

