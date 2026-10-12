from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def local(p):
 p=Path(p)
 return p.relative_to(ROOT).as_posix() if p.is_absolute() else p.as_posix()
current=read(ROOT/'current-artifacts.json')
release_path=ROOT.parents[3]/'docs/MAP_PRODUCTION_RESUME_20261012.json'
if not release_path.exists():release_path=ROOT.parent.parent/'resume-production-20261010/production-resume.json'
release=read(release_path) if release_path.exists() else {}
gate_held=(ROOT/'capacity-gate-ack.json').exists() and not release.get('newArtworkGenerationAllowed',False) and not (ROOT/'user-resume-20261010.json').exists()
selected=set();usable=set();tiles={}
for ident,e in current.items():
 if not re.fullmatch(r'r\d{2}_c\d{2}',ident):continue
 rec=read(ROOT/e['assembly']);names={Path(s['file']).name for s in rec['sources']}
 qa=read(ROOT/e['qa']) if e.get('qa') and (ROOT/e['qa']).exists() else {};cand=ROOT/e['candidate']
 qah=qa.get('candidate',{}).get('sha256') if isinstance(qa.get('candidate'),dict) else qa.get('candidateSha256')
 ok=(qa.get('internalAccepted') is True or qa.get('status')=='internal-native-seams-pass-external-pending') and qah==sha(cand)
 selected.update(names)
 if ok:usable.update(names)
 tiles[ident]={'candidate':e['candidate'],'candidateSha256':sha(cand),'internalAccepted':ok,'qa':e.get('qa'),'qaSha256':sha(ROOT/e['qa']) if e.get('qa') and (ROOT/e['qa']).exists() else None,'assembly':e['assembly'],'assemblySha256':sha(ROOT/e['assembly']),'formalAccepted':False}
entries=[]
seen_native_hashes=set()
for p in sorted(ROOT.rglob('*.png.generation.json')):
 r=read(p);f=Path(r['file'])
 assert f.is_file() and sha(f)==r['sha256'],f
 if r['sha256'] in seen_native_hashes:continue
 seen_native_hashes.add(r['sha256'])
 entries.append({'id':f.stem,'file':local(f),'sha256':r['sha256'],'width':r['width'],'height':r['height'],'generationRecord':local(p),'generationRecordSha256':sha(p),'tool':r['tool'],'actualModel':r.get('actualModel'),'actualQuality':r.get('actualQuality'),'submittedParameters':r.get('submittedParameters'),'globalNativeBox':r['globalNativeBox'],'globalCoreBox':r.get('globalCoreBox'),'geometryNote':'whole-object repair window; globalNativeBox is authoritative' if 'globalCoreBox' not in r else None,'selectedInCurrent4kCandidate':f.name in selected,'status':'selected-current-candidate' if f.name in selected else r.get('status','work-in-progress-not-selected')})
now=datetime.now(timezone.utc).isoformat()
write(ROOT/'source-index.json',{'zone':'northwest','updatedAt':now,'generationCountIncludingRetries':len(entries),'currentCandidateSources':len(selected),'actualModelQualityDisclosure':'not confirmed; configuration targets are in individual records','images':entries})
active=[Path(p).name.removeprefix('work-') for p in current.get('adjacentWork',[])]
p=read(ROOT/'progress.json')
p.update(updatedAt=now,status='native-production-and-seam-repair',target4kCount=49,generatedNativeCount=len(entries),usableNativeCount=len(usable),usableNativeDefinition='Sources contributing to internally accepted 4K candidates; exterior joins separate',selectedCandidateNativeCount=len(selected),complete4kCount=sum(t['internalAccepted'] for t in tiles.values()),complete4kDefinition='4096 fully native-pixel candidate passing internal QA, before external acceptance',candidate4kCount=len(tiles),formalAcceptedCount=0,currentTile=p.get('currentTile','r04_c02'),currentPatch=p.get('currentPatch','native-production'),currentCandidates=tiles,externalSeamsAccepted=False,nextStep=p.get('nextStep','Continue adjacent production and whole-boundary cross-tile checks; native bridge repairs where required'),activeTiles=active)
for stale in ['currentCandidate','internalAccepted']:p.pop(stale,None)
p.update(fullyCovered4kCount=len(tiles),internalPassed4kCount=p['complete4kCount'],externalPassed4kCount=0,missingFullyCovered4kCount=49-len(tiles),missingInternalPassed4kCount=49-p['complete4kCount'],missingFormalAccepted4kCount=49)
if gate_held:
 p.update(status='capacity-layout-gate-generation-held',currentPatch='existing-artwork-QA-only',nextStep='Await main root capacity/layout gate release; preserve existing artwork; no new generation',capacityGate='capacity-gate-ack.json',inFlightGeneration=False)
issues=ROOT/'open-artwork-issues.json'
p['errors']=read(issues).get('issues',[]) if issues.exists() else []
p['productionRelease']={'file':str(release_path),'newArtworkGenerationAllowed':release.get('newArtworkGenerationAllowed',False),'runtimePendingIsNotGlobalArtHold':release.get('runtimePendingIsNotGlobalArtHold',False)}
write(ROOT/'progress.json',p)
plan=read(ROOT/'tile-plan.json')
for t in plan['tiles']:
 if t['id'] in tiles:
  v=tiles[t['id']];t.update(state='internally-accepted-candidate' if v['internalAccepted'] else 'candidate-internal-review',candidate=v['candidate'],formalAccepted=False)
 elif t['id'] in active:t.update(state='capacity-gate-qa-only-partial' if gate_held else 'native-production',formalAccepted=False)
write(ROOT/'tile-plan.json',plan)
print(json.dumps({'generatedNativeCount':len(entries),'currentCandidateSources':len(selected),'complete4kCount':p['complete4kCount'],'candidate4kCount':len(tiles),'formalAcceptedCount':0},ensure_ascii=False))

