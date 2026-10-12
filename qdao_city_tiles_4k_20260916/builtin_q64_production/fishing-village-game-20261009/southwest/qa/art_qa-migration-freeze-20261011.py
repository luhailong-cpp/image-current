import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,shutil,datetime,re
Z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest')
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:{'path':p.as_posix(),'relativePath':p.relative_to(Z).as_posix() if p.is_relative_to(Z) else None,'sha256':sha(p),'bytes':p.stat().st_size}
freeze=Z/'qa/art_qa-migration-freeze-20261011.json'
assert not freeze.exists(), 'Refusing to overwrite existing freeze report'
archive=Z/'migration-art-qa-20261011';archive.mkdir(exist_ok=True)
outputs=[];problems=[];external={}
for p in sorted((Z/'native').glob('r08_c06*.png')):
 stem=p.name[:-4];gp=Path(str(p)+'.generation.json');rp=p.with_suffix('.receipt.json');qp=p.with_suffix('.request.json');pp=p.with_suffix('.prompt.txt')
 row=ref(p);row['metadata']={}
 for label,f in [('generation',gp),('receipt',rp),('request',qp),('prompt',pp)]:
  if f.is_file():row['metadata'][label]=ref(f)
  else:problems.append({'file':p.as_posix(),'missing':label})
 if gp.exists():
  g=rd(gp);row['recordedStatus']=g.get('status');row['generatedAt']=g.get('generatedAt');row['matchesGenerationHash']=g.get('sha256')==row['sha256']
  if not row['matchesGenerationHash']:problems.append({'file':p.as_posix(),'error':'generation hash mismatch'})
  for q in g.get('references',[]):
   ep=Path(q['path'])
   if not ep.is_relative_to(Z):external[ep.as_posix()]=q
 if rp.exists():
  r=rd(rp);src=r.get('sourceGeneratedImage')
  if not src:
   match=re.search(r' as (.+?\.png) by default',str(r.get('output_hint',r.get('result',{}).get('output_hint',''))))
   if match:src=match.group(1)
  if src:
   sp=Path(src);row['originalGeneratedImage']=sp.as_posix();row['originalStillExists']=sp.is_file()
   if sp.is_file():
    row['originalMatchesSavedCopy']=sha(sp)==row['sha256']
    if not row['originalMatchesSavedCopy']:problems.append({'file':p.as_posix(),'error':'source copy mismatch'})
  row['receiptSavedAt']=r.get('savedAt')
 outputs.append(row)
external_map=[]
for name,q in external.items():
 p=Path(name);assert p.exists();h=sha(p);assert h==q['sha256']
 candidates=list((Z/'migration-stair-rebuild-20261011/external-references').glob(p.stem+'-*'+p.suffix))
 saved=next((a for a in candidates if sha(a)==h),None)
 if saved is None:
  d=archive/'external-references';d.mkdir(exist_ok=True);saved=d/(p.stem+'-'+h[:12]+p.suffix)
  if not saved.exists():shutil.copyfile(p,saved)
  assert sha(saved)==h
 external_map.append({'original':ref(p),'archived':ref(saved),'operation':'byte-identical existing archive reused or original copied; original retained'})
contract=Z.parent/'production-contract.json';cd=archive/'production-contract.snapshot.json'
if not cd.exists():shutil.copyfile(contract,cd)
assert sha(cd)==sha(contract)
external_map.append({'original':ref(contract),'archived':ref(cd),'note':'Historical production contract snapshot; current freeze overrides its old generation permission.'})
prepared=[]
for q in sorted((Z/'native').glob('r08_c06*.request.json')):
 png=q.with_name(q.name.replace('.request.json','.png'))
 if not png.exists():prepared.append({'request':ref(q),'state':'prepared_without_successful_output_not_in_flight','note':'No pending generation call; retain as historical prepared request.'})
core=lambda name:ref(Z/'qa'/name)
latest={'status':'working_candidate_NOT_accepted_NOT_internal_QA_passed','context':core('repair-r08_c06-internal-v2-context-native.png'),'candidate':core('repair-r08_c06-internal-v2-candidate-4096.png'),'trace':core('repair-r08_c06-internal-v2-trace.json'),'manifest':core('repair-r08_c06-internal-v2.manifest.json'),'qaIndex':core('repair-r08_c06-internal-v2-qa-index.json')}
report={
 'schemaVersion':1,'agent':'/root/art_qa','purpose':'Local migration freeze only; no new art, repair, composition, QA or Git after freeze.',
 'freezeObservedAtUtc':'2026-10-12T03:17:52Z','freezeObservedAtAmericaNewYork':'2026-10-11T23:17:52-04:00','reportWrittenAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'productionStopped':True,'newGenerationAuthorized':False,'inFlightRequests':[],'inFlightCount':0,'inFlightZeroConfirmed':True,'inFlightEvidence':'All invoked image_gen calls completed and their successful outputs were copied before freeze; all composition sessions returned exit code 0. No queued or pending tool cell remains in this agent.',
 'unSavedSuccessfulOutputs':[],'unSavedSuccessfulCount':0,'successCopyVerificationProblems':problems,
 'r08c06':{'coordinateCoverage':'16/16','savedNativePngCount':len(outputs),'productionPatchPngIncludingRejectedCount':sum('_repair_' not in x['relativePath'] for x in outputs),'repairNativePngCount':sum('_repair_' in x['relativePath'] for x in outputs),'acceptedContext':None,'latestWorking':latest,'baseAssembly':core('full-tile-r08_c06-assembly.json'),'initialQa':core('repair-r08_c06-initial-qa.json'),'priorTrialV1Trace':core('repair-r08_c06-internal-v1-trace.json'),'southJoinStatus':'not started','southAnchor':core('block2x2-r09r10c05c06-v1-r09_c06-context-native.png')},
 'knownRepairBreakpointsFromPreFreezeInspection':[
  'Latest v2 is incomplete and must not be exported as passed. H upper paving partial closed mask introduced a new slab/texture cut at its left boundary; needs future whole-slab-aware source selection or new repair after user resumes.',
  'A lantern geometry and blue-tip duplication fixed. v2 expanded right mask removed the obvious background triangular cut seen in v1; still requires final affected-seam review with H interaction.',
  'B red sign whole-object mask fixed original horizontal offset. v2 polygon leaves a tiny red triangular remnant at bottom-right near the canopy/tassel; future mask adjustment needed.',
  'C/D blue canopy continuity looked smooth in both v1 final native crops; same native sources and core selections retained in v2, but full final affected-seam review not completed.',
  'E v1 fixed stepped canopy edge but added a lower blue patch boundary; v2 narrowed polygon has not been viewed.',
  'F gold fascia v1 introduced boundary offset; v2 fresh native repair and narrower mask saved, v2 finalcrop not yet viewed.',
  'G wood tabletop v1 boundary was still visible; v2 full-object polygon expansion saved, v2 finalcrop not yet viewed.',
  'Initial 39/39 native QA images viewed before repair. v1 all 7 finalcrops viewed. v2 only H/A/B finalcrops viewed before freeze; 14/39 original QA crops are pixel-identical and 25 updated crops exist but are not fully reviewed.',
  'Red sign support foot and original h3072 stone paving confirmed continuous before freeze; no extra repair needed.',
  'r08c06 south join to r09c06 latest 7cda883269fefa3b54c32a6c6720b97fe3c04710ba94a98b632aef9253839e55 remains outstanding.',
  'r08c05 continuation has not started. Earlier authorization was withdrawn by migration freeze.'
 ],
 'savedNativeOutputs':outputs,'preparedNotInvokedRequests':prepared,'necessaryExternalReferences':external_map,
 'priorCompletedWork':{'c06c07FinalPrefix':'qa/pair-r09c06-c07-final-v5','trace':core('pair-r09c06-c07-final-v5-trace.json'),'note':'Completed and handed to root previously. Root owns later canonical/index updates; do not replace current r09c06 with earlier c06/c07-only context.'},
 'portabilityNotes':['Keep all southwest native, layout-only, qa, tools, prompts, requests, receipts, traces, masks, previews and rejected originals. Do not clean files.','Historical JSON uses absolute D:/work/image and C:/Users/luyua paths. Use this original-to-archive map on another computer without rewriting existing provenance.','Builtin generated originals in C:/Users/luyua/.codex/generated_images are duplicates of the 27 verified saved native PNGs listed here; no unique successful output remains only there.','No Git/index/commit/push operation performed by this agent.'],
 'lastNativeGeneratedAtUtc':max((x.get('generatedAt') or '' for x in outputs),default='')
}
freeze.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':ref(freeze),'savedNativePngCount':len(outputs),'problems':problems,'unsavedSuccessful':0,'inFlight':0,'externalArchivedCount':len(external_map),'preparedNotInvokedCount':len(prepared),'latest':latest,'lastNativeGeneratedAtUtc':report['lastNativeGeneratedAtUtc']},ensure_ascii=False))

