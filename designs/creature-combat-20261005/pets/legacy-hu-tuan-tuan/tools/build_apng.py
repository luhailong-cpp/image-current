"""Lossless alpha-preserving playback previews from independent final PNGs."""
import json, hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
for a,n,d in [('hit',6,40),('attack',12,30),('cast',16,45)]:
    for direction in ('E','W'):
        files=[R/'runtime'/a/direction/f'{i:02}.png' for i in range(1,n+1)]
        assert all(p.exists() for p in files), f'Missing {a}/{direction}; cannot make a complete playback preview'
        frames=[Image.open(p).convert('RGBA') for p in files]
        for suffix,factor in [('normal',1),('slow',4)]:
            out=R/'preview'/f'{a}-{direction}-{suffix}.png'
            frames[0].save(out,save_all=True,append_images=frames[1:],duration=d*factor,loop=0,disposal=1,blend=0,format='PNG')
            record={'file':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'operation':{'type':'APNG playback packaging','frameDurationMs':d*factor,'frameCount':n,'pixelInterpolation':False,'canvasTransform':None},'derivedFrom':[{'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generationRecord':p.with_suffix('.png.generation.json').relative_to(R).as_posix()} for p in files]}
            out.with_suffix('.png.derivation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('Wrote six exact-time normal and six 0.25x APNG previews.')
