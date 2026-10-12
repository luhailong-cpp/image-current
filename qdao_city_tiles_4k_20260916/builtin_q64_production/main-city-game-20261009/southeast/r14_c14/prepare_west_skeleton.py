from pathlib import Path
from datetime import datetime,timezone
import sys,json,uuid,importlib.util
import numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs'
spec=importlib.util.spec_from_file_location('i',T/'internal_repairs.py');I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)
old=R/'west-middle-exact-joints-20261011T162236-aa6849a7';p=I.read(old/'preparation.json')
ver='west-middle-skeleton-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8];d=R/ver;d.mkdir()
skeletons=[{'points':[[315,193],[340,176],[365,157],[390,131],[413,99],[440,58],[472,35]],'width':10,'rgb':[0,255,255]},{'points':[[315,856],[400,798],[500,729],[597,665]],'width':10,'rgb':[0,255,255]}]
guide=Image.open(p['guide']['path']).convert('RGB');before=np.array(guide);sk=guide.copy();dr=ImageDraw.Draw(sk)
for a in skeletons:dr.line([tuple(pt) for pt in a['points']],fill=tuple(a['rgb']),width=a['width'],joint='curve')
arr=np.array(sk);holes=np.all(before==[255,0,255],axis=2);arr[~holes]=before[~holes];I.png(d/'target-1254.png',Image.fromarray(arr))
prompt=I.read(old/'request.json')['prompt']+'''
MANDATORY VISUAL STRUCTURE: Bright CYAN lines INSIDE the magenta holes mark the exact missing WIDE DARK GROUT centerlines. Follow BOTH cyan centerlines precisely. They are construction guides, not paint or objects; replace cyan and magenta with finished stone and wide dark beveled grout. The lower cyan line from the left hole edge to the main diagonal is a necessary full T-junction, never a hairline crack. The upper cyan path intentionally makes a gentle custom-cut large slab connection to reconcile two fixed endpoints; preserve its endpoints and do not shift any left-side junction. Do not simplify away either cyan groove or regularize the surrounding grid. Remove all cyan and magenta from final image.
'''
(d/'prompt.txt').write_text(prompt,encoding='utf-8');refs=p['references'][:3]+[{**I.art(d/'target-1254.png'),'role':'LAST only edit target: immutable core crops with magenta holes and cyan required grout skeletons clipped strictly inside holes'}]
req={'prompt':prompt,'referenced_image_paths':[a['path'] for a in refs],'transparent_background':False};I.js(d/'request.json',req)
p.update(version=ver,preparedAt=I.now(),guide=I.art(d/'target-1254.png'),guideSkeletons=skeletons,skeletonClip='only pixels in documented magenta guide holes; all fixed context unchanged',references=refs,request=I.art(d/'request.json'),prompt=I.art(d/'prompt.txt'),derivedFrom=I.art(old/'preparation.json'))
I.js(d/'preparation.json',p)
print(json.dumps({'version':ver,'request':str(d/'request.json'),'target':str(d/'target-1254.png')},indent=2))

