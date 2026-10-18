from pathlib import Path
import json
T=Path(__file__).resolve().parent;p=T/'local-content.json';d=json.loads(p.read_text())
d['p01_02']+=' Native anchor geometry wins over coarse blocky guide: the actual upper tower-face corner lies at x~326 in TOP, so continue this SAME corner vertically down and naturally wrap the approved horizontal lower string courses onto the return face. Do not introduce a second false vertical pillar/corner at x550. Continue the diagonal stone joints on the narrow LEFT-facing return wall exactly from the LEFT native; do not cut them off at x230 or y115.'
d['p02_01']+=' CRITICAL: long grout lines on the main face must keep the upward-right diagonal orientation of TOP native, continuing down-left seamlessly. No horizontal grout row at y230 and no reset to horizontally aligned bricks. The existing lower coping near y1050 is the first permitted structural angle change. Existing right face grid slopes oppositely from main face, follow native corner geometry.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
