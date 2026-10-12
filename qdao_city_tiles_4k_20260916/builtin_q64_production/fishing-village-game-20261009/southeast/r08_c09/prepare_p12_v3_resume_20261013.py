from pathlib import Path
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/r08_c09')
p='''Use case: precise-object-edit. Image1 is the exact native1254square target. KEEP EVERY FISH-LANTERN AND RED-CORD PIXEL visually unchanged: same eye, face, scales, gold ribs, body silhouette and frame clipping. Change ONLY blurred gray paving background around the fish, particularly upper corners and right side, to equally SHARP native cool gray-blue stone slabs matching the already-sharp bottom115 strip and image2. All parts of this game-map patch must be equally sharp, NO depth of field or bokeh. Do not blur, move, resize, zoom, reframe or redraw the fish. Remove the horizontal blur-to-sharp transition at y1139 by painting the paving above it with matching slab endpoints, scale and painterly material. Keep the actual lower115 row geometries unchanged, continue them upward naturally. Exact1254x1254 pixels RGB, same target footprint, no added object, letter, border or watermark.'''
refs=[str(T/'raw/p12-v2-builtin.png'),str(T/'native/p22-v2.png')]
d=dict(prompt=p,referenced_image_paths=refs,transparent_background=False,route='builtin',tool='image_gen__imagegen',submittedModel=None,submittedQuality=None,actualModel=None,actualQuality=None,referenceRoles={'1':'Actual native target, fish unchanged; paving sharpness edit only','2':'Actual lower neighbor stone material only'},referenceEvidence=[dict(path=s,sha256=hashlib.sha256(Path(s).read_bytes()).hexdigest()) for s in refs])
assert not (T/'p12-v3.request.json').exists()
(T/'p12-v3.request.json').write_text(json.dumps(d,indent=2),encoding='utf-8');(T/'p12-v3.prompt.txt').write_text(p,encoding='utf-8')

