"""Preview-only animation packaging of final frames. No generated or interpolated poses."""
from pathlib import Path
from PIL import Image
import hashlib,json
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'previews'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
OUT.mkdir(exist_ok=True)
records=[]
for action,n,ms in [('hit',6,40),('attack',12,30),('cast',16,45)]:
    for direction in ['E','W']:
        sources=[BASE/'runtime'/action/direction/f'{i:02d}.png' for i in range(1,n+1)]
        frames=[Image.open(p).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS) for p in sources]
        for label,multiple in [('normal',1),('slow',4)]:
            p=OUT/f'{action}-{direction}.{label}.png'
            frames[0].save(p,save_all=True,append_images=frames[1:],duration=ms*multiple,loop=0,disposal=0,blend=0,optimize=False)
            with Image.open(p) as im:
                assert im.n_frames==n
                assert all((im.seek(i) is None and im.info['duration']==ms*multiple) for i in range(n))
            records.append({'file':p.relative_to(BASE).as_posix(),'sha256':sha(p),'format':'APNG','size':[512,512],'frames':n,'durationMs':ms*multiple,'speed':1/multiple,'sources':[{'file':s.relative_to(BASE).as_posix(),'sha256':sha(s)} for s in sources],'operation':'uniform preview scale and APNG packaging; no synthesized pose, no interpolated frames'})
(OUT/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print('Built and verified',len(records),'independent APNG previews')
