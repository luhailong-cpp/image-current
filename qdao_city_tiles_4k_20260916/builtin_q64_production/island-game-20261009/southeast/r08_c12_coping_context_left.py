from pathlib import Path
from PIL import Image,ImageFilter
import json,hashlib,os
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
R=Path(__file__).resolve().parent;p=R/'guides/r08_c12_repair_coping_long_left_v01.native-context.png'
im=Image.open(p).convert('RGB');blur=im.filter(ImageFilter.GaussianBlur(24))
# Context-only mechanical defocus removes the old erroneous ledge from conditioning; never used in final art.
im.paste(blur.crop((240,350,1254,1030)),(240,350))
# Restore the actual upper/back-edge endpoint and foliage at the right. Lower incorrect shelf stays defocused.
original=Image.open(R/'tiles/r08_c12.candidate-v13.png').crop((1421,2445,2675,3699))
im.paste(original.crop((1140,0,1254,640)),(1140,0));im.save(p)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=R/'prompts/r08_c12_repair_coping_long_left_v01.request.json';data=json.loads(q.read_text(encoding='utf-8'));data['references'][0]['sha256']=sha(p);data['references'][0]['role']='Context-only defocused incorrect coping guide; exact native size. Sharp left end and upper/back right endpoint are geometry anchors. Blurred pixels are not final art.';q.write_text(json.dumps(data,indent=2),encoding='utf-8')
g=Path(str(p)+'.generation.json');data=json.loads(g.read_text(encoding='utf-8'));data.update(sha256=sha(p),operation='native crop then mechanical Gaussian defocus for context only; no resized or procedurally painted final pixels',contextOnlyDefocus={'radius':24,'box':[240,350,1254,1030],'restoredRightEndpointBox':[1140,0,1254,640]});g.write_text(json.dumps(data,indent=2),encoding='utf-8')

