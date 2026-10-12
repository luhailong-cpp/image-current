"""Prepare a new native repair across the old trial's lower perimeter."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent
S=T/'repairs'/'single-stone-railing-20261012-v2'
D=T/'repairs'/'single-stone-railing-bottom-20261012-v3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):
    with Image.open(p) as im:size=list(im.size)
    return {'path':str(p),'sha256':sha(p),'pixels':size}
def write(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
s=json.loads((S/'composition.json').read_text(encoding='utf-8-sig'))
assert s['candidate']['sha256']=='6289d18745f81a03a428dd931a73d6db947ea4db84b16bf57a3446e3f1e4a7c8'
for k in ('candidate','context'):assert sha(s[k]['path'])==s[k]['sha256']
D.mkdir(parents=True,exist_ok=True);box=[280,2320,1534,3574];target=D/'edit-target-native-1254.png'
with Image.open(s['candidate']['path']) as im:
    with target.open('xb') as f:im.crop(box).save(f,format='PNG')
prompt='''Use case: precise-object-edit. Asset: existing daylight Taoist chibi game city tile. The only input image is the ONLY EDIT TARGET: one exact unscaled 1254x1254 crop from the current native-composed tile.
Primary request: repair the small clipped/duplicated green leaves and interrupted foliage silhouettes along the horizontal old/new join around target y404 (global tile y2724). The affected attached planting extends roughly target x100..1100, y260..700. Make each leaf and twig have one coherent full silhouette across this join, remove chopped leaf tips, overlapping ghosts and straight cut marks. Retain the original low planting strip against the stone railing base. Continue the existing natural grey slab grout and stone base smoothly through this same small affected strip.
The correct scene has exactly ONE pale stone railing. Keep its entire upper geometry, carved panels and direction; do not add a second rail, pillar or finial. Preserve every red festival container fragment at the bottom/left, all original paper scraps, water, paving grid and other objects in exactly the same positions. Edit only clipped foliage and its immediate contact shadow/ground around the join; keep the outer200 pixels and all other scene regions unchanged. No new pots, ornaments, people, free-standing tree, furniture, building, label, lettering, watermark or border. Keep exact camera and framing; do not zoom, crop, scale, rotate or recenter. Preserve the existing painted texture, quiet daylight and colors. Return one genuinely native opaque 1254x1254 PNG.'''
req={'prompt':prompt,'referenced_image_paths':[str(target)],'transparent_background':False}
write(D/'request.json',req);(D/'prompt.txt').write_text(prompt,encoding='utf-8')
write(D/'preparation.json',{'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':T.name,'version':D.name,'sourceCandidate':s['candidate'],'sourceContext':s['context'],'sourceAssembly':{'path':str(S/'composition.json'),'sha256':sha(S/'composition.json')},'target':art(target),'cropBoxIn4096':box,'references':[dict(art(target),role='only edit target, current native-composed foliage and paving')],'tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,'resized':False,'formalAccepted':False,'status':'prepared_not_yet_generated'})
print(json.dumps({'request':str(D/'request.json'),'target':str(target)}))
