from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime
Z = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
name='r05_c12_p11-p21-loweredge-v3'
target=Z/'qa/r05_c12-roofbridge-v1/context.native-1to1.png'
guide=Z/f'guides/{name}.hole.png'
assert not guide.exists()
boxes=[[55,700,155,800],[245,700,370,800]]
im=Image.open(target).convert('RGB');assert im.size==(1254,1254)
draw=ImageDraw.Draw(im)
for x0,y0,x1,y1 in boxes: draw.rectangle((x0,y0,x1-1,y1-1),fill=(125,125,125))
im.save(guide)
prompt='''Use case: precise-object-edit.
Precisely repair ONLY the two small gray squares in attachment 4, x55..155,y700..800 and x245..370,y700..800, on the lower-left blue roof. Gray means missing repair pixels. Return the exact same entire 1254 by 1254 image, exact frame and pixel registration. Attachment 5 is the unmasked current image, showing a 10-20 pixel tile-contour displacement at horizontal y740 inside those two small windows. Each window contains ONE existing blue ceramic tile overlap curve. Connect its fixed endpoint above y700 to its fixed endpoint below y800, as a smooth continuous single overlap arc in the same exact tile geometry. Match the dark gap edge, narrow highlight rim and painted cobalt blue facet to the untouched endpoints at all four sides. Keep exactly the original neighboring tile widths, diagonal slope, cylindrical rounding and row spacing; do not invent new tile arcs or reset the roof tile pattern. The upper and lower tile segments of attachment 5 are the geometric anchors; eliminate the small step where they meet inside the gray windows. Keep every visible blue tile and architectural detail OUTSIDE these two windows exactly in its current position. Do not reconstruct or rescale any entire row, do not straighten the diagonal arcs, do not shift the neighboring tile caps. Leave the gold beam, posts, curled ornament, wood wall, lower fascia, lantern and all lighting unchanged. No blue tone rectangle, blurred patches or conspicuous outlines at window boundaries.
Attachment 1 is the authoritative village layout reference only. Attachment 2 is the material style reference only. Attachment 3 is the approved rounded painterly Q Daoist art style reference only, ignore its UI, text and characters. Maintain the existing polished painterly daylight game illustration. No new object, ornament, people, text, UI, grid, frame or watermark. Make only these two tiny seam corrections.'''
refs=[
'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/donghai-natural-stone-clear-routes-v10.png',
'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/donghai-natural-stone-detail-v1.png',
'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/user-references-20261009/mail-daoist-style.jpg',
str(guide).replace('\\','/'),str(target).replace('\\','/')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
pp=Z/f'records/{name}.prompt.txt';assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
save(Z/f'records/{name}.actual-arguments.json',dict(prompt=prompt,referenced_image_paths=refs,transparent_background=False))
save(Z/f'records/{name}.plan.json',dict(schemaVersion=1,agent='roof_sol',createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 nativeGlobalBox=[44941,16781,46195,18035],expectedNativeSize=[1254,1254],holeLocalBoxes=boxes,
 purpose='Second attempt: two narrowly isolated existing overlap arcs; preserve tile pitch',
 guidePurpose='non-final hole input; no resize',
 references=[dict(path=p,sha256=sha(p),role=r) for p,r in zip(refs,['authoritative map layout','close-up materials','primary Q Daoist style','two-hole edit target guide','unmasked native context, fixed tile endpoints'])],
 actualModel=None,actualQuality=None,modelSelectorSubmitted=False,qualitySelectorSubmitted=False,formalAccepted=False))
save(Z/'qa/r05_c12-loweredge-v2/roof_sol-self-review.json',dict(schemaVersion=1,reviewer='roof_sol',createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 verdict='rejected_new_contribution_boundaries_change_tile_pitch',formalAccepted=False,
 nativeOutput=dict(path=str(Z/'native/r05_c12_p11-p21-loweredge-v2.png'),sha256=sha(Z/'native/r05_c12_p11-p21-loweredge-v2.png'),nativeSize=[1254,1254]),
 viewedNative=['context','top','bottom','left','right','interior-blue-tiles'],
 finding='Original y740 join becomes continuous, but wide replacement changes tile pitch: bottom y820 and both vertical boundaries cross mismatched tile arcs. Do not adopt the derived v2 patches.',
 nextAttempt='Use only two small windows around the reported contour displacements. All existing originals and rejected outputs preserved.'))
print(str(Z/f'records/{name}.actual-arguments.json'))
