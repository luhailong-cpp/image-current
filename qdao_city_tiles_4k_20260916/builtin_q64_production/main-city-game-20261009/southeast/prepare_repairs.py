from pathlib import Path
import json,hashlib,sys
from PIL import Image
B=Path(__file__).resolve().parent;T=B/'r13_c13';R=T/'repairs'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=json.loads((R/'repair-specs.json').read_text(encoding='utf-8'))
contract=json.loads((B.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
for id in sys.argv[1:]:
    box,edit=spec[id]['cropBox'],spec[id]['edit']
    source=T/'candidate'/'r13_c13-4k-candidate-repaired.png'
    target=R/f'{id}-target.png';Image.open(source).crop(box).save(target)
    refs=[contract['layoutReference'],contract['detailStyleReference'],contract['primaryStyleReference'],str(target)]
    prompt=f"""Use case: precise-object-edit, native geometry repair of a current game-map crop.
Images1/2/3 are ONLY approved layout, close-up material and style references. Image4, THE LAST IMAGE, is the ONLY edit target. Return exactly1254x1254 pixels, opaque. Keep the exact image framing, camera, scale, lighting and art style. This is a very small spatial crop, not a standalone scene.
{edit}
Preserve the outermost64 pixels of this target unchanged and make the edited interior join those native edges smoothly. Existing objects continue beyond the image; do not zoom out, reframe or fit whole objects into this crop. No new objects or buildings, no duplicated features, no blank areas, no text/labels/borders. Retain the existing bright clean rounded Taoist chibi game illustration and current native detail."""
    (R/f'{id}.prompt.txt').write_text(prompt,encoding='utf-8')
    (R/f'{id}.request.json').write_text(json.dumps({'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False},ensure_ascii=False,indent=2),encoding='utf-8')
    meta={'id':id,'operation':'unscaled native crop for image_gen geometry repair','source':str(source),'sourceSha256':sha(source),'cropBoxIn4096':box,'width':1254,'height':1254,'resized':False,'target':str(target),'targetSha256':sha(target),'references':[{'path':p,'sha256':sha(p),'dimensions':list(Image.open(p).size),'role':r} for p,r in zip(refs,['approved layout','approved material','approved primary style','only edit target'])]}
    (R/f'{id}.target.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'id':id,'target':str(target),'cropBox':box}))

