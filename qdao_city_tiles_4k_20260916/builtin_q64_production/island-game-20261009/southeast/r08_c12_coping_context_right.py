from pathlib import Path
from PIL import Image,ImageFilter
import json,hashlib,os
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
R=Path(__file__).resolve().parent;p=R/'guides/r08_c12_repair_coping_long_right_v01.native-context.png'
im=Image.open(p).convert('RGB');blur=im.filter(ImageFilter.GaussianBlur(28));im.paste(blur.crop((115,400,830,1060)),(115,400));im.save(p)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=R/'prompts/r08_c12_repair_coping_long_right_v01.request.json';data=json.loads(q.read_text(encoding='utf-8'));data['references'][0]['sha256']=sha(p);data['references'][0]['role']='Context-only defocused obsolete right coping; sharp left115px newly rebuilt middle coping and existing right post are locked geometry anchors.';q.write_text(json.dumps(data,indent=2),encoding='utf-8')
g=Path(str(p)+'.generation.json');data=json.loads(g.read_text(encoding='utf-8'));data.update(sha256=sha(p),operation='native crop plus mechanical Gaussian defocus for context only, no modified guide pixels enter final art',contextOnlyDefocus={'radius':28,'box':[115,400,830,1060]});g.write_text(json.dumps(data,indent=2),encoding='utf-8')

