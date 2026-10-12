from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
from datetime import datetime,timezone
P=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r13_c05/pipeline')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=P/'prompts/p04_02.resumed-full64-v01.request.json'; req=json.loads(base.read_text(encoding='utf-8'))
control=P/'guides/p04_02.diagonal-control-v03.line-guide-not-art.png'; assert not control.exists()
im=Image.new('RGB',(1254,1254),(194,197,197)); g=ImageDraw.Draw(im)
g.line([(445,0),(445,1254)],fill=(60,70,75),width=7)
g.line([(445,465),(1254,1030)],fill=(60,70,75),width=7)
g.line([(445,720),(1190,1254)],fill=(60,70,75),width=7)
for y in (240,485,955): g.line([(0,y),(445,y)],fill=(60,70,75),width=7)
im.save(control)
der={'file':str(control),'sha256':sha(control),'gameArt':False,'role':'schematic only, line coordinates from inspected original layout and native top/left anchors, no source tolerance allowance',
 'width':1254,'height':1254,'operations':'new flat schematic with only explicit line positions; never final pixels','finalPixelCompositing':False,
 'lines':[{'points':[[445,0],[445,1254]]},{'points':[[445,465],[1254,1030]]},{'points':[[445,720],[1190,1254]]}],
 'inputGuide':req['references'][0]}
Path(str(control)+'.derivation.json').write_text(json.dumps(der,indent=2)+'\n',encoding='utf-8')
prefix='''CONTENT LOCK: Edit Image1 at exact1254 square close crop. Image5 is a schematic LINE-POSITION GUIDE ONLY, not art or a style: use ONLY its dark lines as existing shallow stone joints. Keep vertical x445 continuous from top to bottom, no vertical at x230. Exactly2 right-field parallel diagonal seams point DOWNWARD RIGHT: (445,465)->(1254,1030) and (445,720)->(1190,1254). LEFT of x445 native horizontal grooves y240/y485/y955 stop atx445. No other grout lines, cross-joints, diamond grid or raised stair. Native top230 and left230 are exact detailed neighbors, match their material/lines; their image strip boundaries are not joints. Tiny red/gold right-top object side remains clipped in its existing footprint. All other image area stays broad quiet flat gray stone under soft existing shade. Render crisp restrained rounded shallow seams and faint brush variation, no new object, letters or cloudy material patches. Preserve this exact crop and scale. Image5 dark markers themselves must not appear; they indicate geometry for finished stone seams only.'''
prompt=prefix+'\n\nUse case:'+req['prompt'].split('Use case:',1)[1]
q=P/'prompts/p04_02.diagonal-control-v03.request.json'; pf=q.with_name(q.name.replace('.request.json','.prompt.txt')); assert not q.exists() and not pf.exists()
pf.write_text(prompt,encoding='utf-8'); req.update(prompt=prompt,promptFile=str(pf),promptSha256=sha(pf),preparedAtUtc=datetime.now(timezone.utc).isoformat())
req['references'].append({'file':str(control),'sha256':sha(control),'role':'schematic line-position control only; never final art'})
req['referenced_image_paths'].append(str(control)); req['explicitRefinementOf']={'file':str(base),'sha256':sha(base)}
q.write_text(json.dumps(req,indent=2)+'\n',encoding='utf-8')
for attempt in ['diagonal-direction-v02']:
 r=P/'receipts'/f'p04_02.{attempt}.receipt.json'; d=json.loads(r.read_text(encoding='utf-8')); out=r.with_name(r.name.replace('.receipt.json','.disposition.json')); assert not out.exists()
 out.write_text(json.dumps({'native':d['native'],'explicitlyRejected':True,'reason':'Wrong x238 vertical joint at strip transition, topx445 joint terminated and extra diagonal grid; not ingested, selected or propagated.','actualModel':None,'actualQuality':None},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(q),'control':str(control)}))
