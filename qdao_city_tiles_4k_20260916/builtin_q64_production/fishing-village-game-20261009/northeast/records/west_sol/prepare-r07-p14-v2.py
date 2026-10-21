from pathlib import Path
import json,sys
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
import west_sol as w
p='r07_c11_p14';v='v2'
d=w.read(w.R/f'{p}-v1.plan.json')
src=w.Z/'native/r07_c11_p14-v1-west_sol.png'
refs=[w.ref(src,'PRIMARY EDIT TARGET: existing native image, repair internal fish seams only')]+w.mandatory()
prompt="""Edit IMAGE 1 only, preserving its exact 1254x1254 frame and all existing scene geometry. Repair the visible rectangular discontinuities in the fish display: a horizontal cut at y230 interrupts the large blue fish, red fish and ice; another cut at x1024 interrupts the red tail at y200..340. Make each existing fish body, scale pattern, fin, ice crystal and wooden rim continue smoothly through these internal cut lines with physically continuous original contours. The blue hanging textile currently starts abruptly at y230; connect its folded top naturally over the wooden rim without moving that rim or fish. Do not move the outer image edge pixels or reinterpret composition. Preserve the timber post, gold cap, hanging textiles, barrel, crates, stone floor and wood deck exactly; edit only the defect zone y160..360. Images 2, 3 and 4 are respectively placement, material and painterly Daoist Q style references; never import their scene content. No new object, text, people, UI, extra fish or border. Output one opaque native 1254x1254 image, no resize. Coordinate r07_c11_p14; world box [43917,24461,45171,25715]; core [115,115,1139,1139]."""
d.update(version=v,preparedAtUtc=w.now(),references=refs,guide=w.ref(src),guidePurpose='Native edit target, localized repair of y230/x1024 internal discontinuity; prior guide not submitted',previousCandidate=w.ref(src),formalAccepted=False)
w.write(w.R/f'{p}-{v}.plan.json',d)
(w.R/f'{p}-{v}.prompt.txt').write_text(prompt,encoding='utf-8')
w.write(w.R/f'{p}-{v}.actual-arguments.json',dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
w.write(w.R/f'{p}-v1.review.json',dict(patch=p,native=w.ref(src),reviewedAtUtc=w.now(),status='not_selected_pending_repair',issues=['Internal y230 fish/ice/textile cut','Internal x1024 red tail discontinuity'],formalAccepted=False))
print(json.dumps(dict(arguments=str(w.R/f'{p}-{v}.actual-arguments.json'))))
