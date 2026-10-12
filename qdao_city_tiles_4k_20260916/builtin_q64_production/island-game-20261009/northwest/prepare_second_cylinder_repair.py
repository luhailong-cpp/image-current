from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stem='r03_c03_repair_second_cylinder_a01'; box=[1670,2220,2924,3474]
base=Z/'tiles/r03_c03_candidate-v1_4096.png'; assembly=base.with_suffix('.assembly.json')
im=Image.open(base).convert('RGB');assert im.size==(4096,4096)
target=Z/'guides'/f'{stem}.native-crop.png';assert not target.exists();im.crop(box).save(target)
refs=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
inputs=[dict(path=target.as_posix(),sha256=sha(target),nativeSize=[1254,1254],role='edit target: exact unresampled1254 crop of fully traced native4096 candidate; entire second cylinder with visible seams',derivedFrom=dict(path=base.as_posix(),sha256=sha(base),assemblyRecord=assembly.as_posix(),assemblySha256=sha(assembly),cropBox=box,resized=False))]+refs
rec=dict(stem=stem,tileId='r03_c03',tileCropBox=box,globalBox=[box[0]+8192,box[1]+8192,box[2]+8192,box[3]+8192],nativeSize=[1254,1254],inputs=inputs,operation='exact unresampled crop of assembled native art for builtin precise local edit',layoutPixelsForbiddenInFinal=True,isFinalArt=False)
for suffix,value in [('input',rec),('references',dict(inputs=inputs))]:
 (Z/'guides'/f'{stem}.{suffix}.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(target.as_posix())

