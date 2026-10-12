from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
records=[];errors=[];refs=0;derived=0;guides=0
for p in sorted((T/'native').glob('*.png')):
 try:
  d=read(str(p)+'.generation.json');h=sha(p);src=Path(d['sourceOutputPath']);req=read(d['request']);receipt=read(d['evidence'])
  assert h==d['sha256']==sha(src)
  assert Image.open(p).size==(1254,1254)
  assert Path(d['prompt']).read_text(encoding='utf-8').strip()==req['prompt'].strip()
  assert receipt['sourceOutputPath'].replace('\\','/')==str(src).replace('\\','/')
  assert d['actualModel'] is None and d['actualQuality'] is None
  assert len(d['references'])>=4 and len(req['referenced_image_paths'])==len(d['references'])
  for r in d['references']:
   assert sha(r['file'])==r['sha256'];refs+=1
  assert [str(Path(r['file'])) for r in d['references']]==[str(Path(x)) for x in req['referenced_image_paths']]
  records.append({'native':str(p),'sha256':h,'nativeSize':[1254,1254],'sourceByteIdentity':True,'referenceHashCheck':True})
 except Exception as e:errors.append({'file':str(p),'error':str(e)})
for p in sorted((T/'layout-only').glob('*-mixed-context.png.generation.json')):
 try:
  d=read(p);assert sha(d['file'])==d['sha256'];items=d['derivedFrom'];im=Image.open(items[0]['file']).convert('RGB')
  for r in items:
   assert sha(r['file'])==r['sha256'];derived+=1
   if 'crop' in r:im.paste(Image.open(r['file']).convert('RGB').crop(tuple(r['crop'])),tuple(r['paste']))
  assert im.tobytes()==Image.open(d['file']).convert('RGB').tobytes();guides+=1
 except Exception as e:errors.append({'file':str(p),'error':str(e)})
result={'tile':T.name,'nativeCount':len(records),'directReferencesVerified':refs,'derivedSourcesVerified':derived,'mixedGuidesReplayed':guides,'nativeRecords':records,'errors':errors,'actualModel':None,'actualQuality':None,'sourceArtResized':False,'status':'pass' if not errors else 'fail'}
(T/'qa'/'source-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='nativeRecords'}))
if errors:raise SystemExit(1)
