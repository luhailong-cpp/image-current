"""Prepare an immutable native crop edit; no artwork is drawn or resized."""
from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
from PIL import Image
T=Path(__file__).resolve().parent
D=T/'repairs'/'single-stone-railing-20261012-v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):
    with Image.open(p) as im:size=list(im.size)
    return {'path':str(p),'sha256':sha(p),'pixels':size}
latest=json.loads((T/'candidate'/'latest-assembly.json').read_text(encoding='utf-8-sig'))
assert latest['candidate']['sha256']=='e4e2e63caf50abeffcffc2cccb4e38c81128c1bf8699405aa57e17bf466042d6'
for k in ('candidate','context','manifest'):assert sha(latest[k]['path'])==latest[k]['sha256']
D.mkdir(parents=True,exist_ok=True)
box=[300,1470,1554,2724]
target=D/'edit-target-native-1254.png'
if not target.exists():
    with Image.open(latest['candidate']['path']) as im:
        with target.open('xb') as f:im.crop(box).save(f,format='PNG')
with Image.open(latest['candidate']['path']) as im,Image.open(target) as actual:assert im.crop(box).tobytes()==actual.tobytes() and actual.size==(1254,1254)
guide=T/'layout-only'/'p03_01_v20261012T122703_8f086cf0-native-anchor-guide.png'
upper=T/'native'/'p02_01_v20261012T121007_d79fed1c.png'
prompt='''Use case: precise-object-edit. Asset: one opaque native 1254x1254 patch of an existing daylight Taoist chibi city game illustration.
Input 1 is a layout/continuity guide ONLY. Its top 230 pixels show the correct single stone railing, and its coarse lower blocks are geometry guidance, never output pixels. Input 2 is the real native upper neighbor showing the correct original railing and its approved one post. Input 3, THE LAST IMAGE, is the ONLY EDIT TARGET: an unscaled 1254-square crop from the assembled 4K candidate.
Primary request: eliminate the accidentally duplicated FRONT/LOWER stone railing and its extra lower post in the edit target. There must be exactly ONE continuous stone railing along the pond, the upper/back railing already crossing the target from upper-left toward lower-right. Preserve that correct upper/back rail, its diagonal position, width, pale stone finish and carved panel edges. The wrong front rail starts underneath it on the left, separated by a narrow leaf-filled channel, and runs parallel below it. Remove the lower/front rail and the wrongly restarted lower pillar; reveal matching existing grey paved ground and attached low green foliage on the land side. Do not create a second fence, a raised planter wall or a new post.
Keep the correct back railing and all pond water/reflections, terrace wood, approved existing vegetation and sparse red paper pieces unchanged in position and scale. Reconstruct only ground/attached foliage needed to replace the incorrect duplicate. No new finial, ornament, architecture, red container, free-standing tree, pot, person, lettering, label or watermark.
Keep exact camera, crop, framing and native pixel detail density. Do not rotate, pan, scale, zoom or fit a whole object. Preserve outer 48 pixels wherever the correct original geometry occurs; continue grey slab grout and plant silhouettes seamlessly through the affected boundary. The result must be one genuine native opaque 1254x1254 PNG with no border or diagram marks. Match the existing clean rounded painted materials and natural daylight exactly. This is a local object removal, never a whole-scene remake.'''
request={'prompt':prompt,'referenced_image_paths':[str(guide),str(upper),str(target)],'transparent_background':False}
prep={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r14_c15','version':D.name,'sourceCandidate':latest['candidate'],'sourceContext':latest['context'],'sourceAssembly':latest['manifest'],'target':art(target),'cropBoxIn4096':box,'references':[dict(art(p),role=r) for p,r in [(guide,'geometry and approved single railing continuity guide only'),(upper,'native upper neighbor correct single railing'),(target,'only edit target')]],'tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,'resized':False,'formalAccepted':False,'status':'prepared_not_yet_generated'}
for p,d in [(D/'request.json',request),(D/'preparation.json',prep)]:
    if p.exists():assert json.loads(p.read_text(encoding='utf-8-sig'))==d if p.name=='request.json' else json.loads(p.read_text(encoding='utf-8-sig'))['sourceCandidate']==prep['sourceCandidate']
    else:
        with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
if not (D/'prompt.txt').exists():(D/'prompt.txt').write_text(prompt,encoding='utf-8')
print(json.dumps({'directory':str(D),'target':str(target),'upper':str(upper),'request':str(D/'request.json'),'preparation':str(D/'preparation.json')}))
