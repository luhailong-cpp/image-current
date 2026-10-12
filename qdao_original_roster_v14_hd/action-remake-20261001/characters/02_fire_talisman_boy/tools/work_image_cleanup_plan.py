"""Plan all work-image removals after root freeze. Never deletes any file.

Latest root authorization supersedes earlier conservative cleanup suggestions:
formal196/previews/text stay; all work PNG/JPG/JPEG/GIF/WebP may be removed after
checking no unique unexported image contradicts that final-state declaration.
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
import hashlib,json,re

R=Path(__file__).resolve().parents[1]
W=(R/'work').resolve()
OUT=R/'reviews/work-image-cleanup-plan.json'
EXT={'.png','.jpg','.jpeg','.gif','.webp'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def resolve(v,base=R):
 p=Path(str(v).replace('\\','/'));return (p if p.is_absolute() else base/p).resolve()
def rel(p):return p.relative_to(R).as_posix()
auditpath=R/'reviews/full-source-chain-audit.json';audit=read(auditpath)
conflicts=[];record_errors=[];owned=defaultdict(list);rejected_unexported=[]
inventory_snapshot=[];formal={};current_record_paths=set();native_slots=defaultdict(list)
for name in ['inventory-root.json','inventory-hit.json','inventory-cast.json','inventory-run-ne-cast.json','inventory-run-north.json']:
 p=R/name;doc=read(p);inventory_snapshot.append({'file':name,'sha256':sha(p)})
 for f in doc['frames']:
  p=resolve(f['path']);formal[p]={'file':f['path'],'sha256':f['sha256'],'sourceRecord':f.get('source_record') or f['native_evidence']}
  current_record_paths.add(resolve(formal[p]['sourceRecord']))
  if p.is_relative_to(W):conflicts.append({'code':'formal_frame_inside_work','file':rel(p)})
  if not p.is_file() or sha(p)!=f['sha256']:conflicts.append({'code':'current_formal_sha_mismatch','file':f['path']})
for frame in audit['frames']:
 n=frame.get('native',{})
 if n.get('path'):
  p=resolve(n['path'])
  if p.is_relative_to(W):native_slots[p].append({'slot':frame['slot'],'formalFile':frame['formalFile'],'nativeSha256':n['sha256'],'formalSha256':frame['formal']['sha256'],'actualHostSources':frame.get('hostSources',[])})
audit_inputs={x['file']:x['sha256'] for x in audit['inputInventories']}
for row in inventory_snapshot:
 if audit_inputs.get(row['file'])!=row['sha256']:conflicts.append({'code':'inventory_changed_since_full_audit','file':row['file']})
for p in (R/'records').glob('*.json'):
 try:
  doc=read(p)
  if not isinstance(doc,dict) or doc.get('tool')!='image_gen.imagegen':continue
  n=doc.get('native',{});n=n if isinstance(n,dict) else {}
  vals=[n.get('file'),n.get('sourceFile'),doc.get('file')]+doc.get('outputFiles',[])
  paths=[]
  for v in vals:
   if not isinstance(v,str) or Path(v).suffix.lower() not in EXT:continue
   q=resolve(v)
   if q.is_relative_to(W) and q.is_file() and q not in paths:paths.append(q)
  if not paths:continue
  status=str(doc.get('status',''))+' '+str(doc.get('visualQA',{}).get('status',''))
  rejected=any(t in status.lower() for t in ['reject','superseded'])
  claim=n.get('sha256') or doc.get('sha256')
  detail={'record':rel(p),'recordSha256':sha(p),'status':doc.get('status'),'visualStatus':doc.get('visualQA',{}).get('status'),'nativeSha256Claim':claim,'exportFile':doc.get('export',{}).get('file'),'exportSha256':doc.get('export',{}).get('sha256'),'isCurrentInventoryRecord':p.resolve() in current_record_paths}
  for q in paths:owned[q].append(detail)
  if not doc.get('export'):
   if rejected:rejected_unexported.append({'record':rel(p),'images':[rel(q) for q in paths],'statusEvidence':status.strip()})
   else:conflicts.append({'code':'unexported_local_generation_without_rejection','record':rel(p),'images':[rel(q) for q in paths],'statusEvidence':status.strip()})
 except Exception as e:record_errors.append({'file':rel(p),'error':str(e)})
images=[];extensions=Counter();categories=Counter()
for listed in sorted(p for p in W.rglob('*') if p.is_file() and p.suffix.lower() in EXT):
 p=listed.resolve()
 if not p.is_relative_to(W) or not p.is_relative_to(R):
  conflicts.append({'code':'image_resolves_outside_work','listedPath':str(listed),'resolvedPath':str(p)});continue
 if p in formal:
  conflicts.append({'code':'formal_path_selected_for_removal','file':rel(p)});continue
 digest=sha(p);sources=owned[p]
 if p in native_slots:category='current_native_already_exported'
 elif sources and all('reject' in str(s['status']).lower() or 'reject' in str(s['visualStatus']).lower() for s in sources):category='rejected_generation'
 elif sources:category='superseded_or_other_generation_image'
 else:category='work_preview_contact_crop_or_unlinked_image'
 categories[category]+=1;extensions[p.suffix.lower()]+=1
 for slot in native_slots[p]:
  if slot['nativeSha256']!=digest:conflicts.append({'code':'current_native_changed_since_full_audit','file':rel(p),'slot':slot['slot']})
 images.append({'file':rel(p),'absolutePath':str(p),'sha256':digest,'bytes':p.stat().st_size,'extension':p.suffix.lower(),'category':category,'boundaryVerified':True,'currentExportSources':native_slots[p],'sourceRecords':sources,'reason':'最新人类只保留游戏最终素材；root已声明无唯一在制稿。正式PNG和previews保留，work图片为原生/拒稿/加工与私有预览，可按本计划清理。','deletePerformed':False})
# Inspect actual resource references in the retained preview HTML. Historical
# provenance strings remain in text records and are not treated as live pixels.
preview_refs=[]
for p in (R/'previews').glob('*.html'):
 text=p.read_text(encoding='utf-8-sig')
 for v in re.findall(r'(?:src|href)=["\']([^"\']+\.(?:png|gif|jpe?g|webp))["\']',text,re.I):
  q=resolve(v,p.parent)
  if q.is_relative_to(W):preview_refs.append({'html':rel(p),'reference':v,'image':rel(q)})
 if re.search(r'\.\./work[/\\]',text):preview_refs.append({'html':rel(p),'reference':'literal ../work resource path found; inspect retained preview before deleting'})
if preview_refs:conflicts.append({'code':'retained_preview_references_work_images','references':preview_refs})
if record_errors:conflicts.append({'code':'record_parse_errors','records':record_errors})
for row in inventory_snapshot:
 if sha(R/row['file'])!=row['sha256']:conflicts.append({'code':'inventory_changed_during_plan','file':row['file']})
listed_after={p.resolve() for p in W.rglob('*') if p.is_file() and p.suffix.lower() in EXT}
if listed_after!={resolve(x['file']) for x in images}:conflicts.append({'code':'work_image_set_changed_or_boundary_conflict'})
if not audit['pass'] or not audit['summary']['snapshotStable']:conflicts.append({'code':'full_audit_not_passed_or_unstable'})
out={'schema':1,'character':'02_fire_talisman_boy','plannedAtUtc':datetime.now(timezone.utc).isoformat(),'mode':'plan_only_no_deletion','deletionPerformed':False,'readyForRootBoundaryShaCheck':not conflicts,'authority':'2026-10-04 root明确正式PNG已冻结、无未导出唯一在制稿；用户只保最终游戏素材，原生/拒稿/旧联系表可删除。实际删除由root逐项PowerShell校验边界后执行。','allowedImageRoot':str(W),'characterRoot':str(R),'allowedExtensions':sorted(EXT),'fullAudit':{'file':rel(auditpath),'sha256':sha(auditpath),'finishedAtUtc':audit['finishedAtUtc'],'summary':audit['summary'],'receiptEvidenceGrades':audit['receiptEvidenceGrades']},'currentInventories':inventory_snapshot,'retained':{'formal196':list(formal.values()),'previewDirectory':str(R/'previews'),'allNonImageFiles':True,'textSourcesAndHashes':'保留records/prompts/reviews/工具与JSON、MD、TXT、HTML等所有文字文件；已删除原生的历史路径和SHA继续作为来源证据，不篡改为不存在的回执。','outsideCharacterFiles':'禁止本计划删除宿主generated_images、身份画像、designs或任何其他角色。'},'summary':{'workImages':len(images),'totalBytes':sum(x['bytes'] for x in images),'extensions':dict(extensions),'categories':dict(categories),'rejectedUnexportedRecords':len(rejected_unexported),'unexportedUniqueConflicts':len([x for x in conflicts if x['code']=='unexported_local_generation_without_rejection']),'conflicts':len(conflicts)},'images':images,'rejectedUnexportedEvidence':rejected_unexported,'conflicts':conflicts,'rootExecutionRequirements':['Resolve each absolutePath again and require it strictly below allowedImageRoot; require extension in allowedExtensions.','Hash each actual image immediately before removal and require exact listed SHA256. Any mismatch or new inventory/frame change stops execution and requires a refreshed plan.','Use PowerShell Remove-Item -LiteralPath on explicit validated files only; no directory-recursive deletion and no cross-shell composition.','Preserve all196 formal PNG and allpreviews files; preserve allnonimage text. Save deletion outcome hashes/count in text before final post-cleanup verification.'],'postCleanupAuditNote':'This full-source audit was run before authorized native cleanup. Missing work/native after cleanup must be explained by the deletion receipt and retained SHA/actual host match, not misreported as never generated. Reconstructive source checks can still use the retained host files; do not create new fake tool receipts.'}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':rel(OUT),'summary':out['summary'],'readyForRootBoundaryShaCheck':out['readyForRootBoundaryShaCheck'],'conflicts':conflicts,'reportSha256':sha(OUT)},ensure_ascii=True))
