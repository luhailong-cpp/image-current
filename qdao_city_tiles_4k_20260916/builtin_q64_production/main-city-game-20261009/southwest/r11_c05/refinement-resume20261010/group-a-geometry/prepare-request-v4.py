from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
D=Path(__file__).resolve().parent;r=json.loads((D/'request-v1.json').read_text(encoding='utf-8'))
prompt="""Precise local image cleanup. Edit ONLY the first image; the other three images are style references.
In the LOWER HALF of image 1, remove TWO unsupported dead-end grout branches on the LEFT SIDE of the lower junction. Remove the entire northwest spur from its free endpoint around (533,810) down to the junction around (838,1097). Also remove the short southwest spur from (716,1173) up to the same junction. Replace ONLY these two unwanted groove strips, including their bright bevels and shadows, with seamless matching existing pale gray stone texture. The surrounding stone should be one uninterrupted slab with NO marks where those two left branches were.
KEEP the existing northeast branch from (838,1097) to the right edge and the existing southeast branch from (838,1097) to the bottom edge exactly in their original pixel locations. They remain as a clean V-shaped stone corner whose vertex is the ORIGINAL existing junction. Do not move, rotate, straighten or redraw either right-hand branch. This is subtraction of the two left-hand spurs only, not reconstruction of a paving grid.
Keep the rest of the image absolutely identical: the upper long diagonal, its small offset notch near (533,365), every vertical line, every other corner, the existing stone color/texture and the entire external border. Do not extend any joint, add any seam or new geometry. Do not polish or repaint whole slabs. The only edit region is the thin strips occupied by those two unwanted left spurs and the minimal few pixels cleaning their connection to the original lower corner.
Output exactly the original native 1254 by 1254 framing and scale."""
p=D/'prompts/group-a-remove-v4.prompt.txt';p.write_text(prompt,encoding='utf-8');r.update(id='group-a-remove-v4',createdAtUtc=datetime.now(timezone.utc).isoformat(),prompt=prompt,promptFile=str(p),promptSha256=hashlib.sha256(p.read_bytes()).hexdigest())
(D/'request-v4.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')

