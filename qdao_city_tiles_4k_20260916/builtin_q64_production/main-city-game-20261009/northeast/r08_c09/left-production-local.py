from pathlib import Path
import json,sys,hashlib,datetime,subprocess
from PIL import Image
T=Path(__file__).resolve().parent
Z=T.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
cmd=sys.argv[1]
if cmd=='select':
 name=sys.argv[2]; patch=name[:3]; f=T/'native'/f'{name}.png'; rec=json.loads(Path(str(f)+'.generation.json').read_text(encoding='utf8'))
 assert f.exists() and sha(f)==rec['sha256']
 sf=T/'selected-native.json'; s=json.loads(sf.read_text(encoding='utf-8-sig')) if sf.exists() else {}
 s[patch]=f.name;save(sf,s)
 sources=[]
 for p,n in sorted(s.items()):
  q=T/'native'/n
  if q.exists():
   a=json.loads(Path(str(q)+'.generation.json').read_text(encoding='utf8'))
   sources.append({'patch':p,'file':str(q),'sha256':a['sha256']})
 progress={'tile':T.name,'updatedAt':now(),'status':'native_production_in_progress','nativeCount':len(list((T/'native').glob('*.png'))),'selectedCoreCount':len(sources),'remainingCoreCount':16-len(sources),'nativeSources':sources,'completeCandidateCount':0,'internalPassed4kCount':0,'formalAcceptedCount':0,'inflightGeneration':None,'actualModel':None,'unsavedSuccessfulOutputs':0,'generationStopped':False}
 save(T/'tile-progress.json',progress)
 attempt=T/'receipts'/f'{name}.attempt.json'
 if attempt.exists():
  a=json.loads(attempt.read_text(encoding='utf-8-sig'));a.update(state='saved',savedAt=now(),native=str(f),sha256=rec['sha256']);save(attempt,a)
 print(json.dumps({k:progress[k] for k in ['tile','nativeCount','selectedCoreCount','remainingCoreCount']}))
elif cmd=='quick':
 patch=sys.argv[2]; s=json.loads((T/'selected-native.json').read_text(encoding='utf8')); f=T/'native'/(patch+'.png' if '-' in patch else s[patch])
 req=json.loads((T/'prompts'/f'{f.stem}.request.json').read_text(encoding='utf8'))
 ctx=Path(req['referenced_image_paths'][0]);a=Image.open(f).convert('RGB');b=Image.open(ctx).convert('RGB')
 out=T/'qa'/'quick-native';out.mkdir(exist_ok=True)
 for direction in sys.argv[3:]:
  path=out/f'{f.stem}-{direction}.png'
  if path.exists():print(str(path));continue
  if direction=='east':
   im=Image.new('RGB',(600,1024));im.paste(a.crop((839,115,1139,1139)),(0,0));im.paste(b.crop((1139,115,1254,1139)),(300,0));im=im.crop((0,0,415,1024))
  elif direction=='south':
   im=Image.new('RGB',(1024,415));im.paste(a.crop((115,839,1139,1139)),(0,0));im.paste(b.crop((115,1139,1139,1254)),(0,300))
  elif direction=='north':
   im=Image.new('RGB',(1024,415));im.paste(b.crop((115,0,1139,115)),(0,0));im.paste(a.crop((115,115,1139,415)),(0,115))
  else:raise ValueError(direction)
  im.save(path);save(Path(str(path)+'.json'),{'native':str(f),'nativeSha256':sha(f),'context':str(ctx),'contextSha256':sha(ctx),'direction':direction,'seamPixel':115 if direction=='north' else 300,'operation':'integer crops and paste; no resampling'})
  print(str(path))

