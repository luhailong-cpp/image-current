"""Package existing real frames into playback media. No pose synthesis/interpolation."""
import json, hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent
O=R/'preview';O.mkdir(exist_ok=True)
index=[]
for action,n,ms in [('hit',6,40),('attack',12,30),('cast',16,45)]:
 for d in ['E','W']:
  paths=[R/f'runtime/{action}/{d}/{i:02}.png' for i in range(1,n+1)]
  frames=[Image.open(p).convert('RGBA') for p in paths]
  for label,mult in [('normal',1),('slow',4)]:
   name=f'{action}-{d}-{label}.webp';out=O/name
   # Preview-only uniform resolution reduction. Formal source PNGs are untouched.
   small=[im.resize((512,512),Image.Resampling.LANCZOS) for im in frames]
   small[0].save(out,save_all=True,append_images=small[1:],duration=ms*mult,loop=0,lossless=True,method=4)
   check=Image.open(out)
   durations=[]
   for i in range(check.n_frames):
    check.seek(i);check.load();durations.append(check.info.get('duration'))
   if check.n_frames!=n or durations!=[ms*mult]*n:raise ValueError((name,check.n_frames,durations))
   index.append({'file':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'frameCount':n,'durationMs':ms*mult,'totalMs':n*ms*mult,'speed':1/mult,'dimensions':[512,512],'operation':'ordered existing frames, whole-canvas preview resize only; no new poses or interpolation','sourceFiles':[p.relative_to(R).as_posix() for p in paths],'sourceSha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]})
   check.close()
  for im in frames:im.close()
(O/'media-manifest.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'media':len(index),'verifiedFramesAndTiming':True}))
