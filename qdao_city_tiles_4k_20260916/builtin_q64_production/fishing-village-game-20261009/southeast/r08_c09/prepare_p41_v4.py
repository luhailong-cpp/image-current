from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=T/'native/p41-v3.png';s=T.parent/'r09_c09/processed/colorpass-20261012-v1/p11-colorpass.png';a=Image.open(base).convert('RGB');n=Image.open(s).convert('RGB')
# Visually close the guide's extraneous thirteen-pixel shaft extension.
a.paste(a.crop((535,0,553,1024)),(550,0))
for y in range(0,1024,115):a.paste(n.crop((568,115,704,115+min(115,1024-y))),(568,y))
a.paste(n.crop((0,0,1254,230)),(0,1024))
out=T/'layout-only/p41-v4-closed-straight-contour-guide.png';a.save(out)
old=json.loads((T/'p41-v3.request.json').read_text(encoding='utf-8-sig'))
prompt='''Edit image1, a completed RGB native game tile guide, at EXACT1254x1254 pixels. This is a very small contour repair. Keep the existing lantern objects and all their positions, colors, shape, material and ornaments unchanged. The dark post is exactly the straight dark shaft shown in this input: x568..704 over its whole height. Its left-side neighboring pixels at x550..567 are gray stone paving, not wood or a cast-shadow extension. Preserve that straight vertical cut exactly; do not expand the shaft or add any outline to its left. Its right edge stays704. Only make the guide material joins natural: coherent wood grain and connect stone grout where its small strip was copied. Keep the lower230px native artwork and all fixed seam endpoints unchanged, in particular shaft leftedge568, rightedge704 and gold/red lantern bases. Preserve the exact geometry and footprint and do not move anything.
Same approved clear bright-daylight Daoist Q painterly material style. Image2 fullmap layout only; Image3 independent daylight material style; Image4 approved rounded Daoist style only. Existing lanterns on flat bluegray stone ground only, no wall, crossbar, extra object, plant, character, text, glyph, watermark or border. Central core exact[115,115,1139,1139]. Return one original1254square RGB image; no framing, scaling or extra outline.'''
req={**old,'prompt':prompt,'referenced_image_paths':[str(out)]+old['referenced_image_paths'][1:]};req['referenceEvidence']=[dict(path=p,sha256=sha(p),role=req['referenceRoles'][str(i)]) for i,p in enumerate(req['referenced_image_paths'],1)]
(T/'p41-v4.prompt.txt').write_bytes(prompt.encode('utf-8'));(T/'p41-v4.request.json').write_text(json.dumps(req,indent=2),encoding='utf-8')
Path(str(out)+'.derivation.json').write_text(json.dumps(dict(file=str(out),sha256=sha(out),classification='input guide only, never final art',derivedFrom=[dict(file=str(base),sha256=sha(base)),dict(file=str(s),sha256=sha(s))],operations=['unscaled copied input paving strip eliminates extraneous shaft13px','straight shaft native-guide pixels','verified sharp genuine bottom230 input overlap']),indent=2),encoding='utf-8')
print(str(out))
