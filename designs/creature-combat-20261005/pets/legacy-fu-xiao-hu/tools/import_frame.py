"""Export an independently AI-drawn image; never synthesizes animation poses."""
import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

p=argparse.ArgumentParser()
p.add_argument('--input', required=True)
p.add_argument('--output', required=True)
p.add_argument('--receipt', required=True)
p.add_argument('--prompt', required=True)
a=p.parse_args()
src=Path(a.input); dst=ROOT/a.output; rec=ROOT/a.receipt
receipt=json.loads(rec.read_text(encoding='utf-8'))
im=Image.open(src); im.load()
if im.mode!='RGBA' or im.getchannel('A').getextrema()[0]!=0:
    raise ValueError('Expected genuine transparent RGBA from image_gen')
native_sha=digest(src)
native={
    'file':str(src),'sha256':native_sha,'generatedAt':receipt['startedAt'],
    'width':im.width,'height':im.height,'format':'PNG','mode':im.mode,
    'tool':'image_gen.imagegen','route':'builtin',
    'configSnapshot':json.loads((ROOT.parents[3]/'config/image-generation.json').read_text(encoding='utf-8')),
    'submittedParameters':{'model':None,'quality':None,'transparent_background':True},
    'actualModel':None,'actualQuality':None,
    'unverifiedReason':'宿主管理，工具未披露型号/质量；没有model/quality选择器。',
    'evidence':{'toolReceipt':a.receipt,'outputHint':receipt.get('output_hint')},
    'prompt':a.prompt,'references':receipt['references']
}
native_rec=ROOT/(a.output+'.native.generation.json')
save_json(native_rec,native)
dst.parent.mkdir(parents=True,exist_ok=True)
im.resize((1024,1024),Image.Resampling.LANCZOS).save(dst)
save_json(ROOT/(a.output+'.generation.json'),{
    'file':a.output,'sha256':digest(dst),'exportedAt':datetime.now(timezone.utc).isoformat(),
    'width':1024,'height':1024,'format':'PNG','mode':'RGBA',
    'derivedFrom':{'file':str(src),'sha256':native_sha,'generationRecord':str(native_rec.relative_to(ROOT))},
    'operation':{'type':'whole-canvas-resize','sourceSize':list(im.size),'outputSize':[1024,1024],'resampling':'LANCZOS','perFrameAlignment':False},
    'actualModel':None,'actualQuality':None,'visualStatus':'pending-sequence-review'
})
print(json.dumps({'file':str(dst),'nativeSize':im.size,'sha256':digest(dst),'bbox':Image.open(dst).getbbox()}))
