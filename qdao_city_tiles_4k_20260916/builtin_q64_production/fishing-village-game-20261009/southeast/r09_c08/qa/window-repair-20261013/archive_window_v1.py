from pathlib import Path
from datetime import datetime,timezone
import json,shutil,hashlib
from PIL import Image
Q=Path(__file__).resolve().parent
raw=Path(r'C:/Users/luyua/.codex/generated_images/01a13554-e65d-71e2-a119-8c3677ffd303/exec-3605720e-cf7c-40c9-bec9-23d18a812bd7.png')
p=Q/'window-v1-raw.png';assert not p.exists();shutil.copyfile(raw,p)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
with Image.open(p) as im: dims=list(im.size)
record=dict(savedAtUtc=datetime.now(timezone.utc).isoformat(),tool='image_gen__imagegen',route='builtin',
 file=str(p),sha256=sha(p),sourcePath=str(raw),nativeDimensions=dims,actualModel=None,actualQuality=None,
 prompt=str(Q/'window-v1.prompt.txt'),request=str(Q/'window-v1.request.json'),receipt=str(Q/'window-v1.receipt.json'),
 imageOperation='Byte-exact copy of actual builtin output; no resizing or editing',selected=False,
 review=dict(duplicateRemoved=True,usable=False,reason='Existing lower flower and window sill shifted up roughly 60 to 85 pixels; immutable south-neighbor geometry would not match when adopting north-only. Upper diagonal window frame also changed.'))
(Q/'window-v1-raw.png.generation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
