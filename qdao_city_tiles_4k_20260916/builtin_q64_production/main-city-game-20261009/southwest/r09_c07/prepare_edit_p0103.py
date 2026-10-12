from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
q=R/'pipeline/prompts/p01_03.v02.request.json'
r=json.loads(q.read_text());src=R/'pipeline/attempts/p01_03.v02.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
prompt="""Use case: precise-object-edit. Image 1 is already native 1254x1254 game art. Make exactly one local seam repair. There is an artificial straight vertical cut at x263 running from y330 to the bottom. Remove this vertical cut and its tonal strip. Smoothly JOIN the interrupted broad grey and pale stone curved bands across x180..340: the curved edge arriving from the left near y630 must flow into the large grey curved band near y675, with consistent band width and rounded corner. The pale inner curved edge near y540 must likewise join its existing left shape naturally instead of ending as a vertical rectangular cut. The new connection must be shallow continuous stone carving at the same geometry and scale; no disconnected band and no rectangular border. Outside x150..370 keep every contour and material exactly unchanged. Keep all large pale blank stone faces calm and continuous. Do not add any new curve, small spiral, decorative tip, grout line, crack, circle, prop or object. Do not zoom, resize, reframe or render a complete scene. Keep the bottom-right broad band and left outer contour exactly unchanged except where needed to connect at the artificial join. Image 2 approved whole-city geometry only. Image 3 approved daylight stone and hand-painted material. Image 4 approved Daoist style only, no UI or objects. Image 5 clean stone texture only, no layout transfer. Opaque PNG exactly1254x1254, all existing pixels at same positions except the narrow seam repair."""
p=R/'pipeline/prompts/p01_03.v03.prompt.txt';p.write_text(prompt)
r['prompt']=prompt;r['promptFile']=str(p);r['promptSha256']=sha(p)
r['references'][0]={'file':str(src),'sha256':sha(src),'role':'edit target: actual native v02; repair only artificial vertical strip boundary'}
r['referenced_image_paths'][0]=str(src)
r['preparedAtUtc']=datetime.now(timezone.utc).isoformat();r['priorRequest']=str(q);r['priorRequestSha256']=sha(q)
r['nativeEditOperation']='targeted narrow join correction; no spatial resampling'
out=R/'pipeline/prompts/p01_03.v03.request.json';out.write_text(json.dumps(r,ensure_ascii=False,indent=2))
print(json.dumps(r))
