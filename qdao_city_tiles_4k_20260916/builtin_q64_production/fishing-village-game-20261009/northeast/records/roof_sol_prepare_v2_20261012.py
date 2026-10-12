from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime

Z = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
name = 'r05_c12_p11-p21-loweredge-v2'
target = Z / 'qa/r05_c12-roofbridge-v1/context.native-1to1.png'
guide = Z / f'guides/{name}.hole.png'
assert not guide.exists(), guide
im = Image.open(target).convert('RGB')
assert im.size == (1254, 1254)
box = [30, 660, 650, 820]
ImageDraw.Draw(im).rectangle((box[0], box[1], box[2]-1, box[3]-1), fill=(125,125,125))
im.save(guide)
prompt = '''Use case: precise-object-edit.
Asset type: seamless native game-map roof repair.
Edit attachment 4 only: fill its small flat gray rectangle x30..650,y660..820. Gray is a repair hole, not an object. Return the same entire 1254 by 1254 square frame, exact camera, scale and pixel registration. Attachment 5 is the unmasked native context of the same frame. Its horizontal join at y740 contains misplaced blue ceramic tile outlines, especially near x80..125 and x270..340; reconstruct those outlines as single smooth curves across that join. Match the fixed tile endpoints immediately above y660 and below y820: same spacing, cylindrical tile width, diagonal slope direction, overlapping edge rhythm, cobalt glaze, narrow dark gaps and daylight highlights. Remove the short blue-tile steps/wedges and synchronized row discontinuity; do not copy that erroneous seam from attachment 5. Precisely lock artwork outside the gray rectangle, including the gold upright and foot at left, curved fascia, dark wooden wall and corbels, large curled gold scroll at right, lower gold trim, and partial lantern. No change in framing, roof scale, row orientation, exposure or color. At all four hole boundaries, meet the surrounding original contours and painted facets without a shifted outline, sudden tone stripe, duplicated tile, extra line or blur.
Attachment 1 is the authoritative village layout reference only; attachment 2 is the close-up material reference only; attachment 3 is the approved rounded painterly Q Daoist style reference only, ignore its UI/text/characters. Keep the existing polished painterly daylight art. No new object, ornament, people, text, UI, labels, frame or watermark. This is a narrowly localized repair of the blue ceramic roof, with the surrounding architecture kept exactly in place.'''
refs = [
 'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/donghai-natural-stone-clear-routes-v10.png',
 'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/donghai-natural-stone-detail-v1.png',
 'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/user-references-20261009/mail-daoist-style.jpg',
 str(guide).replace('\\','/'), str(target).replace('\\','/')
]
args = dict(prompt=prompt, referenced_image_paths=refs, transparent_background=False)
def save(path, data):
 assert not path.exists(), path
 path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
promptpath = Z/f'records/{name}.prompt.txt'
assert not promptpath.exists()
promptpath.write_text(prompt, encoding='utf-8')
save(Z/f'records/{name}.actual-arguments.json',args)
save(Z/f'records/{name}.plan.json',dict(
 schemaVersion=1,agent='roof_sol',createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 purpose='Repair only blocking lower bridge seam blue-tile contour discontinuity',
 tool='image_gen.imagegen',route='builtin',nativeGlobalBox=[44941,16781,46195,18035],
 expectedNativeSize=[1254,1254],holeLocalBox=box,holeWorldBox=[44971,17441,45591,17601],
 guide=dict(path=str(guide),sha256=sha(guide),purpose='non-final edit input; flat gray hole only; no resize'),
 references=[dict(path=p,sha256=sha(p),role=r) for p,r in zip(refs,['authoritative map layout','close-up materials','primary Q Daoist style','edit target hole guide','native unmasked context, fixed endpoints'])],
 actualModel=None,actualQuality=None,modelSelectorSubmitted=False,qualitySelectorSubmitted=False,
 productionArtworkResizeAllowed=False,formalAccepted=False,
 authorization='Parent assignment relays renewed user request to continue, superseding prior temporary permission error; normal builtin call only'))
print(str(Z/f'records/{name}.actual-arguments.json'))
