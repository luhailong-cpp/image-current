from pathlib import Path
import sys,json,uuid,importlib.util
from datetime import datetime,timezone
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14');R=T/'repairs'
spec=importlib.util.spec_from_file_location('I',T/'internal_repairs.py');I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)
sm=R/'west-middle-skeleton-selected-v1-20261011/composition.json';m=I.read(sm);p=I.read(m['preparation']['path'])
for k in ['candidate','context','westCore']:I.checked(m[k])
ver='west-middle-local-join-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8];d=R/ver;d.mkdir()
raw=Image.new('RGB',(1254,1254));raw.paste(Image.open(m['westCore']['path']).convert('RGB').crop(tuple(p['westCrop'])),(0,0));raw.paste(Image.open(m['candidate']['path']).convert('RGB').crop(tuple(p['currentCrop'])),(315,0));I.png(d/'source-1254.png',raw)
boxes=[[315,150,435,230],[315,740,550,960]]
guide=raw.copy();dr=ImageDraw.Draw(guide)
for a,b,c,e in boxes:dr.rectangle((a,b,c-1,e-1),fill=(255,0,255))
I.png(d/'target-1254.png',guide)
prompt="""Use case: precise-object-edit. Edit ONLY the LAST image, a1254x1254 exact unscaled crop of our existing game-map stone pavement. The first3 images provide style only. Fill the TWO small magenta holes with the matching continuous stone and WIDE DARK BEVELED GROUT. Every visible non-magenta pixel is immutable. The left sides of the two holes at x315 are an already-final neighboring core and CANNOT MOVE. Upper hole: join the wide groove entering the LEFT edge at y193 to the same wide groove leaving the RIGHT edge near y78 (outside small hole) by continuing the existing visible geometry inside the hole. Lower hole: match the EXACT fixed left dark groove endpoint at x315,y856, smoothly join to the right wide dark groove near x550,y750. Keep the groove wide with bright stone bevels and deep dark center. A gentle irregular stone polygon is correct; do not refit or regularize the entire stone grid. Preserve every pixel outside the two magenta holes, particularly all left-side grooves and shadows. Match both sides of every hole with no offset, dangling groove, doubled edge, color jump or vertical strip. No added objects, symbols, blue bands, text, perspective changes, zoom, pan, resizing. Output opaque native1254x1254 PNG with exact framing. Remove all magenta."""
(d/'prompt.txt').write_text(prompt,encoding='utf-8');refs=p['references'][:3]+[{**I.art(d/'target-1254.png'),'role':'LAST edit target; two small holes in immutable native trial composite'}]
I.js(d/'request.json',{'prompt':prompt,'referenced_image_paths':[a['path'] for a in refs],'transparent_background':False})
p.update(version=ver,preparedAt=I.now(),sourceCandidate=m['candidate'],sourceContext=m['context'],rawTarget=I.art(d/'source-1254.png'),guide=I.art(d/'target-1254.png'),guideHoles=boxes,guideSkeletons=[],references=refs,request=I.art(d/'request.json'),prompt=I.art(d/'prompt.txt'),sourceManifest=I.art(sm),derivedFrom=I.art(m['preparation']['path']))
I.js(d/'preparation.json',p)
print(json.dumps({'version':ver,'request':str(d/'request.json'),'target':str(d/'target-1254.png')},indent=2))

