from pathlib import Path
import json,re,hashlib
Z=Path(__file__).resolve().parent
W=Path('D:/work/image')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
out={}
def walk(v,owner,key=''):
 if isinstance(v,dict):
  for k,x in v.items():walk(x,owner,k)
 elif isinstance(v,list):
  for x in v:walk(x,owner,key)
 elif isinstance(v,str) and re.match(r'^[A-Za-z]:[\\/]',v) and '\n' not in v and len(v)<500:
  try:
   p=Path(v)
   if p.is_relative_to(W):return
   k=str(p).replace('\\','/').lower()
   e=out.setdefault(k,{'path':str(p),'exists':p.is_file(),'recordedUses':[]})
   if len(e['recordedUses'])<4:e['recordedUses'].append({'record':str(owner),'key':key})
  except (ValueError,OSError):pass
for p in Z.rglob('*.json'):
 if 'migration-freeze' in p.name:continue
 try:walk(read(p),p)
 except (ValueError,OSError):pass
raw=list(out.values())
(Z/'migration-external-paths-20261011.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'externalCount':len(raw),'existing':sum(x['exists'] for x in raw),'nonGenerated':[x for x in raw if 'generated_images' not in x['path']][:30],'list':str(Z/'migration-external-paths-20261011.json')},ensure_ascii=False))

from datetime import datetime,timezone
import shutil
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
hash_index={}
for record in Z.rglob('*.generation.json'):
 try:
  data=read(record);p=Path(data.get('file',''));h=data.get('sha256')
  if h and p.is_file() and p.is_relative_to(W):hash_index.setdefault(h,[]).append(p)
 except (ValueError,OSError,TypeError):pass
copied=[];mapping=[];missing=[]
for entry in raw:
 p=Path(entry['path'])
 if not p.is_file():missing.append(str(p));continue
 h=sha(p);candidates=hash_index.get(h,[]);mirror=None
 for candidate in candidates:
  if sha(candidate)==h:mirror=candidate;break
 if mirror is None:
  mirror=Z/'migration-preserved-external-20261011'/p.name
  mirror.parent.mkdir(exist_ok=True)
  if mirror.exists():assert sha(mirror)==h
  else:shutil.copy2(p,mirror);copied.append(str(mirror))
  assert sha(mirror)==h
 mapping.append({'externalOriginalPath':str(p),'sha256':h,'workspaceMirror':str(mirror),'workspaceRelativePath':str(mirror.relative_to(W)),'bytes':p.stat().st_size,'sourceOriginalRetained':True})
mp=Z/'migration-external-paths-20261011.json'
mp.write_text(json.dumps({'originals':raw,'portableMappings':mapping,'copiedPreviouslyUnindexedOutputs':copied,'missingExternalFiles':missing,'note':'All external sourceOutputPath files have exact project mirrors. Preserve historical provenance strings. On new computer restore originals to recorded paths or adapt replay path resolution using this mapping, without altering images.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
progress=read(Z/'progress.json');current=[]
for t in progress['tiles']:
 if not t.get('candidate'):continue
 p=Path(t['candidate']);actual=sha(p);assert actual==t['candidateSha256']
 current.append({'tile':t['tile'],'file':str(p),'workspaceRelativePath':str(p.relative_to(W)),'sha256':actual,'internalPassed':t['internalPassed4kCount']==1})
continuation=read(Z/'local-continuation-20261011.json')
now=datetime.now(timezone.utc).isoformat()
freeze={'schemaVersion':1,'zone':'main-city/northeast','savedAtUtc':now,'generationStoppedAtUtc':'2026-10-12T02:29:59Z','stoppedTimeBasis':'First verified idle snapshot in this freeze turn; production was already idle after the last completed turn.','freezeReason':'User requests migration commit/push and continuation on another computer.','controllerFreeze':str(W/'MAP_MIGRATION_FREEZE_20261011.json'),'generationStopped':True,'newGenerationAllowed':False,'newRepairAllowed':False,'activeCoordinates':[],'lastCompletedCoordinates':[x['tile'] for x in current],'liveChildTaskCount':0,'stopPropagation':'No child agents remain live; collaboration.list_agents returned root only. No child was restarted.','inflightRequests':[],'unsavedSuccessfulOutputPaths':[],'selectedCandidatePaths':current,'complete4kCandidateCount':8,'internalPassed4kCount':8,'connectedGroupReviewed4kCount':8,'formalAcceptedCount':0,'remainingTileCount':56,'missingNativeCoreCount':896,'missingCoordinates':continuation['stillNeedsGeneration'],'nextMissingCoordinate':None,'nextCoordinateNote':'No new coordinate has been started or assigned. After migration, select an adjacent missing coordinate within rows1-8,cols9-16 and recheck ownership/real native neighbors.','pendingRepairs':[],'repairBreakpoint':'Current two connected groups have no open P2. Unpainted outer-world edges remain unreviewed; never infer whole-zone completion.','currentReplayEntrypoints':[{'tile':'r07_c13','script':str(Z/'r07_c13/qa/shared-foliage-20261011/apply.py'),'args':['--check']},{'tiles':['r08_c13','r08_c14'],'script':str(Z/'qa/central-foliage-20261011/apply.py'),'args':['check']},{'tile':'r07_c14','evidence':str(Z/'r07_c14/qa/final-review/source-replay.json')}],'connectedGroupIndex':str(Z/'connected-groups.json'),'latestPreview':str(Z/'qa/connected-group-r07_c13-r08_c14/b8d681f571f8430e473e/connected-2x2-preview.png'),'externalReferencePaths':[m['externalOriginalPath'] for m in mapping],'externalReferenceManifest':str(mp),'externalReferenceManifestSha256':sha(mp),'externalReferenceCount':len(mapping),'externalOriginalsHaveVerifiedWorkspaceMirrors':not missing,'newlyPreservedUnindexedOutputs':copied,'missingExternalFiles':missing,'portabilityNote':'All177 external references are generated image originals; approved style/layout inputs are already inside D:/work/image. Exact mirrors and path-remapping table are in workspace. Existing scripts use absolute Windows paths, so retain/restore paths or adapt resolver after moving computers. Python/Pillow runtime must be available on destination.','preserveAllOriginalsDraftsPreviews':True,'gitMutationsPerformed':False,'gitOwner':'01a11b5e-158a-77d0-8c02-e8e503b7abe4','privateUploaderStateUntouched':True,'resumeOnlyAfterMigrationAndAuthorization':True}
fp=Z/'migration-freeze-20261011.json';fp.write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
progress.update({'status':'migration_frozen_no_new_generation','updatedAt':now,'nextStep':'Migration freeze active. Preserve all files; no new generation or repair until authorized after migration.','generationStopped':True,'migrationFreeze':str(fp)})
(Z/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['continuation-round-20261011.json','local-continuation-20261011.json']:
 p=Z/name;j=read(p);j.update({'generationStopped':True,'migrationFreeze':str(fp),'nextStep':'Frozen for migration; do not resume artwork before migration and authorization.'});p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
handoff=Z/'HANDOFF.md';old=handoff.read_text(encoding='utf-8-sig');head='# 迁移冻结（最高优先级，2026-10-11纽约时间）\n\n已停止全部新生图、返修与扩图；当前无在途请求、无运行子任务、无未保存成功结果。请以 migration-freeze-20261011.json 为准；下方续作说明仅作迁移后的历史断点，不是当前开工指令。8/64块与两组接缝已通过，56块待做。177个工作区外生成源均已对应到项目内逐字节副本；映射见 migration-external-paths-20261011.json。原图、在制稿、预览全部保留；本工位未执行Git操作。\n\n'
if not old.startswith('# 迁移冻结'):handoff.write_text(head+old,encoding='utf-8')
print(json.dumps({'freeze':str(fp),'externalReferences':len(mapping),'newlyPreserved':copied,'missingExternal':missing,'inflight':0,'unsavedSuccessful':0,'generationStopped':True}))


