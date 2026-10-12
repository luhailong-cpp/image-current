from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stem='r03_c03_repair_window_wall_a01'; box=[900,700,2154,1954]
base=Z/'tiles/r03_c03_candidate-v1_4096.png'; ass=base.with_suffix('.assembly.json')
crop=Z/'guides'/f'{stem}.native-crop.png'; deriv=Z/'guides'/f'{stem}.native-crop.derivation.json'
assert not crop.exists(); Image.open(base).crop(box).save(crop)
d=dict(derivedFrom=dict(path=base.as_posix(),sha256=sha(base),assemblyRecord=dict(path=ass.as_posix(),sha256=sha(ass))),cropBox=box,operation='native-coordinate crop',resizing=False,registration=False,feathering=False,colorCorrection=False,output=dict(path=crop.as_posix(),sha256=sha(crop),nativeSize=[1254,1254]))
deriv.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inputs=[dict(path=crop.as_posix(),sha256=sha(crop),nativeSize=[1254,1254],role='edit target: exact native1254 crop of traced4096 candidate; only remove window-top white wall brightness step',derivedFrom=d['derivedFrom'])]+json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
rec=dict(stem=stem,tileId='r03_c03',tileCropBox=box,globalBox=[v+8192 for v in box],nativeSize=[1254,1254],inputs=inputs,editTarget=dict(path=crop.as_posix(),sha256=sha(crop),derivationRecord=dict(path=deriv.as_posix(),sha256=sha(deriv))),operation='exact native-coordinate crop for builtin local material correction',layoutPixelsForbiddenInFinal=True,isFinalArt=False)
for suffix,value in [('input',rec),('references',dict(inputs=inputs))]:
 (Z/'guides'/f'{stem}.{suffix}.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(crop.as_posix())
