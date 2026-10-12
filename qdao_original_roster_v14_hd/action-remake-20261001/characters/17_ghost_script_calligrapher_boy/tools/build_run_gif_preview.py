"""Legacy script name; exact60ms animated WebP preview only: preserves full-canvas framing; never edits source sprites."""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parents[1]
if (BASE/'manifest.json').exists():
    manifest = json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
    directions = [d for d in ['N','NE','E','SE','S','SW','W','NW'] if any(s['action']=='run' and s['direction']==d for s in manifest['sequences'])]
    sequences = {d:[{'key':f"run-{d}-{f['frame']:02d}",'path':'../'+f['file'],'sha256':f['sha256']} for f in next(s for s in manifest['sequences'] if s['action']=='run' and s['direction']==d)['frames']] for d in directions}
else:
    manifest = json.loads((BASE/'preview/manifest-preview.json').read_text(encoding='utf-8'))
    directions = [d for d in ['N','NE','E','SE','S','SW','W','NW'] if all(s['selected'] for s in manifest['slots'] if s['action']=='run' and s['direction']==d)]
    sequences = {d: [s['selected'] for s in manifest['slots'] if s['action']=='run' and s['direction']==d] for d in directions}
assert all(len(v)==16 and all(v) for v in sequences.values())
frames=[]
for n in range(16):
    canvas=Image.new('RGB',(960,288*((len(directions)+3)//4)),'#d5d9d2')
    draw=ImageDraw.Draw(canvas)
    for k,d in enumerate(directions):
        item=sequences[d][n]
        source=BASE/'preview'/item['path']
        assert hashlib.sha256(source.read_bytes()).hexdigest()==item['sha256']
        with Image.open(source) as im:
            tile=im.convert('RGBA').resize((240,240),Image.Resampling.LANCZOS)
            canvas.paste(tile,((k%4)*240,(k//4)*288+25),tile)
        draw.text(((k%4)*240+10,(k//4)*288+8),d+' - 960ms /60ms uniform',fill='#23382b')
        draw.text(((k%4)*240+10,(k//4)*288+270),item['key'],fill='#23382b')
    frames.append(canvas)
out=BASE/'preview/run-current-960ms.webp'
frames[0].save(out,save_all=True,append_images=frames[1:],duration=60,loop=0,lossless=True)
with Image.open(out) as im:
    assert im.n_frames==16
blob=out.read_bytes();pos=12;durations=[]
while pos+8<=len(blob):
    tag=blob[pos:pos+4];size=int.from_bytes(blob[pos+4:pos+8],'little');payload=pos+8
    if tag==b'ANMF': durations.append(int.from_bytes(blob[payload+12:payload+15],'little'))
    pos=payload+size+(size%2)
assert durations==[60]*16 and sum(durations)==960
record={'file':out.name,'previewOnly':True,'userRequestedPreviewTiming':True,'clientTimingConfirmed':False,'cycleMs':960,'frameDurationsMs':durations,'fullCanvasDisplayPx':240,'pixelChangesToSourceSprites':False,'format':'lossless animated WebP with exact60ms frame duration','sources':sequences}
(BASE/'preview/run-current-960ms.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'frames':len(durations),'cycleMs':sum(durations),'previewOnly':True}))
