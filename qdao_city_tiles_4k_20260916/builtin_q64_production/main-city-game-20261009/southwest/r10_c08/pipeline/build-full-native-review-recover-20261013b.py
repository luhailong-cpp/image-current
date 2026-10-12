from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image, ImageDraw

T=Path(__file__).resolve().parents[1]
A=T/'pipeline/output/72f40489f8fbeac8/assembly.json'
q=json.loads(A.read_text(encoding='utf-8-sig'))
D=T/'pipeline/qa/72f40489f8fbeac8/recover-review-v01'
assert not D.exists()
D.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert q['verifiedNativeCount']==16
panels=[]
for rec in q['qa']:
    assert sha(rec['file'])==rec['sha256']
for axis in ('vertical','horizontal'):
 for seam in (1024,2048,3072):
  name=f'{axis}_{"x" if axis=="vertical" else "y"}{seam}_full.png'
  rec=next(r for r in q['qa'] if Path(r['file']).name==name)
  im=Image.open(rec['file']).convert('RGB')
  panel=Image.new('RGB',(4*258,1044) if axis=='vertical' else (1024,4*258),'white')
  draw=ImageDraw.Draw(panel); crops=[]
  for i in range(4):
   box=[0,i*1024,238,(i+1)*1024] if axis=='vertical' else [i*1024,0,(i+1)*1024,238]
   pos=(i*258,20) if axis=='vertical' else (0,i*258+20)
   panel.paste(im.crop(box),pos)
   draw.text((pos[0],pos[1]-18),f'{axis} {seam}, segment {i+1}',fill='black')
   crops.append({'sourceFile':rec['file'],'sourceSha256':rec['sha256'],'sourceBox':box,'pastePosition':list(pos),'resampling':False})
  f=D/f'{axis}-{seam}-segments.png';panel.save(f)
  panels.append({'file':str(f),'sha256':sha(f),'pixels':list(panel.size),'crops':crops,'actualViewed':False})
for y in (1024,2048,3072):
 panel=Image.new('RGB',(1536,532),'white');draw=ImageDraw.Draw(panel);crops=[]
 for i,x in enumerate((1024,2048,3072)):
  name=f'intersection_x{x}_y{y}.png'
  rec=next(r for r in q['qa'] if Path(r['file']).name==name)
  im=Image.open(rec['file']).convert('RGB');panel.paste(im,(i*512,20));draw.text((i*512,2),f'Intersection {x}, {y}',fill='black')
  crops.append({'sourceFile':rec['file'],'sourceSha256':rec['sha256'],'sourceBox':[0,0,512,512],'pastePosition':[i*512,20],'resampling':False})
 f=D/f'intersections-{y}.png';panel.save(f)
 panels.append({'file':str(f),'sha256':sha(f),'pixels':list(panel.size),'crops':crops,'actualViewed':False})
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r10_c08','assembly':{'file':str(A),'sha256':sha(A)},'core':q['output'],'context':q['contextOutput'],'panels':panels,'sourceResampling':False,'formalAccepted':False,'internalPassed':False}
(D/'panels.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'directory':str(D),'panelFiles':[r['file'] for r in panels],'core':q['output'],'context':q['contextOutput']},ensure_ascii=False))
