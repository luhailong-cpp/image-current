from pathlib import Path
import sys,json,uuid,importlib.util
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14');R=T/'repairs'
spec=importlib.util.spec_from_file_location('I',T/'internal_repairs.py');I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)
sm=R/'west-middle-dark-selected-v1-20261011/composition.json';m=I.read(sm);p=I.read(m['preparation']['path'])
ver='west-middle-t-mouth-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8];d=R/ver;d.mkdir()
raw=Image.new('RGB',(1254,1254));raw.paste(Image.open(m['westCore']['path']).convert('RGB').crop(tuple(p['westCrop'])),(0,0));raw.paste(Image.open(m['candidate']['path']).convert('RGB').crop(tuple(p['currentCrop'])),(640,0));I.png(d/'source-1254.png',raw)
boxes=[[895,648,945,698]];guide=raw.copy();dr=ImageDraw.Draw(guide)
for a,b,c,e in boxes:dr.rectangle((a,b,c-1,e-1),fill=(255,0,255))
before=np.array(guide);draw=ImageDraw.Draw(guide);sk=[]
paths=[[[902,648],[940,698]],[[895,683],[920,667]]]
for width,color in [(16,[250,244,231]),(8,[62,46,25])]:
 for points in paths:
  draw.line([tuple(a) for a in points],fill=tuple(color),width=width,joint='curve');sk.append({'points':points,'width':width,'rgb':color})
arr=np.array(guide);holes=np.all(before==[255,0,255],axis=2);arr[~holes]=before[~holes];I.png(d/'target-1254.png',Image.fromarray(arr))
prompt="""Use case: precise-object-edit. The LAST image is our existing exact1254x1254 game pavement crop, and must remain pixel-for-pixel fixed outside one tiny50x50magenta hole around the T-junction near x920,y670. First3 images are style references only. Fill the tiny magenta pixels as the same grey stone texture. Preserve the exact sketched dark T-shaped channel inside this tiny hole and connect all THREE exposed dark groove ends. At the T mouth the dark branches MUST physically join into one continuous dark recess. No white rim, bright cap, stone bridge, separation or closure across the mouth. Round only the three immediately adjacent stone corner tips. Keep the size, routes, angles and endpoints of every existing long groove unchanged. Do not redraw any slab, shadow, texture or pixel outside the tiny hole. No objects, text, scaling, zoom or pan. Opaque native1254x1254PNG, unchanged framing, no magenta."""
(d/'prompt.txt').write_text(prompt,encoding='utf-8');refs=p['references'][:3]+[{**I.art(d/'target-1254.png'),'role':'LAST edit target: tiny50x50hole with open dark T skeleton, rest fixed'}]
I.js(d/'request.json',{'prompt':prompt,'referenced_image_paths':[a['path'] for a in refs],'transparent_background':False})
p.update(version=ver,preparedAt=I.now(),sourceCandidate=m['candidate'],sourceContext=m['context'],rawTarget=I.art(d/'source-1254.png'),guide=I.art(d/'target-1254.png'),guideHoles=boxes,guideSkeletons=sk,references=refs,request=I.art(d/'request.json'),prompt=I.art(d/'prompt.txt'),sourceManifest=I.art(sm),derivedFrom=I.art(m['preparation']['path']))
I.js(d/'preparation.json',p)
print(json.dumps({'version':ver,'request':str(d/'request.json'),'target':str(d/'target-1254.png')},indent=2))

