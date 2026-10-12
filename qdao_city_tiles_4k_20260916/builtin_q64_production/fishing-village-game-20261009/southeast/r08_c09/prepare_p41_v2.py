from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((T/'p41-v1.request.json').read_text(encoding='utf-8-sig'))
base=Path(old['referenced_image_paths'][0]);a=Image.open(base).convert('RGBA')
s=T.parent/'r09_c09/processed/colorpass-20261012-v1/p11-colorpass.png';n=Image.open(s).convert('RGBA')
# Input constraint only: establish the exact same vertical post silhouettes x568..704.
# Repeated native strip is a geometry/material guide, not selected final art.
for y in range(0,1139,115):a.paste(n.crop((568,115,704,115+min(115,1139-y))),(568,y))
# Remove only obsolete blurred shaft extension from the input; it is a repairable hole.
alpha=a.getchannel('A');alpha.paste(0,(390,0,568,1139));a.putalpha(alpha)
out=T/'layout-only/p41-v2-post-core-guide.png';a.save(out)
prompt=old['prompt']+'\nImage 1 now includes a transparent guide hole where obsolete blurred background touched the pole. Fill that hole with the existing stone ground only. The straight crisp wood shaft immediately on its right is the required post width and position: preserve its left and right vertical contours exactly for its whole height. Its repeated material bands are guide-only and must become coherent NEW natural wood grain; do not change its shape or width. Keep the red rectangular lantern on the far left and the round red lantern on the right at their exact existing positions. Connect them to the unchanged gold endcaps below. No horizontal crossbar is visible in this close crop; do not add one.'
req={**old,'prompt':prompt,'referenced_image_paths':[str(out)]+old['referenced_image_paths'][1:]}
req['referenceEvidence']=[dict(path=p,sha256=sha(p),role=req['referenceRoles'][str(i)]) for i,p in enumerate(req['referenced_image_paths'],1)]
(T/'p41-v2.prompt.txt').write_bytes(prompt.encode('utf-8'))
(T/'p41-v2.request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
(T/'native/p41-v1.rejection.json').write_text(json.dumps(dict(status='rejected_not_selected',reason='Shaft at left x430 fails exact fixed lower neighbor contour x568; source gold/paving also drifted. Preserve candidate and regenerate exact-shaft guide.',selected=False),indent=2),encoding='utf-8')
der=dict(file=str(out),sha256=sha(out),classification='input only, no final art reuse',operations=['unscaled repeated real shaft strip to establish straight x568..704 guide silhouettes','transparent obsolete blurred background hole x390..568 y0..1139'],derivedFrom=[dict(file=str(base),sha256=sha(base)),dict(file=str(s),sha256=sha(s))],nativePixels=1254,geometryFixedAtLowerNeighbor=True)
Path(str(out)+'.derivation.json').write_text(json.dumps(der,indent=2),encoding='utf-8')
print(json.dumps(dict(target=str(out),request=str(T/'p41-v2.request.json'))))
