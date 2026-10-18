import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
import west_sol as w
p='r07_c11_p12';v='v3';base=w.Z/f'native/{p}-v2-west_sol.png';old=w.Z/f'native/{p}-v1-west_sol.png';d=w.read(w.R/f'{p}-v2.plan.json')
im=Image.open(base).convert('RGB');im.paste(Image.open(old).convert('RGB').crop((0,0,1254,230)),(0,0))
gp=w.Z/f'guides/{p}-{v}-west_sol.native-top-repair.png';assert not gp.exists();im.save(gp)
w.write(Path(str(gp)+'.derived.json'),dict(base=w.ref(base),topAnchor=w.ref(old),operation='Exact native integer top230 crop/paste only; guide not final pixels'))
refs=[w.ref(gp,'PRIMARY EDIT TARGET: native pendant with restored correct top paving')]+w.mandatory()
prompt="""Edit IMAGE1 only in exact1254 square frame. Keep the restored top y0..230 stone pavement completely unchanged: no object, cord or ornament may enter that band. Repair only the upper attachment of the narrow LEFT red pendant around x0..330,y230..380. Its currently truncated red knot should become a clean complete small rounded knot entirely BELOW y240, attached by a short curved RED HORIZONTAL CORD that exits the LEFT edge around y280 toward the off-frame existing lamp support. NO VERTICAL CORD UPWARD. Do not extend any red cord toward the top edge. The long pendant body with three gold medallions, cropped bottom tassel, large right lantern and all surrounding paving must stay at their present exact scale and location. Maintain a smooth continuous pendant top with no straight cut. Do not alter top230 or right230 native anchors. No extra objects, letters, people, UI, zoom or blur. Images2,3,4 are layout, material and Daoist Q style references only. Output opaque native1254x1254, coordinate r07_c11_p12 world[41869,24461,43123,25715], core[115,115,1139,1139]."""
d.update(version=v,preparedAtUtc=w.now(),references=refs,guide=w.ref(gp),guidePurpose='Native top anchor guide for local pendant attachment correction',previousCandidate=w.ref(base),formalAccepted=False)
w.write(w.R/f'{p}-{v}.plan.json',d);(w.R/f'{p}-{v}.prompt.txt').write_text(prompt,encoding='utf-8')
w.write(w.R/f'{p}-{v}.actual-arguments.json',dict(prompt=prompt,referenced_image_paths=[e['path'] for e in refs],transparent_background=False))
w.write(w.R/f'{p}-v2.review.json',dict(native=w.ref(base),status='not_selected_pending_attachment_repair',reviewedAtUtc=w.now(),issue='Restored pendant but model added vertical red cord through top115 where north source is stone, causing north seam discontinuity.',formalAccepted=False))

