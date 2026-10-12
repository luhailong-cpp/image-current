from pathlib import Path
import json, hashlib
from PIL import Image
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
contract=json.loads((ROOT.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
src=ROOT/'r11_c05/refinement-resume20261010/full-tile-review/output/r11_c05.repaired.candidate.context.png'
box=(1650,1750,2904,3004)
target=OUT/'c-horizontal-joint.target.png'
with Image.open(src) as im: im.crop(box).save(target)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
refs=[{'file':str(target),'sha256':sha(target),'role':'edit target: exact native crop, no resampling'}]
for key in ['layoutReference','detailStyleReference','primaryStyleReference']:
 p=contract[key];refs.append({'file':p,'sha256':sha(p),'role':key})
prompt="""Use case: precise-object-edit. Output one opaque native 1254x1254 PNG at exactly the framing of Image1. This is a tiny ground paving fragment, not a scene. Image2 is only approved city geometry reference, Image3 stone daylight material reference, Image4 approved Daoist painting style reference, do not copy their content.
Only fix the malformed hanging end of the horizontal paving grout near target pixel (583,530), corresponding to world tile core (2118,2165). Keep ALL other paving edges, surface colors and texture in exactly their original positions. This horizontal line must connect to the neighboring existing vertical grout at its same height, without a gap, stub or overlap. Extend only its missing short connection, at original thickness and bevel. Do not move vertical lines, do not add new grout networks, staircases, props or patterns. Preserve the original cropped image and every outer border pixel. No material restyling, no new texture, no artificial straight boundary. Only the existing local line defect is corrected; return the complete same-sized native crop."""
(OUT/'c-horizontal-joint.prompt.txt').write_text(prompt,encoding='utf-8')
req={'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'references':refs,'transparent_background':False,'source':str(src),'sourceSha256':sha(src),'sourceContextBox':box,'sourceResampling':False,'actualModel':None,'actualQuality':None,'preparedAtUtc':datetime.now(timezone.utc).isoformat()}
(OUT/'c-horizontal-joint.request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'request':str(OUT/'c-horizontal-joint.request.json'),'seed':str(target)}))

