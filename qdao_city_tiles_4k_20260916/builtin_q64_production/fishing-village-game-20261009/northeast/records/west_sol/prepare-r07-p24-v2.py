import sys,json
from pathlib import Path
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
import west_sol as w
p='r07_c11_p24';v='v2';src=w.Z/'native/r07_c11_p24-v1-west_sol.png'
sel=w.own_selection('r07_c11')
w.write(w.R/'r07_c11.selection-before-p24-layout-correction.json',sel)
sel.pop(p,None);w.write(w.R/'r07_c11.selected.json',sel,True)
w.write(w.R/f'{p}-v1.layout-review.json',dict(native=w.ref(src),reviewedAtUtc=w.now(),status='withdrawn_pending_layout_correction',reason='Local edge-only quick review missed overextended stone floor. Authoritative overview interior is wood dock; successor guide exposes false vertical stone/wood rectangular boundary.',formalAccepted=False))
d=w.read(w.R/f'{p}-v1.plan.json')
refs=[w.ref(src,'PRIMARY EDIT TARGET: keep frame, correct floor material footprint')]+w.mandatory()+[d['guide']]
prompt="""Edit IMAGE 1 in its exact original 1254x1254 frame. Correct the floor material footprint to the authoritative image5 position guide: the blurred warm brown interior in image5 is WOOD DOCK, not stone. The stone paving from the top should terminate with a natural angled timber/stone threshold in the upper third, turning into the dock; the majority of the lower two thirds must be the same warm diagonal wooden plank deck already on the right. Keep the existing partial crate at upper-left, the topmost stone slab contours and the right edge plank spacing at their exact coordinates. Extend the right-edge planks smoothly leftward across the lower interior with native crisp timber texture; make the upper stone-to-wood boundary physically coherent and naturally angled, never a straight horizontal screen cut or rectangular pasted panel. Preserve image1 outermost top115 and right115 anchor pixels, matching the same exposure and plank direction. No new objects or structures. Image2 is whole-map layout only; image3 supplies daylight material quality, image4 Daoist Q style; image5 is the exact layout frame with native top/right anchors. Follow the brown dock footprint, not invented all-stone pavement. No UI, text, people or borders. Output opaque native1254 square, no resizing. Coordinate r07_c11_p24 world [43917,25485,45171,26739], core [115,115,1139,1139]."""
d.update(version=v,preparedAtUtc=w.now(),references=refs,guide=w.ref(src),guidePurpose='Native edit to correct overextended paving into wood dock footprint',previousCandidate=w.ref(src),formalAccepted=False)
w.write(w.R/f'{p}-{v}.plan.json',d);(w.R/f'{p}-{v}.prompt.txt').write_text(prompt,encoding='utf-8')
w.write(w.R/f'{p}-{v}.actual-arguments.json',dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
p='r07_c11_p34';src=w.Z/f'native/{p}-v1-west_sol.png'
w.write(w.R/f'{p}-v1.review.json',dict(native=w.ref(src),reviewedAtUtc=w.now(),status='not_selected',reason='Internal false rectangular stone/wood edge x1024 from inherited floor material footprint; must use corrected p24 south anchor before retry.',formalAccepted=False))
print('p24 withdrawn; v2 prepared; p34-v1 retained not selected')

