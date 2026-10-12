import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
ROOT=Path(r'D:/work/image/designs/creature-combat-20261005/pets/01-zhuling')
R=ROOT/'records/cast/E';Q=ROOT/'qa/cast/E'
notes=json.loads((Q/'static-inspection.json').read_text(encoding='utf-8'))
notes['frames'].update(json.loads((Q/'final-notes.json').read_text(encoding='utf-8')))
notes['reviewedAt']=datetime.now(timezone.utc).isoformat()
notes['playback']='pending parent final normal and 0.25x continuous review'
(Q/'static-inspection.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2),encoding='utf-8')
rows=[];hashes=set()
for i in range(1,17):
 f=f'{i:02d}';p=R/f'{f}.generation.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
 d['visualStatus']='viewed-static';d['visualNotes']=[notes['frames'][f]]
 receipt=json.loads((R/f'{f}.receipt.json').read_text(encoding='utf-8-sig'))
 if receipt.get('referenceRoles'):
  for j,rr in enumerate(d['references']): rr['purpose']=receipt['referenceRoles'][j]
 if i in (6,10,11): d['references'][3]['purpose']='rejected native same-frame candidate as targeted AI repair input'
 pp=Path(d['file']);im=Image.open(pp);im.load();a=im.getchannel('A');h=hashlib.sha256(pp.read_bytes()).hexdigest()
 assert im.size==(1024,1024) and im.mode=='RGBA' and a.getextrema()==(0,255)
 assert h==d['sha256'] and h not in hashes
 hashes.add(h)
 assert Path(d['prompt']).exists() and Path(d['evidence']['receipt']).exists()
 for ref in d['references']:
  assert Path(ref['path']).exists() and hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest()==ref['sha256']
 ni=Image.open(d['native']['path']).convert('RGBA');na=ni.getchannel('A');w,hh=ni.size
 ne=[sum(v>200 for v in na.crop(box).get_flattened_data()) for box in [(0,0,w,1),(0,hh-1,w,hh),(0,0,1,hh),(w-1,0,w,hh)]]
 d['nativeOpaqueBorderPixelCountsTLBR']=ne
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 rows.append({'frame':i,'file':str(pp),'sha256':h,'width':1024,'height':1024,'durationMs':45,'pivot':[0.5,0.08],'event':'release' if i==10 else None,'generationRecord':str(p),'native':d['native'],'alphaBBox':a.getbbox(),'nativeOpaqueBorderCountsTBLR':ne,'visualStatus':'static-reviewed; playback pending parent'})
for f,reason in [('06','Highest wing tip touched native top edge'),('10','Ray too long and raised far wing near boundary'),('11','Outer wings spread too near native side boundaries'),('15','Wing recovery dropped too far from preceding ready pose')]:
 p=R/f'{f}.attempt-01.generation.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
 if d['file']!=d['native']['path']: d['replacedExport']={'file':d['file'],'sha256':d['sha256'],'status':'overwritten by accepted AI retry'}
 d['file']=d['native']['path'];d['sha256']=d['native']['sha256'];d['width']=d['native']['width'];d['height']=d['native']['height'];d['mode']=d['native']['mode'];d['operation']='native rejected candidate; derived runtime candidate replaced'
 d['visualStatus']='rejected-replaced';d['visualNotes']=[reason]
 d['prompt']=str(ROOT/'prompts/cast/E'/f'{f}.attempt-01.txt')
 d['submittedParameters']['promptFile']=d['prompt'];d['evidence']['receipt']=str(R/f'{f}.attempt-01.receipt.json')
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
report={'action':'cast','direction':'E','status':'16 frames generated; technical checks passed; static review recorded; continuous playback pending parent','count':16,'durationMs':45,'totalMs':720,'uniqueFileHashes':len(hashes),'fixedExport':'native complete square uniformly resized to820x820, placed(102,102) on1024x1024 RGBA; no per-frame alignment','tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'nativeSize':[1254,1254],'client':'not read, not integrated, not tested','generatedImageCallsWithImage':20,'failedCalls':1,'frames':rows}
(Q/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(1280,1360),(235,237,234));draw=ImageDraw.Draw(sheet)
for i,row in enumerate(rows):
 im=Image.open(row['file']).convert('RGBA').resize((320,320),Image.Resampling.LANCZOS)
 x=(i%4)*320;y=(i//4)*340
 sheet.paste(im,(x,y),im);draw.text((x+10,y+320),f"E cast {i+1:02d} / 45ms",fill=(30,45,40))
sheet.save(Q/'contact-sheet.png')
print(json.dumps({'frames':16,'uniqueSHA':len(hashes),'allNativeOpaqueBorderCountsZero':all(all(v==0 for v in r['nativeOpaqueBorderCountsTBLR']) for r in rows),'validation':str(Q/'validation.json'),'contact':str(Q/'contact-sheet.png')}))

