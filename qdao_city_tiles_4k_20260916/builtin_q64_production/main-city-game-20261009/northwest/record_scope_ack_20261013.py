from pathlib import Path
from datetime import datetime, timezone
import json
import production_v2 as p
root = p.ZONE.parents[3]
f = root/'docs/MAP_PARALLEL_SPLIT_20261013.json'
b = next(b for b in p.read(f)['batches'] if b['key']=='city-yamen-north')
assert b['status']=='allocated_root_reserved'
assert b['owner']=='01a12075-f5cf-7c30-9edc-ceb79ed8cfbd'
conflicts = [t for t in b['tiles'] if (p.ZONE/t).exists()]
assert not conflicts, conflicts
ack = root/b['ownerAckFile']
assert not ack.exists()
assert ack.resolve() == (root/'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/coordination/city-yamen-north.owner-ack.json').resolve()
data = {'ownerThreadId':b['owner'],'reservedTiles':b['tiles'],'workerThreadId':b['worker'],'ready':True,'timestamp':datetime.now(timezone.utc).isoformat(),'activeConflicts':[],'inFlightSaved':True,'inFlightAtReservedCoordinates':[],'sourceEvidence':'All four original owner tile directories are absent. Root and active agents are restricted to r07_c05, r07_c06 and r06_c03. Updated refresh_progress.py excludes current allocated_root_reserved tiles.','neighborRevisionStability':{'reservedCoordinatesRemainUnwrittenByOwner':True,'noCurrentNativeNeighborAtReservedCoordinates':True,'neighborChangesMustUseVersionedFiles':True},'manifest':{'file':str(f),'sha256':p.sha(f)},'existingDeliveryPackagesUnchanged':True}
ack.parent.mkdir(parents=True, exist_ok=True)
with ack.open('x', encoding='utf-8') as stream:
    json.dump(data, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(ack)
