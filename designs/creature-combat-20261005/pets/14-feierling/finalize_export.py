"""One fixed, non-cropping export transform per direction, across all three actions."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(p):
 p=Path(p)
 return p if p.is_absolute() else ROOT/p
def native_path(r):
 n=r.get('native',{})
 candidates=[r.get('nativeSavedPath'),n.get('file'),n.get('path'),r.get('nativeFile'),r.get('nativePath')]
 for item in candidates:
  if item and resolve(item).is_file(): return resolve(item)
 raise FileNotFoundError(str(candidates))
TRANSFORMS={d:{'nativeCanvas':[1254,1254],'resizedCanvas':[853,853],'scale':853/1254,'offset':[0 if d=='E' else 50,126],'outputCanvas':[1024,1024],'footAnchorTopLeft':[512,942],'perFrameAlignment':False,'resampling':'LANCZOS','crop':False} for d in ['E','W']}
for d,t in TRANSFORMS.items():
 t['nominalNativeRoot']=[(512-t['offset'][0])/t['scale'],(942-t['offset'][1])/t['scale']]
 t['calibration']='Direction-wide nominal standing support root estimated from ready poses; feet may move around this root naturally. Entire native canvas retained. No per-frame adjustment.'
applied=[]
for action,count in [('hit',6),('attack',12),('cast',16)]:
 for direction in ['E','W']:
  t=TRANSFORMS[direction]
  for i in range(1,count+1):
   record=ROOT/'generation'/action/direction/f'{i:02}.generation.json'
   r=json.loads(record.read_text(encoding='utf-8-sig')); src=native_path(r)
   assert sha(src)==r['native']['sha256'],f'native hash mismatch: {src}'
   with Image.open(src) as im:
    assert im.mode=='RGBA' and im.size==(1254,1254),(src,im.mode,im.size)
    out=Image.new('RGBA',(1024,1024));out.paste(im.resize((853,853),Image.Resampling.LANCZOS),tuple(t['offset']))
    dest=ROOT/'runtime'/action/direction/f'{i:02}.png';out.save(dest)
    alpha=out.getchannel('A');hist=alpha.histogram()
   r.setdefault('preFinalExport',{'sha256':r.get('sha256') or r.get('exported',{}).get('sha256'),'operation':r.get('operation') or r.get('derivedFrom',{}).get('operation')})
   r.update(file=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),width=1024,height=1024,mode='RGBA',format='PNG',durationMs={'hit':40,'attack':30,'cast':45}[action],pivot=[0.5,0.08],footAnchorTopLeft=[512,942],action=action,direction=direction,frame=i)
   r['operation']={'type':'fixed-direction-export',**t}
   r['finalExportAt']=datetime.now(timezone.utc).isoformat()
   r['derivedFrom']={'sha256':sha(src),'nativeFile':str(src),'operation':r['operation']}
   r['alpha']={'extrema':alpha.getextrema(),'bbox':alpha.getbbox(),'transparentPixels':hist[0],'partialPixels':sum(hist[1:255]),'opaquePixels':hist[255]}
   if 'exported' in r:r['exported']={'file':r['file'],'sha256':r['sha256'],'width':1024,'height':1024,'mode':'RGBA','alphaMinMax':alpha.getextrema()}
   record.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
   applied.append({'file':r['file'],'sha256':r['sha256'],'sourceSHA256':sha(src)})
(ROOT/'EXPORT_TRANSFORMS.json').write_text(json.dumps({'directions':TRANSFORMS,'frameCount':len(applied),'applied':applied},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'exported':len(applied),'transforms':TRANSFORMS},ensure_ascii=False))
