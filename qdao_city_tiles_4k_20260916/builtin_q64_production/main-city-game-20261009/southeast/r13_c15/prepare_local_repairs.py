from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image

T=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=json.loads((T/'candidate'/'latest-assembly.json').read_text(encoding='utf-8-sig'))
base=Path(p['candidate']['path']); im=Image.open(base).convert('RGB')
refs=json.loads(next((T/'records').glob('p01_01*.request.json')).read_text())['referenced_image_paths'][:3]
jobs=[('remove-bell-v1',(850,0,2104,1254),'Remove only the small hanging bell and red tassel at the TOP of this crop, restoring the existing smooth olive-green plaster wall behind it. This bell/tassel was an accidental invented ornament. Preserve the entire white rabbit cheek at right, all wooden trim, bamboo basket fragment at bottom and daylight shadows. Do not add a post or plaque; keep the current wall and wood geometry exactly.'),
      ('remove-extra-cap-v1',(1650,2842,2904,4096),'Remove only the small extra white round railing-post cap near the BOTTOM-RIGHT of this crop and its small pale post segment, restoring continuous existing golden wooden deck edge/fascia behind it. Keep the LARGE existing white round cap at bottom-left unchanged; that is the correct original post. Preserve every timber plank joint, deck outer edge, table-leg fragment, grain scale, and lighting. Do not add any object, alter the deck outline, or remove the large correct left post.')]
for key,box,instruction in jobs:
    out=T/'repairs'/key;out.mkdir(parents=True,exist_ok=True)
    target=out/'target-1254.png';im.crop(box).save(target)
    prompt='Use case: precise-object-edit. Output exactly 1254x1254 opaque pixels. Images1-3 are approved style/layout references only. Image4 LAST is the only edit target, an unscaled crop of existing map artwork. '+instruction+' Change only the named accidental extra ornament and its immediate contact shadow. Everything else and the outermost100 pixels must remain pixel-aligned unchanged. Rounded bright daylight Taoist chibi game painting, warm timber. No zoom, resize, reframe, global redraw, new architecture, extra decoration, text or watermark.'
    (out/'prompt.txt').write_text(prompt,encoding='utf-8')
    write(out/'request.json',{'prompt':prompt,'referenced_image_paths':refs+[str(target)],'transparent_background':False})
    write(out/'preparation.json',{'base':str(base),'baseSha256':sha(base),'target':str(target),'targetSha256':sha(target),'tileBox':box,'resized':False,'createdAt':datetime.now(timezone.utc).isoformat(),'status':'prepared_not_generated'})
    print(json.dumps({'id':key,'target':str(target),'request':str(out/'request.json')}))
