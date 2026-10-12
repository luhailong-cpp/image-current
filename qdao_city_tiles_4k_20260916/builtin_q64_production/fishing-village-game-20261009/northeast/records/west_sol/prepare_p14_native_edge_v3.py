from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
Z=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast');R=Z/'records/west_sol'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role):return dict(path=str(p).replace('\\','/'),sha256=sha(p),role=role)
def write(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p='r06_c11_p14';v='v3';old=read(R/f'{p}-v2.plan.json')
base=Z/f'native/{p}-v2-west_sol.png';im=Image.open(base).convert('RGB')
for e in old['nativeEdgeSources']:
 q=Image.open(e['path']).convert('RGB');im.paste(q.crop(e['sourceCropBox']),tuple(e['targetPasteAt']))
target=Z/f'guides/{p}-{v}-west_sol-native-target.png';assert not target.exists();im.save(target)
hole=Z/f'guides/{p}-{v}-west_sol-native-hole.png';assert not hole.exists()
box=[850,230,1120,1254];ImageDraw.Draw(im).rectangle((850,230,1119,1253),fill=(125,125,125));im.save(hole)
refs=old['references'][:3]+[ref(hole,'native edit target with one narrow right-side gray transition hole'),ref(target,'unmasked fully native context; existing original top/right neighbor bands fixed')]
prompt='''Use case: precise-object-edit. Fill ONLY the gray right-side rectangle x850..1120,y230..1254 in attachment4. Return the same entire1254 by1254 native image in exact pixel registration. Attachment5 is the unmasked native context, with original adjoining native artwork copied exactly into TOP y0..230 and RIGHT x1024..1254. The gray rectangle marks only a transition needing reconstruction: continue the single existing giant amber counterfront and its dark undercounter framing from the LEFT, meeting the fixed timber pillar and basket on the RIGHT. Match the slate grey stone slab edges, beveled corners and painted facet colors from the LEFT to their fixed endpoints at RIGHT x1120. Make the stone routes continuous below the counter. The original right band controls exact timber column base, basket placement, stone-joint geometry and daylight tones; do not move, duplicate, cut or hide them. Keep TOP y0..230, RIGHT x1120..1254 and LEFT x0..850 exactly as shown. Do not add or scale any object. At y230 meet the fixed upper frame; at x850 and x1120 keep single continuous timber and stone contours without wedge, abrupt tone stripe, doubled joint or shifted line. This remains a giant cropped counterfront occupying the upper half and grey stone walkway below. No tabletop, folded goods, miniature stalls, additional tables, new post, canopy or fish is visible in this frame. Preserve the huge original counter scale and exact camera; no zoom or redesign.
Attachment1 is authoritative village layout only; attachment2 is daylight materials only; attachment3 is the approved rounded painterly Q Daoist style only, ignore its UI/text/people/night. Warm daylight, polished fine hand-painted facets, naturally grey stone and amber timber. No new objects, people, text, UI, grid, frame, watermarks or blur. Only repair this native transition to the actual right neighbor.'''
pp=R/f'{p}-{v}.prompt.txt';assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
write(R/f'{p}-{v}.actual-arguments.json',dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
plan=dict(old);plan.update(version=v,preparedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),references=refs,guide=ref(hole,'non-final native hole guide'),guidePurpose='Fully native context from v2 and exact adjoining anchors, gray edit hole; no resize',baseNative=ref(base,'previous raw native'),editHoleLocalBox=box,unmaskedNativeTarget=ref(target,'fully native contextual edit input'),formalAccepted=False)
write(R/f'{p}-{v}.plan.json',plan)
write(Path(str(target)+'.derived.json'),dict(**ref(target,'non-final native edit target'),base=ref(base,'previous generated native'),nativeEdgeSources=old['nativeEdgeSources'],operation='Exact opaque crop/paste of native TOP230 and RIGHT230 into native base; no resize or feather; guide only'))
write(R/f'{p}-v2.rejection.json',dict(patch=p,verdict='not_selected_right_stone_joint_geometry_needs_transition',formalAccepted=False,top='Giant counterfront scale now preserved, north geometry substantially continuous',right='Native stone joints and basket height differ from adjoining source across right core seam; reconstruct native transition before propagation',nextAttempt='native context edit with fixed top/right anchors and narrow right transition hole'))
