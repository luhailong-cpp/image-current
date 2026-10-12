from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=T/'native/p44-v1.png';left=T/'native/p43-v1.png';south=T.parent/'r09_c09/processed/colorpass-20261012-v1/p14-colorpass.png'
a=Image.open(base).convert('RGBA');l=Image.open(left).convert('RGBA');s=Image.open(south).convert('RGBA')
a.paste(l.crop((1024,0,1254,1254)),(0,0));a.paste(s.crop((0,0,1254,230)),(0,1024))
alpha=a.getchannel('A');alpha.paste(0,(230,580,1254,1024));a.putalpha(alpha)
out=T/'layout-only/p44-v2-real-lower230-guide.png';a.save(out)
old=json.loads((T/'p44-v1.request.json').read_text(encoding='utf-8-sig'))
prompt='''Use case: precise-object-edit. Fix only the transparent area of image1 at exact original1254x1254 resolution. Subject ONLY flat bluegray stone pavement, closeup of a few large painted slabs. The sharp lower230px are genuine native neighboring slabs and their grout paths are exact fixed lower endpoints. The sharp left230px are genuine native neighboring slabs and their grout paths are exact fixed left endpoints. Upper opaque stone is fixed too. Draw the missing same stone slabs in the transparent gap by tracing the ACTUAL existing grout from the bottom upwards to connect naturally into the top and left. Maintain correct grout alignment at eventual cuts115 and1139px. No rectangular line or discontinuous/missing stone joint at1139. The source lower230 has the final correct smaller slab endpoints; do not draw a different large slab across them or conceal the mismatch with blur. A natural few irregular rectangular slabs connecting those endpoints is required. Preserve opaque stone detail, bright clear daylight and broad crisp handpainted material strokes. No new objects, walls, buildings, lanterns, symbols, UI, text, watermark or border. Do not change the viewpoint, zoom, crop, rescale or render a wholemap.
Image2 fullmap layout/context only, Image3 daylight stone material style only, Image4 approved Daoist Q painterly style only. These refs do not add any content to this pavement-only crop. Output one1254square RGB native patch with fully painted sharp detail, fixed original stone silhouettes and corrected natural grout connection.'''
req={**old,'prompt':prompt,'referenced_image_paths':[str(out)]+old['referenced_image_paths'][1:]};req['referenceEvidence']=[dict(path=p,sha256=sha(p),role=req['referenceRoles'][str(i)]) for i,p in enumerate(req['referenced_image_paths'],1)]
(T/'p44-v2.prompt.txt').write_bytes(prompt.encode('utf-8'));(T/'p44-v2.request.json').write_text(json.dumps(req,indent=2),encoding='utf-8')
Path(str(out)+'.derivation.json').write_text(json.dumps(dict(file=str(out),sha256=sha(out),classification='input guide only, never final pixels',alphaHole=[230,580,1254,1024],operations=['unscaled left genuine230 native overlap','unscaled south genuine230 native overlap','transparent own-core lower repair hole'],derivedFrom=[dict(file=str(p),sha256=sha(p)) for p in [base,left,south]]),indent=2),encoding='utf-8')
print(str(out))
