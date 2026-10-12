"""Recheck existing cleanup candidates only; never deletes or reruns the full audit."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
A=R/'reviews/full-source-chain-audit.json'
O=R/'reviews/full-source-cleanup-candidates-current.json'
EXT={'.png','.gif','.jpg','.jpeg','.webp'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def path(v,base=R):
 p=Path(str(v).replace('\\','/'));return (p if p.is_absolute() else base/p).resolve()
def image_paths(v):
 if isinstance(v,dict):
  for x in v.values():yield from image_paths(x)
 elif isinstance(v,list):
  for x in v:yield from image_paths(x)
 elif isinstance(v,str) and '\n' not in v and len(v)<1200 and Path(v.replace('\\','/')).suffix.lower() in EXT:yield v
previous=read(A);original_audit_sha=sha(A)
snapshots=[];current={};protected=defaultdict(set);parse_issues=[]
for name in ['inventory-root.json','inventory-hit.json','inventory-cast.json','inventory-run-ne-cast.json','inventory-run-north.json']:
 p=R/name;v=read(p);snapshots.append({'file':name,'sha256':sha(p)})
 for f in v['frames']:
  current[f['path']]=f;protected[path(f['path'])].add('current_formal_frame')
  recpath=path(f.get('source_record') or f['native_evidence']);rec=read(recpath)
  n=rec.get('native',{})
  for v in [n.get('file'),n.get('sourceFile'),rec.get('file')]+rec.get('outputFiles',[]):
   if v:protected[path(v)].add('current_native_or_output')
  for v in image_paths(rec.get('references',[])):protected[path(v)].add('current_record_reference_conservatively_retained')
  for v in image_paths(rec.get('submittedParameters',{})):protected[path(v)].add('current_submission_reference_conservatively_retained')
for p in (R/'records').glob('*.json'):
 try:
  rec=read(p)
  if not isinstance(rec,dict) or rec.get('tool')!='image_gen.imagegen':continue
  status=str(rec.get('status','')).lower()+' '+str(rec.get('visualQA',{}).get('status','')).lower()
  if rec.get('export') or any(x in status for x in ['reject','superseded','failed','error']):continue
  for v in image_paths(rec):
   q=path(v)
   if q.is_relative_to(R):protected[q].add('possible_unique_in_progress_or_reference')
 except Exception as e:parse_issues.append({'file':str(p.relative_to(R)),'error':str(e)})
for p in list(R.rglob('*.html'))+list(R.rglob('*.md'))+list(R.rglob('preview-data.json')):
 try:
  text=p.read_text(encoding='utf-8-sig')
  refs=list(image_paths(json.loads(text))) if p.suffix=='.json' else re.findall(r'["\'(`]([^"\'<>\r\n)`]+\.(?:png|gif|webp|jpe?g))["\')`]',text,re.I)
  for v in refs:
   for base in [p.parent,R]:
    q=path(v,base)
    if q.is_relative_to(R) and q.is_file():protected[q].add('current_document_or_preview_reference')
 except Exception as e:parse_issues.append({'file':str(p.relative_to(R)),'error':str(e)})
safe=[];held=[]
for row in previous['cleanup']['candidates']:
 p=path(row['file']);reasons=[]
 if not p.is_relative_to(R):reasons.append('outside_character_boundary')
 elif not p.is_file():reasons.append('file_missing')
 else:
  if p.relative_to(R).parts[0] in ['frames','previews','preview']:reasons.append('formal_or_preview_tree')
  if sha(p)!=row['sha256']:reasons.append('candidate_sha_changed_since_full_audit')
  reasons.extend(protected[p])
  replacement_ok=False
  for e in row['evidence']:
   f=current.get(e['currentReplacement'])
   if not f or f['sha256']!=e['currentReplacementSha256']:continue
   q=path(f['path'])
   if q.is_file() and sha(q)==f['sha256']:replacement_ok=True
  if not replacement_ok:reasons.append('replacement_changed_or_unverified_since_full_audit')
 if reasons:held.append({'file':row['file'],'reasons':sorted(set(reasons))})
 else:safe.append({'file':row['file'],'absolutePath':str(p),'sha256':row['sha256'],'bytes':p.stat().st_size,'boundaryVerified':True,'sourceRecords':sorted(set(e['sourceRecord'] for e in row['evidence'])),'replacementEvidence':row['evidence'],'deletionAuthorized':False})
changed=[p for p in snapshots if sha(R/p['file'])!=p['sha256']]
out={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'mode':'candidate_revalidation_only_not_full_source_chain_audit','allowedRoot':str(R),'originalFullAudit':{'file':A.relative_to(R).as_posix(),'sha256':original_audit_sha,'finishedAtUtc':previous['finishedAtUtc']},'currentInventorySnapshots':snapshots,'snapshotStable':not changed,'changedInventories':changed,'originalCandidateCount':len(previous['cleanup']['candidates']),'currentCandidateCount':len(safe),'candidateBytes':sum(x['bytes'] for x in safe),'candidates':safe,'held':held,'parseIssues':parse_issues,'deletionPerformed':False,'deletionAuthorized':False,'limits':['Only revalidates previously audited candidates; new obsolete images are not added.','Current formal/native/submitted references and possible unique work in progress are retained.','SHA and boundary must be rechecked immediately before any later root-approved deletion.','Any inventory change during this check invalidates the candidate snapshot.','Full196-source audit remains pending root notification.']}
O.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':O.relative_to(R).as_posix(),'currentCandidates':len(safe),'bytes':out['candidateBytes'],'held':len(held),'holdReasons':dict(Counter(r for x in held for r in x['reasons'])),'snapshotStable':not changed,'parseIssueCount':len(parse_issues),'reportSha256':sha(O)},ensure_ascii=True))
