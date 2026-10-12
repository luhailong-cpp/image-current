from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

OUT = Path(__file__).resolve().parent
REPO = OUT.parent.parent.parent.parent
ZONE = REPO / 'qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/accelerated-northeast-coast'
DEST = OUT / 'coast-sources-v2.json'
assert not DEST.exists()

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

old = load(OUT / 'coast-sources-v1.json')
new = dict(old)
new['auditId'] = 'island-east-coast-sources-v2'
new['sourceVerificationCompletedAtUtc'] = old['completedAtUtc']
new['completedAtUtc'] = datetime.now(timezone.utc).isoformat()
new['supersedes'] = {'report': (OUT / 'coast-sources-v1.json').relative_to(REPO).as_posix(), 'sha256': digest(OUT / 'coast-sources-v1.json'), 'scope': 'Policy clarification and later input hash freshness; v1 remains a historical snapshot.'}
new.pop('requiredFutureImageModel',None)
new.pop('requiredFutureRouteVerified',None)
policies=[]
for name in ['AGENTS.md','docs/IMAGE_MODEL_REQUIREMENT.md']:
    p=REPO/name
    text=p.read_text(encoding='utf-8-sig')
    assert ('2.0' in text and ('撤销' in text or 'revoked' in text))
    policies.append({'repositoryRelativePath':name,'sha256':digest(p)})
new['currentModelPolicy']={'userClarifiedDate':'2026-10-13','existingFree25Preferred':True,'existingBuiltin20FallbackAllowed':True,'missing25SelectorDoesNotPauseProduction':True,'paidApiAuthorized':False,'unknownActualModelMustRemainUnknown':True,'thisTaskStillDoesNotGenerateOrRepairArt':True,'evidence':policies}
changed=[]
for entry in old['inputSnapshot']:
    p=REPO/entry['repositoryRelativePath']
    now=digest(p) if p.is_file() else None
    if now!=entry['sha256']:
        changed.append({'repositoryRelativePath':entry['repositoryRelativePath'],'auditedSha256':entry['sha256'],'currentSha256':now,'rasterChanged':p.suffix.lower()=='.png'})
candidate_fields=['tileId','file','sha256','dimensions','selectedCores']
current_progress=load(ZONE/'progress.json')
current_selection=load(ZONE/'current-selection-20261012.json')
initial_candidates={t['tileId']:t for t in old['tiles']}
semantic_conflicts=[]
for record in current_progress['currentAdopted4096Files']:
    expected=initial_candidates.get(record['tileId'])
    if not expected or record['sha256']!=expected['candidate']['sha256']:
        semantic_conflicts.append({'tileId':record['tileId'],'type':'new_candidate_hash_requires_new_source_audit'})
for t in old['tiles']:
    sid={s['id']:s for s in t['sources']}
    for group in [current_progress['selectedNativeSourcesByTile'][t['tileId']],current_selection['native'][t['tileId']]]:
        if set(x['id'] for x in group)!=set(sid) or any(x['sha256']!=sid[x['id']]['sha256'] for x in group if x['id'] in sid):
            semantic_conflicts.append({'tileId':t['tileId'],'type':'new_native_selection_requires_new_source_audit'})
    initial_grid=[[s['id'] for s in sorted(t['sources'],key=lambda x:(x['pasteAt'][1],x['pasteAt'][0]))][i:i+4] for i in range(0,16,4)]
    current_cand=next(x for x in current_selection['candidates'] if x['tileId']==t['tileId'])
    if current_cand['sha256']!=t['candidate']['sha256'] or current_cand['selectedCores']!=initial_grid:
        semantic_conflicts.append({'tileId':t['tileId'],'type':'new_candidate_selection_requires_new_source_audit'})
new['freshnessAfterProductionResumed']={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'changedFiles':changed,'rasterFilesChangedCount':sum(x['rasterChanged'] for x in changed),'selectedCandidateOrNativeSemanticConflicts':semantic_conflicts,'currentCandidateAndSourceSelectionsUnchanged':not semantic_conflicts,'hashPassesApplyOnlyToRecordedSourceBytes':True,'newVersionsNotAutomaticallyPassed':True}
if semantic_conflicts or any(x['rasterChanged'] for x in changed):
    new['summary']['sourceIdentityOrPositionUncertainCount']+=len(semantic_conflicts)+sum(x['rasterChanged'] for x in changed)
new['notes'].append({'type':'latest_user_model_rule','action':'Earlier mandatory 2.5 policy fields are superseded. Production owners may use the existing builtin fallback. This independent provenance task still produces no new art.'})
DEST.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(DEST),'freshness':new['freshnessAfterProductionResumed'],'summary':new['summary']},ensure_ascii=False))
