from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
notes={
 'cream_band_join':'Full 1254 native crop inspected. Cream plaster and door head beam continuous; no former horizontal stripe or blind end. Door moulding and gold bracket remain coherent.',
 'door_lower_continuity':'Full 1254 native crop inspected. Lower door moulding meets side posts; sill and two stone steps have continuous edges without the former offset.',
 'side_plaster_continuity':'Full 1254 native crop inspected. Side wall plaster and red horizontal beams continuous; tree occlusion and paving contours coherent.'
}
out=Z/'qa/r07_c03_three_repairs_independent_connected_20261013.json'
items=[]
for name,note in notes.items():
 p=Z/'qa'/f'r07_c03_{name}_mask_v1/combined_native_crop.png'
 items.append(dict(name=name,image=dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),nativeSize=[1254,1254],resizedForReview=False,visualGeometry='pass',note=note))
with out.open('x',encoding='utf8') as f:json.dump(dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='connected_continuation',status='three_local_geometry_reviews_passed_whole_tile_pending',items=items,formalTileAcceptance=False),f,indent=2)
print(str(out))
