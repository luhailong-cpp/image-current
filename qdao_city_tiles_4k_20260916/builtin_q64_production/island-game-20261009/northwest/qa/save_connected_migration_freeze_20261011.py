"""Metadata-only freeze archive; no art, QA rerun, or acceptance mutation."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=str(Path(p).resolve()),sha256=sha(p))
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
mp=Z/'qa/connected-r04-r05-current-v5.manifest.json';manifest=read(mp)
for item in manifest['tiles']:
 for k in ('image','record'):assert sha(item[k]['path'])==item[k]['sha256']
stems=['cross_r04r05_c03c04_lantern_body_a01','cross_r04r05_c03_pillar_tone_a01','cross_r05_c03c04_jar_base_a01','cross_r04r05_c04_paving_right_a01']
saved=[]
for i,s in enumerate(stems):
 raw=Z/'native'/f'{s}.png'
 # First generation has the same submitted prompt made absolute in a preserved sibling evidence record.
 if i==0:gp=Z/'native'/f'{s}.png.generation-evidence-v2.json'
 else:gp=Z/'native'/f'{s}.png.generation.json'
 g=read(gp);receipt=Z/'receipts'/f'{s}.receipt.json';prompt=Z/'prompts'/f'{s}.prompt.txt';r=read(receipt)
 assert sha(raw)==g['sha256']==g['sourceOutputSha256']
 assert sha(prompt)==g['promptSha256'] and prompt.read_text(encoding='utf8')==r['submitted']['promptText']
 saved.append(dict(stem=s,raw=info(raw),generation=info(gp),receipt=info(receipt),prompt=info(prompt),sourceOutputPath=g['sourceOutputPath'],sourceOutputExists=Path(g['sourceOutputPath']).is_file(),mask=info(Z/'qa'/f'{s}_mask_v1'/'source_selection_mask.png'),combined=info(Z/'qa'/f'{s}_mask_v1'/'combined_native_crop.png'),completedVisualReview=info(Z/'qa'/f'{s}_mask_v1'/'visual_review.json')))
# Collect referenced absolute paths from the selected ancestry metadata without image inspection or revalidation.
seen=set();queue=[mp]+[Path(t['record']['path']) for t in manifest['tiles']];dependencies={}
def add(value,declared=None):
 if not isinstance(value,str) or not re.match(r'^[A-Za-z]:[\\/]',value):return
 p=Path(value).resolve();key=str(p)
 d=dependencies.setdefault(key,dict(path=key,declaredSha256=[]))
 if declared and declared not in d['declaredSha256']:d['declaredSha256'].append(declared)
 if p.suffix.lower()=='.json' and p.is_relative_to(Z) and p.is_file() and key not in seen:queue.append(p)
def visit(obj):
 if isinstance(obj,dict):
  add(obj.get('path'),obj.get('sha256'))
  add(obj.get('sourceOutputPath'),obj.get('sourceOutputSha256'))
  for k,v in obj.items():
   if isinstance(v,str):add(v,obj.get(k+'Sha256'))
   else:visit(v)
 elif isinstance(obj,list):
  for v in obj:visit(v)
while queue:
 p=queue.pop();key=str(p.resolve())
 if key in seen:continue
 seen.add(key);visit(read(p))
external=[]
for key,d in sorted(dependencies.items()):
 p=Path(key)
 if p.is_relative_to(Z):continue
 d['existsAtFreeze']=p.is_file();d['byteCount']=p.stat().st_size if p.is_file() else None;external.append(d)
replay=Z/'qa/connected-r04-r05-final-v1/pixel-replay-and-qa.json';rp=read(replay)
assert len(rp['nativeScaleCrops'])==17 and rp['verifiedPixelCount']==67108864
out=Z/'qa/connected-migration-freeze-20261011.json'
report=dict(schemaVersion=1,frozenAtUtc=datetime.now(timezone.utc).isoformat(),status='migration_frozen_no_further_art_or_acceptance_work',owner='/root/connected_closure',scope='r04/r05 x c03/c04 latest actually applied four-tile candidate',currentLastAppliedManifest=info(mp),currentLastAppliedTiles=manifest['tiles'],previousCompletedGroupManifest=info(Z/'qa/connected-closure-current-v5.manifest.json'),previousCompletedGroupClosure=info(Z/'qa/connected-closure-final-v1/closure.json'),successfulSavedNativeOutputs=saved,inflightCount=0,unarchivedUniqueOutputCount=0,activeImageGenerationCalls=0,pendingImageGenerationCalls=0,processNotes=['All four image_gen calls returned and were copied into native with matching hash, receipt and exact prompt.','Build session1840 and final QA export session8869 completed with exit0.','Strict memo server75699 completed its last audit request; attempting to close at freeze returned Unknown process id, so no resumable server remains.'],completedBeforeFreeze=dict(sharedBoundaryNativeQaPassed=17,changedNativeQaReopenedAndPassed=8,unchangedQaExactPixelEqualToPreviouslyViewedPassedCrops=9,wholeLanternNativeCropsPassed=2,wholeLanternNote='Native1254 body plus native700 bottom/tassel crop were both viewed and passed immediately before freeze, covering cap/body/gold mount/bead/full single tassel.',repairCombinedIndependentReviewsPassed=4,independentRepairReviewer='/root',fullOrderedPixelReplay=info(replay),verifiedPixelCount=67108864,orderedRepairOverlapPixels=474,strictFinalRecursiveAuditInput=info(Z/'guides/connected_r04_r05_final_native_audit_a01.input.json'),strictInvocationMemo=dict(hits=124,misses=64,rehashes=65125,dependencyChanges=0)),pendingAtFreeze=['Final shared-boundary closure.json was not yet created; do not treat this freeze record as new acceptance.','Outer neighbors still require their separate seam/zone closure.','Parent owns root progress and authoritative region selection; neither was modified by this agent.'],formalAcceptedCount=0,southBoundaryHandoff=dict(edgeDifferenceEvidence=info(Z/'qa/connected-r04-r05-v1.input-edge-differences.json'),r05_c03='Initial connected selection changed south edge x4089..4095 inclusive, 7 pixels, relative to internal v8; all four subsequent repairs preserve this connected south edge.',r05_c04='South edge exactly equals internal v4, including its previously disclosed x954..1483 update from earlier internal repair.',nextGroup='Use currentLastAppliedManifest r05_c03 and r05_c04 for future r05/r06 connection. r04 north edges equal previously passed upper-group inputs.'),preview=rp['previewOnly'],nativeQaDirectory=str(Z/'qa/connected-r04-r05-final-v1'),preservation='All versions, raws, prompts, receipts, masks, guides, source-selection archives, provenance and previews retained; no deletion or Git operation.',dependencyCollectionMethod='Metadata-only absolute file references reachable through selected JSON ancestry; declared hashes retained without rehashing or re-reviewing historical dependency images.',visitedAncestryJsonCount=len(seen),externalDependencyCount=len(external),externalDependencies=external,missingExternalDependencyCount=sum(not d['existsAtFreeze'] for d in external),historicalMissingReferences='Previously disclosed retired style reference PNG bytes may be unavailable. Existing historical records and hashes are preserved; no replacement or provenance rewrite performed.')
with out.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(freeze=info(out),inflightCount=0,unarchivedUniqueOutputCount=0,visitedAncestryJsonCount=len(seen),externalDependencyCount=len(external),missingExternalDependencyCount=report['missingExternalDependencyCount'],currentLastAppliedTiles=manifest['tiles']),ensure_ascii=False,indent=2))
