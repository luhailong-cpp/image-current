"""Write exact native-edit request and inputs before invoking the builtin tool."""
from pathlib import Path
import json,sys
from workflow import ROOT,read,write,sha,patch,progress
pid=sys.argv[1]; version=sys.argv[2]; description=sys.argv[3]; neighbors=sys.argv[4:]
p=patch(pid)
guide=ROOT/'guides'/f'{pid}.native-context-{version}.png'
if not guide.exists():guide=ROOT/'guides'/f'{pid}.native-context.png'
if not guide.exists():guide=ROOT/'guides'/f'{pid}.layout-only.png'
refs=[{'file':guide.as_posix(),'sha256':sha(guide),'role':'EDIT TARGET / exact coordinate guide. Sharp adjacent overlap is immutable, blurry region requires native redraw. Guide not usable as final art.'}]
for n in neighbors:
    f=ROOT/'native'/n;refs.append({'file':f.as_posix(),'sha256':sha(f),'role':'Adjacent native patch, continuity authority. Preserve overlap tile contours, shade and scale.'})
refs+=read(ROOT/'references.json')
prompt=f'''Use case: precise-object-edit. Produce one native square game-art patch for the continuous daylight Eight Immortals island in 五行奇谈, desired 1254 x 1254 pixels.

Attached image 1 is the EDIT TARGET: exact coordinate guide, partly blurry overview crop and partly sharply rendered adjacent native overlap. Redraw ONLY blurry area into matching native detail. Keep every pixel in the sharp overlap region exactly fixed. It is already correctly positioned. Do not reproduce the visual boundary between sharp and blurry content. Continue the shapes crossing that boundary, preserving location, tangent, spacing, shade and hand-painted scale. Output a single complete crop, no multi-panel comparison.
Attached adjacent native images are continuity references; they show the area OUTSIDE this crop plus overlap. Do not fit the full neighboring image inside this crop. A horizontal neighbor contributes its rightmost 230 pixels to this crop's leftmost 230 pixels; a vertical neighbor contributes its bottommost 230 pixels to this crop's topmost 230 pixels.
Last three attached images, in order: full island sole LAYOUT authority; independent close-up for MATERIALS ONLY (not coordinates); approved mail UI PRIMARY PAINTING STYLE ONLY (no UI, letters, characters or night lighting). Learn rounded bright elegant Q Daoist hand-painted surfaces and restrained warm gold from the style references.

Exact crop identity: {pid}. Global native extent {p['nativeGlobalBox']} in 57344 square map; overview extent {p['layoutReferenceBox']} in 1254 square reference. Core local [115,115,1139,1139). Never zoom out or invent a miniature island/building inside this small crop.
LOCAL CONTENT AND GEOMETRY: {description}

Keep clear crisp painted contours, rounded full forms, bright clean daylight, restrained material texture and soft dimensional shading. No photoreal grain, heavy scratches, plastic glare, excessive brush noise, blurry enlarged pixels, fake sharpening, halos, dark lighting or washed-out glow.

Global invariants: eight separate immortal residences, four per side, with existing identity props and open courtyards; do not merge or add residences. North central main hall, southwest lotus pavilion and south gate are EXTRA buildings. Central taiji plaza, cross roads and circulation continuous. Southeast dock and short south route preserved; no larger coast/gate exterior; no new free-standing coastal or plaza trees, no potted trees. Trees only at existing buildings/walls. Natural pale grey/blue-grey stone slabs, weak joints, appropriate wood/sand; no red ground. Daylight; architectural Spring Festival red doors/windows/papercuts/couplets/eave lanterns, sparse Lantern/Mid-Autumn accents only where present in layout. Sparse spent red scraps/black-mouth tubes/wall-side boxes must not block paths. Do not add those objects when outside this exact crop. No people, NPCs, players, animals, HUD, labels, text or watermark. Opaque square output.
'''
prompt_file=ROOT/'prompts'/f'{pid}_{version}.prompt.txt';prompt_file.write_text(prompt,encoding='utf-8')
request={'promptPath':prompt_file.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}}
write(ROOT/'prompts'/f'{pid}_{version}.request.json',request)
progress(status='generating',currentPatch=pid,nextStep='Builtin image_gen request recorded; generate and inspect adjacency',lastError=None)
print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False},ensure_ascii=True))
