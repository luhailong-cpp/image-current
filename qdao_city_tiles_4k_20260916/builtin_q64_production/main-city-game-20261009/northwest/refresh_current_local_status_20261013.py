from pathlib import Path
from datetime import datetime, timezone
import json, shutil, hashlib
import production_v2 as p
Z=p.ZONE
now=datetime.now(timezone.utc).isoformat()
old=p.read(Z/'progress.json')
snapshot=Z/'progress-before-local-resume-20261013.json'
if not snapshot.exists(): shutil.copyfile(Z/'progress.json',snapshot)
excluded=set(old['excludedCoordinates'])
passed=set(['r05_c04','r05_c05','r06_c04','r06_c05','r05_c06','r06_c06','r07_c04','r05_c07','r07_c05','r06_c07'])
patches=[f's{r:02d}_{c:02d}' for r in range(1,5) for c in range(1,5)]
rows=[]
for r in range(1,9):
 for c in range(1,9):
  tile=f'r{r:02d}_c{c:02d}'
  if tile in excluded: continue
  T=Z/tile; sel=p.read(T/'selection.json') if (T/'selection.json').exists() else {}
  present=[q for q in patches if p.selected_path(T,q,sel).is_file()]
  rows.append({'tile':tile,'selectedCoreCount':len(present),'missingNativePatches':[q for q in patches if q not in present],'all16Selected':len(present)==16,'currentVerifiedDelivery':tile in passed,'formalAccepted':False})
by={x['tile']:x for x in rows}
for entry in old['tiles']:
 if entry['tile'] not in by: continue
 row=by[entry['tile']]
 entry.update(selectedAvailable=row['selectedCoreCount'], selectedUsable=row['selectedCoreCount'], missingNativePatches=row['missingNativePatches'])
 if entry['tile']=='r05_c03':
  entry.update(internalQAPassed=False,formalAccepted=False)
  entry['qa']={'internalPassed':False,'formalPassed':False,'status':'reopened_native_internal_geometry_defect','evidence':str(Z/'r05_c03/reopened-repair-20261013/reopened-current-status.json')}
count=sum(x['selectedCoreCount'] for x in rows);full=sum(x['all16Selected'] for x in rows)
counts={'deduplicatedTargetTiles':56,'tilesWithAll16NativePatches':full,'internallyPassedTiles':len(passed),'tilesStillMissingNativePatches':56-full,'fullSourceTilesPendingInternalRepairOrReview':full-len(passed),'selectedUniqueNativeCores':count,'missingNativePatches':896-count,'externalPerimeterPendingDoesNotCountAsUndrawn':True}
current={'updatedAtUtc':now,'status':'incomplete_production_continuing','counts':counts,'currentPassedTileIds':sorted(passed),'reopenedTile':'r05_c03','reopenedEvidence':str(Z/'r05_c03/reopened-repair-20261013/reopened-current-status.json'),'historicalElevenPackagesUnmodified':True,'historicalElevenPackageIsNotCurrentFullAcceptance':True,'rows':rows,'wholeZoneComplete':False,'countingMethod':'Read current explicit selections plus legacy original native files at absent selection IDs. Existing ingest validation retained; no ZIP rehash, historical QA rescan or regenerated overview. Counts are native coverage, not visual acceptance.','gitMutated':False}
p.write_json(Z/'current-production-status-20261013.json',current,replace=True)
old.update(updatedAt=now,status='incomplete_production_continuing',generationToolBlocked=False,generationToolBlocker=None,generationOnHold=False,selectedAvailableNativeCount=count,selectedUsableNativeCount=count,currentScopeCounts=counts,remainingTileCountWithoutFullUsableSourceCoverage=56-full,nextStep='Continue r07_c07 missing cores, r06_c03 independent local repairs, r08_c04 full QA and local repair; r05_c03 reopened defect remains unpassed. Use current-production-status-20261013.json for current local counts.')
old['currentLocalStatus']={'file':str(Z/'current-production-status-20261013.json'),'sha256':p.sha(Z/'current-production-status-20261013.json')}
if old.get('currentVerifiedDelivery'):
 old['historicalVerifiedDelivery']=old.pop('currentVerifiedDelivery')
old['currentVerifiedDelivery']={'tileCount':10,'tiles':sorted(passed),'derivedFromHistoricalPackage':True,'excludedReopenedTiles':['r05_c03'],'historicalPackageRetained':True,'currentNewPackageCreated':False,'wholeZoneComplete':False,'outerUnfinishedNeighborsPending':True}
p.write_json(Z/'progress.json',old,replace=True)
print(json.dumps(counts))

