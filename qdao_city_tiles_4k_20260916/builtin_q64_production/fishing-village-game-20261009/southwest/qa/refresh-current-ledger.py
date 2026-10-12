import sys
sys.dont_write_bytecode=True
import json,re,importlib.util
from pathlib import Path
from datetime import datetime,timezone
z=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(spec);spec.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':prod.sha(p)}
ip=z/'art-delivery-index.json';idx=read(ip);accepted={e['tile']:e for e in idx['artAccepted']}
lp=z/'current-tile-ledger.json';prior=read(lp) if lp.exists() else {};old={e['tile']:e for e in prior.get('tiles',[])}
slots={};records=list((z/'native').glob('*.png.generation.json'))
for rp in records:
 r=read(rp);status=r.get('status','')
 if any(s in status for s in ['superseded','rejected','frozen']):continue
 m=re.match(r'(r\d{2}_c\d{2})_(p\d{2}_\d{2})_v(\d+)\.png',rp.name)
 if not m:continue
 if r.get('coordinates',{}).get('role','').startswith('localized native seam repair'):continue
 slots.setdefault(m[1],set()).add(m[2])
entries=[]
split=read(z.parents[3]/'docs'/'MAP_PARALLEL_SPLIT_20261013.json')
delegated=sorted({tile for batch in split['batches'] if batch.get('owner')=='01a1216d-3f65-7331-939e-0ea73b19f3bf' and batch.get('status')=='allocated_root_reserved' for tile in batch['tiles']})
target=49-len(delegated)
for rr in range(8,15):
 for cc in range(1,8):
  if f'r{rr:02d}_c{cc:02d}' in delegated:continue
  tile=f'r{rr:02d}_c{cc:02d}';n=len(slots.get(tile,set()));e={'tile':tile,'nativeSlots':n,'coverage':'full' if n==16 else 'partial' if n else 'missing','current4096':None,'internalQa':'pending','knownSharedEdgesQa':'pending','outerEdgesPending':True,'artExport':False}
  if tile in old and old[tile].get('current4096'):
   e.update({k:v for k,v in old[tile].items() if k not in ['nativeSlots','coverage']})
  if tile in accepted:
   a=accepted[tile];e.update({'nativeSlots':16,'coverage':'full','current4096':a['file'],'internalQa':'passed','knownSharedEdgesQa':'passed_for_recorded_edges','artExport':True,'sourceTrace':a['sourceTrace'],'artAudit':a['artAudit'],'nativeContext':a['nativeContext']})
  elif n==16:
   ap=z/'qa'/f'full-tile-{tile}-assembly.json'
   if ap.exists() and not e['current4096']:
    a=read(ap);out=a.get('output',{})
    if out.get('path') and Path(out['path']).exists():e.update({'current4096':out,'sourceTrace':ref(ap)})
  entries.append(e)
counts={'targetTiles':target,'originalTargetTiles':49,'delegatedTileCount':len(delegated),'fullCoverageCoordinates':sum(e['coverage']=='full' for e in entries),'candidate4096Coordinates':sum(bool(e['current4096']) for e in entries),'internalPassedCoordinates':sum(e['internalQa']=='passed' for e in entries),'artExportCoordinates':len(accepted),'nativeSlots':sum(e['nativeSlots'] for e in entries),'outerEdgesPendingCoordinates':sum(e['outerEdgesPending'] for e in entries)}
now=datetime.now(timezone.utc).isoformat();ledger={'updatedAtUtc':now,'targetTiles':target,'originalTargetTiles':49,'delegatedTiles':delegated,'splitManifest':ref(z.parents[3]/'docs'/'MAP_PARALLEL_SPLIT_20261013.json'),'tiles':entries,'counts':counts,'countingPolicy':'One current entry per owned coordinate; historical versions and currently delegated coordinates excluded. Art export reflects recorded internal/shared-edge audits; other outer edges can remain pending. No runtime gate.'};prod.write(lp,ledger)
p=read(z/'progress.json');p.update({'updatedAtUtc':now,'complete4kCount':len(accepted),'artAccepted4kCount':len(accepted),'candidate4kCount':counts['candidate4096Coordinates'],'fullCoverage4kCount':counts['fullCoverageCoordinates'],'internalQaPassed4kCount':counts['internalPassedCoordinates'],'remainingMissingCoverageCount':49-counts['fullCoverageCoordinates'],'remainingInternalQaCount':49-counts['internalPassedCoordinates'],'currentTileLedger':ref(lp),'artDeliveryIndex':ip.as_posix(),'generatedNativeCount':len(records),'usableNativeSlotCount':counts['nativeSlots'],'candidate4kPaths':[e['current4096']['path'] for e in entries if e['current4096']],'runtimeGateActive':False})
p.update({'fullyCovered4kCount':counts['fullCoverageCoordinates'],'internalPassed4kCount':counts['internalPassedCoordinates'],'internalPassedTiles':[e['tile'] for e in entries if e['internalQa']=='passed'],'internalCompleteTiles':[e['tile'] for e in entries if e['internalQa']=='passed'],'remainingInternal4kCount':49-counts['internalPassedCoordinates'],'missingCoverage4kCount':49-counts['fullCoverageCoordinates'],'currentSelectedNativeSlotCount':counts['nativeSlots'],'usableNativeCount':counts['nativeSlots'],'missingNativeCoreSlotCount':49*16-counts['nativeSlots'],'exportedInternalCandidate4kCount':len(accepted),'remainingArtAcceptanceCount':49-len(accepted),'currentCoverageByTile':{e['tile']:e['nativeSlots'] for e in entries if e['nativeSlots']},'candidate4kFiles':p['candidate4kPaths'],'internalQaPending':[e['tile'] for e in entries if e['coverage']=='full' and e['internalQa']!='passed']})
p.update({'target4kCount':target,'originalTarget4kCount':49,'delegatedTiles':delegated,'remainingMissingCoverageCount':target-counts['fullCoverageCoordinates'],'remainingInternalQaCount':target-counts['internalPassedCoordinates'],'remainingInternal4kCount':target-counts['internalPassedCoordinates'],'missingCoverage4kCount':target-counts['fullCoverageCoordinates'],'missingNativeCoreSlotCount':target*16-counts['nativeSlots'],'remainingArtAcceptanceCount':target-len(accepted)})
prod.write(z/'progress.json',p)
print(json.dumps(counts))
