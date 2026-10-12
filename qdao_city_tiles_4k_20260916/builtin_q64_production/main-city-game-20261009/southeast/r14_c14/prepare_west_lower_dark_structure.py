from pathlib import Path
from datetime import datetime,timezone
import sys,json,uuid,importlib.util
import numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14');R=T/'repairs'
spec=importlib.util.spec_from_file_location('i',T/'internal_repairs.py');I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)
old=R/'west-middle-left-dominant-20261011T173851-d8f59e02';p=I.read(old/'preparation.json');cur=I.read(T/'candidate/latest-assembly.json')
ver='west-lower-dark-structure-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8];d=R/ver;d.mkdir()
p.update(westCrop=[3456,2842,4096,4096],currentCrop=[0,2842,614,4096])
raw=Image.new('RGB',(1254,1254));raw.paste(Image.open(p['westCore']['path']).convert('RGB').crop(tuple(p['westCrop'])),(0,0));raw.paste(Image.open(cur['candidate']['path']).convert('RGB').crop(tuple(p['currentCrop'])),(640,0));I.png(d/'source-1254.png',raw)
boxes=[[640,200,920,480]];guide=raw.copy();dr=ImageDraw.Draw(guide)
for a,b,c,e in boxes:dr.rectangle((a,b,c-1,e-1),fill=(255,0,255))
before=np.array(guide);draw=ImageDraw.Draw(guide);sk=[]
for points in [[[640,404],[735,340],[825,279],[885,242]],[[853,200],[880,235],[900,264],[920,291]]]:
 for width,color in [(20,[162,145,116]),(16,[250,244,231]),(8,[62,46,25])]:
  draw.line([tuple(a) for a in points],fill=tuple(color),width=width,joint='curve');sk.append({'points':points,'width':width,'rgb':color})
# Final dark branch center crosses into the main groove so the T mouth stays open.
a={'points':[[874,249],[891,238]],'width':8,'rgb':[62,46,25]};draw.line([tuple(v) for v in a['points']],fill=tuple(a['rgb']),width=a['width']);sk.append(a)
arr=np.array(guide);holes=np.all(before==[255,0,255],axis=2);arr[~holes]=before[~holes];I.png(d/'target-1254.png',Image.fromarray(arr))
prompt="""Use case: precise-object-edit. Edit ONLY the LAST exact1254x1254 image of our existing stone pavement. First3 are style references only. Fill only the magenta pixels with matching natural grey stone texture and shadows. The dark brown groove with pale raised stone bevel drawn inside the hole is the required structural guide: keep its precise centerline and width. Continue the wide fixed left groove at x640,y404 to the existing main diagonal as an OPEN T-junction at x885,y242. At the T mouth, the dark groove centers must genuinely meet with no white bevel or bright cap separating them. Round the adjacent stone corners naturally, preserve the open dark center. Do not move any visible fixed left-side stone or groove. Do not narrow the required branch to a crack, remove it, regularize the grid, or elongate the slab. Preserve all nonmagenta surroundings and exact scale, framing, stone lighting and shadows. No added objects, symbols, blue bands, text, zoom, pan, or resize. Output opaque native1254x1254PNG with all magenta removed."""
(d/'prompt.txt').write_text(prompt,encoding='utf-8');refs=p['references'][:3]+[{**I.art(d/'target-1254.png'),'role':'LAST edit target: one magenta fill area with fixed dark groove skeleton and open T mouth'}]
I.js(d/'request.json',{'prompt':prompt,'referenced_image_paths':[a['path'] for a in refs],'transparent_background':False})
p.update(version=ver,preparedAt=I.now(),sourceCandidate=cur['candidate'],sourceContext=cur['context'],rawTarget=I.art(d/'source-1254.png'),guide=I.art(d/'target-1254.png'),guideHoles=boxes,guideSkeletons=sk,skeletonClip='only original magenta holes; guide structure is not final artwork; output retained only from builtin native',references=refs,request=I.art(d/'request.json'),prompt=I.art(d/'prompt.txt'),derivedFrom=I.art(old/'preparation.json'))
I.js(d/'preparation.json',p);print(json.dumps({'version':ver,'target':str(d/'target-1254.png'),'request':str(d/'request.json')},indent=2))

