from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
g=R/'guides/r12_c13_p41.native-edit-v03.png';m=json.loads(Path(str(g)+'.generation.json').read_text())
b=R/'native/r12_c13_p41_v02.png';e=R/'native/r12_c13_p42_v01.png'
im=Image.open(b).convert('RGB');im.paste(Image.open(e).convert('RGB').crop((0,0,230,1254)),(1024,0));im.save(g)
m['sha256']=sha(g);m['derivedFrom']=m['derivedFrom'][:2];m['placements']=m['placements'][:2];m['note']='Preserve already passed north actual core seam from original body. Its outer native overlap differs from latest north redraw; pasting full north overlap would create a new horizontal boundary at y230. No new north paste used.';write(Path(str(g)+'.generation.json'),m)
p=R/'prompts/r12_c13_p41_v03.request.json';r=json.loads(p.read_text());r['references'][0]['sha256']=sha(g);write(p,r)
print(json.dumps({'guideSha256':sha(g)}))
