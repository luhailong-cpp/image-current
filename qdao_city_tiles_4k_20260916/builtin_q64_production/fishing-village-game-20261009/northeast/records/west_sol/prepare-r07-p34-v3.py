import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
import west_sol as w
p='r07_c11_p34';v='v3';base=w.Z/f'native/{p}-v2-west_sol.png';d=w.read(w.R/f'{p}-v2.plan.json')
right=next(e for e in d['nativeEdgeSources'] if e['side']=='right')
im=Image.open(base).convert('RGB');q=Image.open(right['path']).convert('RGB');im.paste(q.crop((0,0,230,1254)),(1024,0))
gp=w.Z/f'guides/{p}-{v}-west_sol.native-bollard-repair.png';assert not gp.exists();im.save(gp)
w.write(Path(str(gp)+'.derived.json'),dict(base=w.ref(base),rightAnchor=right,operation='Exact native integer right230 crop/paste only, guide not final pixels'))
refs=[w.ref(gp,'PRIMARY EDIT TARGET: native current image with exact neighbor anchor')]+w.mandatory()
prompt="""Edit IMAGE1 only, in the exact1254 square frame. The floor and timber rail are already correct and must stay unchanged. Repair ONLY the lower-right BLUE MOORING BOLLARD and its cream rope across the visible small vertical discontinuity at x1024,y1000..1254. Its RIGHT part x1024..1254 is the authoritative original native neighboring anchor: preserve that part at its exact position and scale, including the cap height, blue stave spacing, cylindrical contour and rope. Adjust only the LEFT continuation of this same single bollard around x890..1024,y1000..1254 to join that right part smoothly. Do not raise the cap, change its diameter, add another post, repaint the outer right115 pixels, shift rope or alter the wood deck. Match the exact contours through x1024 and x1139 without a visible cut. Images2,3,4 are whole-layout, daylight material and Q Daoist style references only; ignore all their scene content. No text, people, UI or borders. Output opaque native1254x1254; coordinate r07_c11_p34, world [43917,26509,45171,27763], core[115,115,1139,1139]."""
d.update(version=v,preparedAtUtc=w.now(),references=refs,guide=w.ref(gp),guidePurpose='Native integer anchor guide for local bollard continuation repair',previousCandidate=w.ref(base),formalAccepted=False)
w.write(w.R/f'{p}-{v}.plan.json',d);(w.R/f'{p}-{v}.prompt.txt').write_text(prompt,encoding='utf-8')
w.write(w.R/f'{p}-{v}.actual-arguments.json',dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
w.write(w.R/f'{p}-v2.review.json',dict(native=w.ref(base),status='not_selected_pending_local_bollard_repair',reviewedAtUtc=w.now(),issue='Dock footprint corrected; blue bollard cap shifted upward roughly30pixels at right core seam. Do not propagate geometry.',formalAccepted=False))

