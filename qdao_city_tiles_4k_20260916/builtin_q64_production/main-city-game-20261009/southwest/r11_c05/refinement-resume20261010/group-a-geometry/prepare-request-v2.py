from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
D=Path(__file__).resolve().parent
r=json.loads((D/'request-v1.json').read_text(encoding='utf-8'))
prompt="""Use case: precise-object-edit. Edit image 1 with exact GEOMETRY ANCHORS. This is a 1254x1254 pixel native crop; DO NOT recompute or regularize the paving grid. Images 2-4 are style-only references.
Preserve ALL existing groove centerlines and framing. The previous attempt incorrectly shifted the entire lower diagonal about 29 pixels UP and moved the bottom junction; that is absolutely forbidden. Do not move any original joint to fit the new segment. Add missing pixels to the existing joint positions.
THREE strictly local corrections in image-1 pixel coordinates:
1. Tiny upper groove offset near (533,365). Keep the original vertical junction near (422,435), keep original groove anchor (480,396), and keep right-hand original anchors (555,361),(575,347),(595,334). Remove only the duplicated abrupt step and connect those existing left/right pieces cleanly and continuously over the small local interval x495..560. It may make a very gentle local transition; do not shift the long line on either side or its vertical junction.
2. The false endpoint near (533,810) needs ONLY the missing northwest continuation. The EXISTING down-right joint must remain exactly through these measured centerline anchors: (540,818),(560,836),(600,873),(650,920),(700,967),(750,1014),(800,1061),(835,1094),(880,1136),(920,1173),(950,1200). Do not change even the position of that existing portion. Add the missing straight line backward approximately through (500,781),(450,735),(400,688),(350,641),(300,594), finally meeting the EXISTING upper-left diagonal near (255,553) as a T joint. The only new groove is this missing northwest segment. Keep the original upper diagonal position at the intersection unchanged. No shifted parallel groove, no extra bevel and no doubled line.
3. Remove only the short southwest spur from about (716,1173) to the EXISTING junction centered near (840,1098). Fill the spur with seamlessly matching original stone texture. Keep the original NW-SE long diagonal through all the measured anchors above, and the original NE branch from this junction toward the right edge, in the EXACT original positions. The corrected existing junction becomes a T junction in the same location. Do not enlarge, move or round a different corner.
The original external image border and everything outside the three repair neighborhoods are locked. Keep gray palette, original texture, lighting, all vertical joints and all other existing slab corners. No broad material painting, no global line shifts, no new objects or decorative cracks. Exact original 1254-square output. The crop will be used in tiny local patches, so any movement of existing geometry makes the result unusable."""
p=D/'prompts/group-a-v2.prompt.txt';p.write_text(prompt,encoding='utf-8')
r.update(id='group-a-v2',createdAtUtc=datetime.now(timezone.utc).isoformat(),prompt=prompt,promptFile=str(p),promptSha256=hashlib.sha256(p.read_bytes()).hexdigest())
(D/'request-v2.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'id':r['id'],'promptSha256':r['promptSha256']}))

