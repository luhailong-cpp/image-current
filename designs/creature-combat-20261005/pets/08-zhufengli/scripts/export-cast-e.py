from pathlib import Path
from PIL import Image
import json, hashlib, sys
base=Path(__file__).resolve().parents[1]
n=int(sys.argv[1])
stem=f'cast-E-{n:02d}'
recpath=base/'receipts'/f'{stem}.json'
r=json.loads(recpath.read_text(encoding='utf-8'))
src=Path(r['nativeSourcePath'])
dest=base/'runtime'/'cast'/'E'/f'{n:02d}.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(src).convert('RGBA')
native_size=list(im.size)
out=im.resize((1024,1024),Image.Resampling.LANCZOS) if im.size!=(1024,1024) else im.copy()
out.save(dest)
a=out.getchannel('A')
r.update({'nativeSize':native_size,'nativeSHA256':sha(src),'outputPath':str(dest),'outputSize':[1024,1024],'outputMode':out.mode,'outputSHA256':sha(dest),'alphaExtrema':list(a.getextrema()),'alphaBBox':a.getbbox(),'referenceSHA256':{ref['path']:sha(Path(ref['path'])) for ref in r['references']},'operation':'whole-canvas RGBA resize to 1024x1024 using Lanczos; no crop, translation, per-frame foot alignment, synthesis, or interpolation between frames'})
r.update({'file':f'runtime/cast/E/{n:02d}.png','sha256':sha(dest),'generatedAt':r['receivedAt'],'prompt':f'prompts/{stem}.txt','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))})
if isinstance(r.get('evidence'),str):
    r['evidenceStatement']=r['evidence']
r['evidence']={'receipt':f'receipts/{stem}.json','request':f'receipts/{stem}.request.json','statement':r.get('evidenceStatement','Host-managed imagegen; model and quality undisclosed')}
recpath.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
(dest.with_suffix('.generation.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frame':n,'size':out.size,'alphaExtrema':a.getextrema(),'bbox':a.getbbox(),'sha256':sha(dest)}))
