from pathlib import Path
import json,shutil,hashlib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;old=D/'W02';d=D/'W02-last-v2';d.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(p),'sha256':sha(p)}
def dump(p,o):p.write_text(json.dumps(o,indent=2,ensure_ascii=False),encoding='utf-8')
p=json.loads((old/'preparation.json').read_text(encoding='utf-8-sig'))
for k in ['target','unmarkedReference','savedMask','alpha','fullAlpha']:
 src=Path(p[k]['path']);assert sha(src)==p[k]['sha256'];dest=d/src.name;shutil.copyfile(src,dest);p[k]=info(dest)
p['references']=[p['target'],p['unmarkedReference']]
prompt="""Precise local repair of stone paving. Produce exactly one opaque native 1254 x 1254 PNG at the identical framing and scale of image 1.
IMAGE 1: magenta-mask edit target. Replace ONLY magenta. IMAGE 2: original true-core boundary, showing the damaged stone joints. The whole left side x0..639 is immutable reference from the neighbor; NEVER change it. Do not change any unmasked pixels.
The ONE required correction is to connect the diagonal groove already coming from the lower-left into x640,y680. Find it visually: above the green leaf, the existing large four-way joint near (595,730) sends a short groove UP AND RIGHT until it is abruptly cut at the magenta left edge. Continue exactly that groove from (640,680) upward-right through the edited area until it connects naturally with the upper-right groove near (915,470). The dark groove center and both beveled stone edges must touch at the left boundary without any gap, turn-back or height jump.
Completely erase the wrong higher floating corner/branch near (645,600), which has NO matching incoming line from the left. Do NOT draw a groove leaving the boundary near y600. Stone texture should be continuous there. Rebuild only the affected local slab borders so that the incoming groove at y680 is the single connected continuation. Keep the lower diagonal main joint endpoints and the leaf-protecting notch fixed; do not move the lower slab edge to make a different disconnected endpoint at the bottom. Preserve thin natural cracks separately from deep stone joints.
The output must preserve the leaf at the bottom-left notch, the red paper, stone rail, warm daylight, paving texture/scale and shadows. No new objects, no blue band, no broad recolor, no blurred cover, no extra crossing/doubled groove. Remove all magenta, retain the exact real pixel framing. Before finishing check that the line coming from (595,730) remains physically connected across x640,y680 into the repaired right side."""
(d/'prompt.txt').write_text(prompt,encoding='utf-8')
req={'schemaVersion':1,'job':'W02-last-v2','tool':'image_gen.imagegen','route':'builtin','actualModel':None,'actualQuality':None,'attemptNumberAtW02':2,'lastTargetedAttemptThisRound':True,'priorFailedSource':info(old/'actual-native-581542e13335b668.png'),'submittedParameters':{'prompt':prompt,'referenced_image_paths':[x['path'] for x in p['references']],'transparent_background':False}}
dump(d/'request.json',req);p['request']=info(d/'request.json');p['prompt']=info(d/'prompt.txt');p['version']='west-stone-joints-20261013-W02-last-v2';p['preparedAtUtc']=datetime.now(timezone.utc).isoformat();p['priorPreparation']=info(old/'preparation.json');p['attemptNumberAtW02']=2
dump(d/'preparation.json',p)
dump(d/'attempt-start.json',{'savedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'prepared_for_actual_builtin_call_not_yet_returned','request':info(d/'request.json'),'preparation':info(d/'preparation.json'),'actualModel':None,'actualQuality':None})
print(json.dumps(req))

