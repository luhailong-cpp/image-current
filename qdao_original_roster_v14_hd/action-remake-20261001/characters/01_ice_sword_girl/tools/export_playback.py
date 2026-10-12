"""Export only an offline playback preview. Source sprite pixels are untouched."""
from pathlib import Path
import hashlib,json
from PIL import Image,features
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'review/run-E-selection.json').read_text(encoding='utf-8'))
frames=[]
for f in s['frames']:
    p=R/f['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
    frames.append(Image.open(p).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS))
out=R/'preview/run-E-1x-1200ms.webp'
frames[0].save(out,format='WEBP',save_all=True,append_images=frames[1:],duration=s['timing']['frameDurationsMs'],loop=0,lossless=True,method=6)
im=Image.open(out)
assert im.n_frames==16
assert im.size==(256,256)
durs=[]
for i in range(im.n_frames):
    im.seek(i);im.load();durs.append(im.info.get('duration'))
assert durs==s['timing']['frameDurationsMs'],durs
report={'kind':'offline_playback_preview_not_game_sprite','file':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'canvasSize':[256,256],'frames':16,'durationsMs':durs,'totalMs':sum(durs),'playbackRate':1,'loop':0,'selectionSha256':hashlib.sha256((R/'review/run-E-selection.json').read_bytes()).hexdigest(),'operation':'whole square source canvas downscaled uniformly for preview only; no crop, translation, interpolation or duplicate pose','clientRuntimeVerified':False}
(R/'preview/run-E-1x-1200ms.webp.preview.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))

