import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
z=Path(__file__).resolve().parent.parent
sp=importlib.util.spec_from_file_location('prod',z/'production.py');prod=importlib.util.module_from_spec(sp);sp.loader.exec_module(prod)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
l=read(z/'current-tile-ledger.json');c=l['counts'];target=l['targetTiles'];pending=[e['tile'] for e in l['tiles'] if e['coverage']=='full' and e['internalQa']!='passed']
r={'updatedAtUtc':prod.now(),'targetUnique4kCoordinates':target,'originalTargetCoordinates':49,'delegatedCoordinates':l['delegatedTiles'],'native16Complete4kCandidateCoordinates':c['fullCoverageCoordinates'],'saved4096CandidateCoordinates':c['candidate4096Coordinates'],'internalCheckPassedCoordinates':c['internalPassedCoordinates'],'stillMissingNativeCoordinates':target-c['fullCoverageCoordinates'],'existingCompleteArtPendingRepairOrCheckCoordinates':len(pending),'pendingRepairOrCheckTiles':pending,'exportedArtCoordinates':c['artExportCoordinates'],'nativeCoreSlotsReady':c['nativeSlots'],'nativeCoreSlotsMissing':target*16-c['nativeSlots'],'countingPolicy':'Each currently owned coordinate counted once; six allocated coordinates excluded from this producer scope. Other workers keep independent output directories. Unavailable outside neighbors remain pending.'}
prod.write(z/'current-scope-summary.json',r)
print(json.dumps(r))
