from pathlib import Path
from PIL import Image
import json,hashlib
O=Path(__file__).resolve().parent;V=O/'v03';V.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((O/'v01/preparation.json').read_text())
im=Image.open(O/'v02/derived-context.png').convert('RGB');im.save(V/'context-native.png')
holes=[[345,608,440,697],[485,545,825,685]]
mask=im.convert('RGBA')
for b in holes:mask.paste((0,0,0,0),tuple(b))
mask.save(V/'edit-guide-transparent.png')
prompt='''Use case: precise-object-edit. Fill ONLY the two tiny transparent holes in Image 1, an existing 1254 x 1254 glazed turquoise game-roof texture. Image 2 is the complete original for exact anchoring. Return one opaque 1254 x 1254 completed image. Preserve all the supplied surrounding image exactly.

Hole A x345..440,y608..697: the right tip of a curved overlapping tile lip has 3-4 tiny pointed sawteeth and an unnatural black V tear. Replace those sawteeth with one smooth rounded ceramic lip, curving down and tapering naturally into the existing narrow vertical dark gutter. Keep the tile body above and below fixed. No extra rim or additional tile.

Hole B x485..825,y545..685: two adjacent roof lips expose large triangular tears showing misplaced vertical blue gutters. Replace the triangular torn flaps with smooth short rounded OVERLAP COLLARS that connect the exact upper and lower existing tile boundaries. Preserve the intentional stagger of the lower row; do NOT move the lower row or change its tile count. Curved lips can gently skew sideways to meet the staggered lower tiles. Do not straighten the whole roof into different columns.

Each repaired lip must be a continuous dark navy curved edge with a thin turquoise highlight and the same painterly glaze as the intact neighbors. All visible edge endpoints where the hole meets original pixels are fixed anchors. No triangular flaps, tooth-like edge, duplicated curves, square patches, new tile rows, changed scale, text, annotations or margins. The two holes are the ONLY edit areas, not a request to redesign the roof.'''
params={'prompt':prompt,'referenced_image_paths':[str(V/'edit-guide-transparent.png'),str(V/'context-native.png')],'transparent_background':False}
(V/'parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2),encoding='utf-8');(V/'prompt.txt').write_text(prompt,encoding='utf-8')
p.update(repairContextBox=[130,515,825,725],repairSubBoxes=holes,baseContextPriorDerivation=str(O/'v02/derivation-pending.json'),referenceSources=[{'file':f,'sha256':sha(Path(f))} for f in params['referenced_image_paths']])
(V/'preparation.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'v02/visual-review.json').write_text(json.dumps({'verdict':'FAIL_PENDING_LOCAL_REFINEMENT','actuallyViewed':True,'finding':'Lower anchor retained; one sawtoothed ceramic lip remains at context [373,633,424,675]. Derived context may be used only as a refinement input, not a passed delivery.','independentQA':'seam_diagnosis confirmed same defect'},indent=2),encoding='utf-8')
print(V)
