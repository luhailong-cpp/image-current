from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rp=T/'p31-v1.request.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));b=Path(r['referenced_image_paths'][0]);a=Image.open(b).convert('RGBA');s=T/'native/p41-v4.png';n=Image.open(s).convert('RGBA')
for y in range(990,1139,115):a.paste(n.crop((568,115,704,115+min(115,1139-y))),(568,y))
alpha=a.getchannel('A');alpha.paste(0,(390,1005,568,1139));a.putalpha(alpha)
out=T/'layout-only/p31-v1-post-conditioned.png';a.save(out)
r['referenced_image_paths'][0]=str(out);r['prompt']+='\nThe existing post shaft at the bottom is fixed x568..704. Continue it exactly straight to the existing horizontal lantern arm, retaining that width and centerline; center the existing upper finial over this same shaft. Fill only the small transparent obsolete blurred shaft area to its left with stone paving. No extra lantern or object; only the existing finial, wood crossarm with existing attachments, partial existing lantern tops in bottomframe, flat stone background. Keep actual native bottom contour endpoints exactly.'
r['referenceEvidence']=[dict(path=p,sha256=sha(p),role=r['referenceRoles'][str(i)]) for i,p in enumerate(r['referenced_image_paths'],1)]
rp.write_text(json.dumps(r,indent=2),encoding='utf-8');(T/'p31-v1.prompt.txt').write_bytes(r['prompt'].encode('utf-8'))
Path(str(out)+'.derivation.json').write_text(json.dumps(dict(file=str(out),sha256=sha(out),classification='input only, not selected final artwork',derivedFrom=[dict(file=str(b),sha256=sha(b)),dict(file=str(s),sha256=sha(s))],operation='Exact unscaled projected lower shaft guide plus alpha hole; original layout elsewhere',alphaHole=[390,1005,568,1139]),indent=2),encoding='utf-8')
print(str(out))
