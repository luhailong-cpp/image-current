import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
from datetime import datetime,timezone
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
children=[]
for name in ['art_qa','finish_r10c05','stair_rebuild']:
 p=z/'qa'/(name+'-migration-freeze-20261011.json');r=read(p);children.append({'id':name,'receipt':ref(p),'archiveReceipt':r})
lp=z/'current-tile-ledger.json';ledger=read(lp)
for e in ledger['tiles']:
 if e['tile']=='r10_c07':
  tp=z/'qa/repair-r10_c07-v2-trace.json';tr=read(tp);e.update({'current4096':tr['candidate'],'nativeContext':tr['context'],'sourceTrace':ref(tp),'internalQa':'passed','knownSharedEdgesQa':'joint_pending_repairs','artAudit':ref(z/'qa/r10_c07-internal-visual-audit-v2.json'),'resumeBreakpoint':'block2x2-r09r10c06c07-v1 reviewed 9/21; lamp post color band and central dead-end grout pending, no repair request started.'})
 if e['tile']=='r08_c06':
  tp=z/'qa/repair-r08_c06-internal-v2-trace.json'
  if tp.exists():
   tr=read(tp);e.update({'current4096':tr.get('candidate',tr.get('output')),'nativeContext':tr.get('context'),'sourceTrace':ref(tp),'internalQa':'repairs_pending_final_review','knownSharedEdgesQa':'pending','resumeBreakpoint':'Use child art_qa migration receipt for exact repair mask and visual-review breakpoint; do not restart from base assembly.'})
 if e['tile']=='r11_c06':e.update({'internalQa':'pending','knownSharedEdgesQa':'pending','resumeBreakpoint':'All 16 native patches saved, p01_03 v2 selected; full assembly and 39 QA saved but not reviewed; north join pending.'})
 if e['tile']=='r10_c03':e['resumeBreakpoint']='10/16 native slots saved; p03_02 has guide/request only; then p03_01 and all row4 remain. No candidate assembly.'
counts={'targetTiles':49,'fullCoverageCoordinates':sum(e['coverage']=='full' for e in ledger['tiles']),'candidate4096Coordinates':sum(bool(e['current4096']) for e in ledger['tiles']),'internalPassedCoordinates':sum(e['internalQa']=='passed' for e in ledger['tiles']),'artExportCoordinates':sum(e.get('artExport',False) for e in ledger['tiles']),'nativeSlots':sum(e['nativeSlots'] for e in ledger['tiles']),'outerEdgesPendingCoordinates':sum(e['outerEdgesPending'] for e in ledger['tiles'])}
now=datetime.now(timezone.utc).isoformat();ledger.update({'updatedAtUtc':now,'counts':counts,'status':'frozen_for_migration'});prod.write(lp,ledger)
pp=z/'progress.json';p=read(pp);p.update({'status':'frozen_for_migration','updatedAtUtc':now,'candidate4kCount':counts['candidate4096Coordinates'],'fullCoverage4kCount':counts['fullCoverageCoordinates'],'internalQaPassed4kCount':counts['internalPassedCoordinates'],'complete4kCount':counts['artExportCoordinates'],'artAccepted4kCount':counts['artExportCoordinates'],'remainingMissingCoverageCount':49-counts['fullCoverageCoordinates'],'remainingInternalQaCount':49-counts['internalPassedCoordinates'],'remainingArtAcceptanceCount':49-counts['artExportCoordinates'],'currentTileLedger':ref(lp),'candidate4kPaths':[e['current4096']['path'] for e in ledger['tiles'] if e['current4096']],'nextStep':'Frozen. Resume only after user authorizes work on new computer; consult migration-freeze-20261011.json and child receipts.'});prod.write(pp,p)
fp=z/'migration-freeze-20261011.json';f=read(fp);f.update({'status':'frozen_archived_no_inflight','finalizedAtUtc':now,'inFlightImageRequests':0,'unsavedSuccessfulOutputs':[],'children':children,'counts':counts,'currentTileLedger':ref(lp),'currentAdoptedIndex':{**ref(z/'art-delivery-index.json'),'artAcceptedTiles':counts['artExportCoordinates'],'targetTiles':49},'progress':ref(pp),'remainingCoordinatesWithoutCompleteCoverage':[e['tile'] for e in ledger['tiles'] if e['coverage']!='full'],'remainingCoordinatesWithoutArtAcceptance':[e['tile'] for e in ledger['tiles'] if not e.get('artExport')],'allCurrentCoordinates':ledger['tiles'],'referenceInventory':ref(z/'migration-reference-inventory-20261011.json'),'externalReferencesStatus':'No unique outside-workspace image reference required by native requests. Four shared D:/work/image references inventoried; byte-exact portable copies are in migration-stair-rebuild-20261011/external-references. Original C: generated images preserved; successful output copies and receipts saved locally.','relocationNotes':'Keep all southwest native, QA, tiles/history, reference archives, sidecars and scripts; also carry parent production-contract.json and shared style/layout references listed in inventory. Paths in existing JSON are absolute to old D:/work/image; preserve root mapping or rebase paths using recorded hashes. No art generation, new composition, new visual review, Git operation or deletion performed during freeze.'});prod.write(fp,f)
print(json.dumps({'freeze':ref(fp),'counts':counts,'inFlightImageRequests':0,'unsavedSuccessfulOutputs':0}))
