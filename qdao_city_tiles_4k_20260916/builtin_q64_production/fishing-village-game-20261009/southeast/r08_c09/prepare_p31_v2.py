from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=T/'native/p31-v1.png';s=T/'native/p41-v4.png';a=Image.open(base).convert('RGBA');n=Image.open(s).convert('RGBA')
# Input-only correction establishes one straight shaft shared with the fixed lower tile.
for y in range(740,1024,115):a.paste(n.crop((568,115,704,115+min(115,1024-y))),(568,y))
a.paste(n.crop((0,0,1254,230)),(0,1024))
alpha=a.getchannel('A')
for box in [(390,740,568,817),(390,990,568,1024)]:alpha.paste(0,box)
a.putalpha(alpha);out=T/'layout-only/p31-v2-true-straight-shaft.png';a.save(out)
old=json.loads((T/'p31-v1.request.json').read_text(encoding='utf-8-sig'))
prompt='''Use case: precise-object-edit. Image1 is an almost completed original1254x1254 native game closeup. Correct ONLY the lower wood shaft shape/material and the transparent stone holes. Keep upper existing gold finial and horizontal wooden lantern arm and all lanterns unchanged. The actual straight post shaft is the narrow dark vertical wood at x568..704, from below the existing gold cap through the bottom of this image. This is fixed genuine lower-neighbor width. Keep its exact left and right contours straight at568 and704. Never expand it leftwards. The formerly extra dark wood left of568 in transparent holes is now ONLY flat bluegray stone paving background. At y817..990 the horizontal wood arm crosses behind this narrow post; keep that arm, but change any obsolete leftward vertical wood grain there into coherent HORIZONTAL arm grain. Fill transparent holes with the same surrounding stone grout/material and do not add cast shadow stripes.
The lower230px are exact sharp genuine selected neighboring art. Keep their geometry and all existing lantern and gold ring pixels fixed. The shaft joins lower wood exactly across native cut1139; no width change, rectangle, step, duplicate outline or new object. Preserve upper gold cap silhouette; the narrow straight shaft supports it naturally. Final1254square native RGB, no camera/scale/crop/object-position change. Same clear daylight and broad crisp Daoist Q painterly material style. Image2 layout/context only,3 independent daylight materials style,4 approved Daoist Q style only. No wall, extra object, plant, building, letter, character, UI, border or watermark. Render natural new grain in repeated guide strip while retaining exact shaft silhouette.'''
req={**old,'prompt':prompt,'referenced_image_paths':[str(out)]+old['referenced_image_paths'][1:]};req['referenceEvidence']=[dict(path=p,sha256=sha(p),role=req['referenceRoles'][str(i)]) for i,p in enumerate(req['referenced_image_paths'],1)]
(T/'p31-v2.prompt.txt').write_bytes(prompt.encode('utf-8'));(T/'p31-v2.request.json').write_text(json.dumps(req,indent=2),encoding='utf-8')
Path(str(out)+'.derivation.json').write_text(json.dumps(dict(file=str(out),sha256=sha(out),classification='input only',operation='unscaled real lower230 neighbor overlap and repeated straight shaft with small alpha holes',derivedFrom=[dict(file=str(p),sha256=sha(p)) for p in [base,s]]),indent=2),encoding='utf-8')
print(str(out))
