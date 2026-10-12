from pathlib import Path
import json,hashlib,os,sys
from datetime import datetime,timezone
R=Path(__file__).resolve().parent.parent;assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c11.json'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pid,ver=sys.argv[1:3];desc=sys.argv[3];guide=R/'guides'/f'{pid}.native-context-{ver}.png';grec=rd(Path(str(guide)+'.generation.json'));p=grec['coordinate']
refs=[{'file':str(guide),'sha256':sh(guide),'role':'EDIT TARGET. Exact unscaled adjacent native/candidate anchors over layout-only blurry crop. Preserve actual sharp anchor geometry; redraw only unknown crop area.'}]+rd(R/'references.json')
prompt=f'''Use case: precise-object-edit. Produce ONE native opaque square, desired 1254 x 1254 pixels, a small exact-position crop of the continuous daylight Q Daoist Eight Immortals island game map.

Image1 is the exact EDIT TARGET, not an example. Its blurry area is only a coordinate/layout guide to redraw at native painted detail. Its sharp parts are already-finished neighboring artwork at their TRUE pixel scale and location. Continue the sharp objects seamlessly through the blurry region, keeping their curve tangents, spacing, silhouette, perspective, lighting and texture density. Remove the visual sharp/blurry transition. Never render the guide's rectangular anchor outline, freeze a bad blur boundary, zoom out, fit an entire neighboring image inside this crop, or invent another building.
Image2 is the sole overall layout authority. Image3 is independent material/architecture style only, NOT coordinates. Image4 is the approved primary Q Daoist painting-style reference; take its refined rounded hand-painted forms, NOT its UI, lettering, people or night lighting.

Exact crop {pid}; global native box {p['nativeGlobalBox']} on the57344 square art grid; layout1254 reference box {p['layoutReferenceBox']}. Final core is local[115,115,1139,1139]. Continue upward/leftward from real finished neighbors. RIGHT anchor and BOTTOM anchor must remain at their current true positions. Some bottom/right parts have a full230 native overlap, but the corrected lower-right roof has only115 verified pixels at the BOTTOM y1139..1253, and some right parts only115 at x1139..1253. Where the guide is blurry inside those bands it is unknown and must be completed. Never copy any sharp/blurry straight line into the painting. Do not restore historical blue roof color bars.

LOCAL CONTENT: {desc}

Rendering: clear crisp painted edges, plump rounded forms, clean bright daylight, matching neighboring restrained fine directional brushwork and dimensional shade. Blue glazed roof surfaces must stay continuous within each curved barrel, with one dark separating gutter and complete curved collars; no straight material-tone division through a barrel. Gold roof trims remain connected whole objects with rounded highlights; red supports stay structural. Natural pale grey/blue-grey stone, subtle low-contrast joints. No photoreal noise, thick scratches, plastic glare, glow, sharpening halos, or enlarged blurry final pixels.
Do not add buildings, columns, trees, lanterns, signs, ground decorations, medallions or props absent from this crop. Keep all layout courtyards/openings/routes and coast unchanged. Existing festival details only where actually present. No people, NPCs, animals, HUD, letters, labels, grid, watermark or comparison panels. No resize/warp/rotation/mirroring of geometry. Output only the single completed native square.'''
pf=R/'prompts'/f'{pid}_{ver}.prompt.txt';rf=R/'prompts'/f'{pid}_{ver}.request.json';assert not pf.exists() and not rf.exists();pf.write_text(prompt,encoding='utf-8')
request={'createdAt':datetime.now(timezone.utc).isoformat(),'promptPath':str(pf),'promptSha256':sh(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'coordinate':p,'status':'prepared_not_submitted'};wr(rf,request)
prog=rd(R/'progress-r08_c11.json');prog.update({'status':'submitting_builtin','currentPatch':pid,'inFlight':True,'nextStep':'Exact inputs already viewed; submit this single recorded builtin native request and save receipt/output.'});wr(R/'progress-r08_c11.json',prog)
print(json.dumps({'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}))
