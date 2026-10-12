from pathlib import Path
from datetime import datetime,timezone
import sys,json,uuid,importlib.util
import numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14');R=T/'repairs'
spec=importlib.util.spec_from_file_location('i',T/'internal_repairs.py');I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)
old=R/'west-middle-left-dominant-20261011T173851-d8f59e02';p=I.read(old/'preparation.json');cur=I.read(T/'candidate/latest-assembly.json')
ver='west-middle-dark-structure-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8];d=R/ver;d.mkdir()
raw=Image.new('RGB',(1254,1254));raw.paste(Image.open(p['westCore']['path']).convert('RGB').crop(tuple(p['westCrop'])),(0,0));raw.paste(Image.open(cur['candidate']['path']).convert('RGB').crop(tuple(p['currentCrop'])),(640,0));I.png(d/'source-1254.png',raw)
boxes=[[640,600,1085,930]];guide=raw.copy();dr=ImageDraw.Draw(guide)
for a,b,c,e in boxes:dr.rectangle((a,b,c-1,e-1),fill=(255,0,255))
before=np.array(guide);draw=ImageDraw.Draw(guide)
sk=[]
for points in [[[640,856],[735,792],[830,728],[922,665]],[[870,600],[920,663],[970,729],[1020,795],[1070,861],[1085,881]]]:
 for width,color in [(25,[162,145,116]),(20,[250,244,231]),(10,[62,46,25])]:
  draw.line([tuple(a) for a in points],fill=tuple(color),width=width,joint='curve');sk.append({'points':points,'width':width,'rgb':color})
arr=np.array(guide);holes=np.all(before==[255,0,255],axis=2);arr[~holes]=before[~holes];I.png(d/'target-1254.png',Image.fromarray(arr))
prompt="""Use case: precise-object-edit. Edit ONLY the LAST exact1254x1254 image of existing stone game pavement; first3 images are style only. Fill ONLY magenta pixels with matching natural grey stone slab texture and shadows. The dark-brown groove with pale raised bevel already drawn across the magenta hole is a FIXED REQUIRED STRUCTURE, and must remain at exactly the displayed route and width. Do not move, delete, simplify, narrow or change either existing dark groove or the T intersection. Preserve every visible non-magenta pixel, including this structural guide. Replace magenta with two separate large stone surfaces divided by that fixed wide dark groove. The groove entering from x640,y856 must remain a wide dark groove, NOT a crack; it meets the crossing at x922,y665. Keep all existing left-side slabs, endpoints and shadows exactly. Do not regularize the pavement or merge the two stone slabs. No added objects, text, blue bands, zoom, pan or scaling. Output an opaque native1254x1254PNG at exactly the same framing, all magenta removed."""
(d/'prompt.txt').write_text(prompt,encoding='utf-8');refs=p['references'][:3]+[{**I.art(d/'target-1254.png'),'role':'LAST edit target: magenta fill with fixed dark groove structure sketched only within hole'}]
I.js(d/'request.json',{'prompt':prompt,'referenced_image_paths':[a['path'] for a in refs],'transparent_background':False})
p.update(version=ver,preparedAt=I.now(),sourceCandidate=cur['candidate'],sourceContext=cur['context'],rawTarget=I.art(d/'source-1254.png'),guide=I.art(d/'target-1254.png'),guideHoles=boxes,guideSkeletons=sk,skeletonClip='only original magenta holes; guide structure is not final artwork; output retained only from builtin native',references=refs,request=I.art(d/'request.json'),prompt=I.art(d/'prompt.txt'),derivedFrom=I.art(old/'preparation.json'))
I.js(d/'preparation.json',p);print(json.dumps({'version':ver,'target':str(d/'target-1254.png'),'request':str(d/'request.json')},indent=2))

