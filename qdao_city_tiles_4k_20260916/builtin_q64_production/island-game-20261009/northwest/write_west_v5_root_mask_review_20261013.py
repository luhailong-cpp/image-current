from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
z=Path(__file__).resolve().parent
info=lambda p:dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
p=z/'qa/r05_c02_v5_root_independent_mask_review_20261013.json'
with p.open('x',encoding='utf8') as f:json.dump(dict(reviewedAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='root',communication='collaboration message received by west_continuation',candidate=info(z/'tiles/r05_c02_candidate-v5_4096.png'),crop=info(z/'qa/r05_c02_southwest_ground_join_a01_union_mask_v2/combined_native_crop.png'),nativeViewedSize=[1254,1254],status='PASS_local_geometry',note='Root independently viewed full1254: middle-foot cloud moulding and bottom circular bands continuous; primary foot-side stone joints connected.',southEdgeChanged=True,acceptanceScope='This repair crop only; not whole map/formal tile acceptance'),f,indent=2)
print(info(p))

