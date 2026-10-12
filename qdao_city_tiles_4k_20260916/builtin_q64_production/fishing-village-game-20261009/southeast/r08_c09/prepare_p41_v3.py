from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=T/'native/p41-v2.png';s=T.parent/'r09_c09/processed/colorpass-20261012-v1/p11-colorpass.png'
a=Image.open(base).convert('RGBA');n=Image.open(s).convert('RGBA')
# Verified sharp neighbor top1254 band; use it as an INPUT, never as selected art.
a.paste(n.crop((0,0,1254,230)),(0,1024))
for y in range(0,1024,115):a.paste(n.crop((568,115,704,115+min(115,1024-y))),(568,y))
alpha=a.getchannel('A')
holes=[(530,0,568,1024),(150,0,557,245),(704,0,902,240),(0,950,568,1024),(704,950,1254,1024)]
for box in holes:alpha.paste(0,box)
a.putalpha(alpha);out=T/'layout-only/p41-v3-fixed-post-and-bottom-guide.png';a.save(out)
old=json.loads((T/'p41-v1.request.json').read_text(encoding='utf-8-sig'))
prompt='''Use case: precise-object-edit. Edit image1 into exactly1254x1254 native RGB game world art. This target is an almost-finished lantern/post patch. Keep every opaque existing object and all opaque contours unchanged. Fill ONLY the transparent guide holes. The upper holes replace unwanted masonry with the same flat blue-gray stone paving visible below, preserving actual grout direction. No wall or extra vegetation exists here. The very narrow vertical hole to the left of the straight dark wood shaft must be flat stone background right up to its left silhouette x568. Preserve the shaft at x568..704, fixed throughout its height; its repeated grain guide should become coherent natural painterly grain without changing its silhouette.
The bottom230px are exact, sharp selected neighboring native artwork at fixed coordinates. Keep the bottom native strip, post, red/gold lantern base ornaments and pavement contours unchanged. Fill the horizontal holes immediately above that strip by connecting the existing lantern red shell and cream paper down into those existing rounded red bases and gold endcaps. These are partial lantern forms, not new objects. Keep upper body outlines and attachments unchanged, with a natural smooth transition; no rectangular cutoff or doubled edges. Keep opaque gold/body contour positions. Do not move, zoom, widen, crop or rescale anything. The eventual exact core cuts are115 and1139px.
Image2 fullmap is LAYOUT ONLY. Image3 independent clear-daylight materials is STYLE ONLY. Image4 approved Daoist Q rounded painterly art is STYLE ONLY, no night lighting, no UI/text/characters. Same bright daylight, native crisp broad painterly strokes and existing texture density. No new crossbar, walls, props, glyphs, text, people or background objects. Return one exact1254-square at original footprint. Do not repeat the neighbor; preserve fixed endpoint contours. No blur, border, watermark or guide seams.'''
req={**old,'prompt':prompt,'referenced_image_paths':[str(out)]+old['referenced_image_paths'][1:]}
req['referenceRoles']['1']='Native edit target with alpha holes, exact straight shaft guide, verified sharp full lower native overlap230'
req['referenceEvidence']=[dict(path=p,sha256=sha(p),role=req['referenceRoles'][str(i)]) for i,p in enumerate(req['referenced_image_paths'],1)]
(T/'p41-v3.prompt.txt').write_bytes(prompt.encode('utf-8'));(T/'p41-v3.request.json').write_text(json.dumps(req,indent=2),encoding='utf-8')
Path(str(out)+'.derivation.json').write_text(json.dumps(dict(file=str(out),sha256=sha(out),classification='guide only, never selected art',derivedFrom=[dict(file=str(base),sha256=sha(base)),dict(file=str(s),sha256=sha(s))],operation='unscaled genuine native lower230 paste, straight-shaft guide and alpha holes',holes=holes),indent=2),encoding='utf-8')
(T/'native/p41-v2.rejection.json').write_text(json.dumps(dict(status='rejected_not_selected',reason='Unrequested upper masonry, shaft left edge11px from exact lower neighbor and bottom lantern attachment mismatch; superseded fixed-border native refresh.',selected=False),indent=2),encoding='utf-8')
print(str(out))
