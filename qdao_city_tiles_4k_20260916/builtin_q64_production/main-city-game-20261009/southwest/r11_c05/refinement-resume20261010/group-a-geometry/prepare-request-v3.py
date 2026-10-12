from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
D=Path(__file__).resolve().parent;r=json.loads((D/'request-v1.json').read_text(encoding='utf-8'))
prompt="""Edit image 1 surgically. Output the exact same 1254x1254 image. Images 2-4 are style references only.
Perform ONLY ONE action: extend the single incomplete diagonal groove in the lower half BACKWARD toward the upper-left until it touches the existing upper long diagonal groove.
The incomplete groove's upper-left endpoint is at image pixel (533,810). From that point it already runs downward-right to the junction near (838,1097). That entire EXISTING part stays pixel-aligned, unchanged. Add only the MISSING continuation from (533,810) upward-left through (500,781),(450,735),(400,688),(350,641),(300,594), to a T-junction near (255,553) on the already existing long diagonal. Match the existing width, bevel and shadow. Do not extend through the upper diagonal.
DO NOT move, repaint or straighten the existing lower diagonal, its lower junction, or the upper long diagonal. The existing groove centers at (540,818),(560,836),(600,873),(650,920),(700,967),(750,1014),(800,1061),(835,1094) MUST STAY EXACT. Do not make the lower groove fit an idealized grid. Add missing pixels to its existing line.
Leave the small upper groove notch near (533,365) and the bottom short spur near (716,1173) EXACTLY as they are; these are NOT targets of this edit. No changes anywhere except the narrow new missing groove segment and its tiny upper T junction. Original stone surface, colors, texture and all image edges remain unchanged. No new shapes, cracks, grid lines, objects or decor."""
p=D/'prompts/group-a-G01-v3.prompt.txt';p.write_text(prompt,encoding='utf-8');r.update(id='group-a-G01-v3',createdAtUtc=datetime.now(timezone.utc).isoformat(),prompt=prompt,promptFile=str(p),promptSha256=hashlib.sha256(p.read_bytes()).hexdigest())
(D/'request-v3.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')

