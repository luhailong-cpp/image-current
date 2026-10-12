from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
T=Path(__file__).resolve().parent;Q=T/'qa/full-native-finish-20261013-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=Q/'candidate-4096.png';box=[397,1421,1651,2675];im=Image.open(src).crop(box)
dst=T/'layout-only/p31-ne-joint-v1.png';assert not dst.exists();im.save(dst)
target=T/'p31-ne-joint-v1.request.json'
prompt="""Use case: precise-object-edit. Repair this exact1254x1254 crop of contiguous Daoist Q hand-painted gray stone pavement. There is an obvious bad square lower-left quadrant: at x627 and y627 its slab joints and brush density abruptly change from the surrounding pavement. Repaint ONLY the PAVEMENT of this lower-left quadrant so every existing large slab joint continues cleanly across x627 from the right and y627 from above, with consistent stone material and continuous daylight. Treat the other three quadrants as fixed authoritative native context. Continue their large bluegray slab shapes into the lower-left; no miniature grid, no square texture boundary, no straight band. Keep every pixel coordinate in the other three quadrants and keep the visible gold finial/column portion at bottom-left exactly as it is; it must not move or change shape. The crop's outermost80pixels are fixed context on all four sides. Preserve endpoints on these edges exactly. Repair cracks and textures naturally, no blur/feather/shadow concealment, no new object. Output this exact crop in native1254x1254 RGB, no reframe, labels, grid or border."""
req={'prompt':prompt,'referenced_image_paths':[str(dst)],'transparent_background':False,'route':'builtin','tool':'image_gen__imagegen','submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'createdAt':datetime.now(timezone.utc).isoformat(),'referenceEvidence':[{'path':str(dst),'sha256':sha(dst),'role':'Unscaled native exact selected-core joint crop; all context real'}],'jointGlobalBox':[33165,30093,34419,31347],'jointTileBox':box,'sourceCandidate':str(src),'sourceSha256':sha(src)}
assert not target.exists();target.write_text(json.dumps(req,indent=2),encoding='utf-8')
(T/'p31-ne-joint-v1.prompt.txt').write_text(prompt,encoding='utf-8')
Path(str(dst)+'.derivation.json').write_text(json.dumps({'source':str(src),'sourceSha256':sha(src),'crop':box,'operation':'exact unscaled native-core crop, input guide only','sha256':sha(dst)},indent=2),encoding='utf-8')

