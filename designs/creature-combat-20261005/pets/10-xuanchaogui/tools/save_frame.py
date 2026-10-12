"""Persist a real built-in generated frame; whole-canvas export only, no pose synthesis."""
import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

ap = argparse.ArgumentParser()
ap.add_argument('--receipt', required=True)
a = ap.parse_args()
rp = Path(a.receipt).resolve()
receipt = json.loads(rp.read_text(encoding='utf-8-sig'))
action, direction, number = receipt['action'], receipt['direction'], int(receipt['frame'])
assert action in ('hit','attack','cast') and direction in ('E','W')
native = Path(receipt['nativePath'])
dest = ROOT / 'runtime' / action / direction / f'{number:02d}.png'
dest.parent.mkdir(parents=True, exist_ok=True)
with Image.open(native) as im:
    original_size, mode, fmt = im.size, im.mode, im.format
    assert im.width == im.height, 'non-square native requires an explicit direction-wide transform'
    assert 'A' in im.getbands(), 'native must supply real alpha'
    rgba = im.convert('RGBA')
    assert rgba.getchannel('A').getextrema()[0] == 0, 'no transparent background'
    # All frames receive the same whole-square 1024 export, never content-aware alignment.
    out = rgba.resize((1024,1024), Image.Resampling.LANCZOS) if rgba.size != (1024,1024) else rgba
    out.save(dest)
    bbox = out.getchannel('A').getbbox()
config = json.loads((ROOT.parents[3] / 'config' / 'image-generation.json').read_text(encoding='utf-8-sig'))
source_record = ROOT / 'provenance' / action / direction / f'{number:02d}.generation.json'
refs = []
for i,p in enumerate(receipt['referenced_image_paths']):
    roles = ['identity E front-three-quarter', 'identity W rear-three-quarter', 'primary painting/material style']
    refs.append({'path':p, 'sha256':sha(p), 'role':roles[i] if i < 3 else 'animation continuity / fixed composition'})
prompt_rel = receipt.get('promptPath', f'prompts/{action}/{direction}/{number:02d}.txt')
data = dict(file=str(native), sha256=sha(native), generatedAt=receipt['completedAt'], startedAt=receipt['startedAt'],
            width=original_size[0], height=original_size[1], format=fmt, mode=mode,
            tool='image_gen.imagegen', route='builtin', configSnapshot=config,
            submittedParameters={'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':receipt['referenced_image_paths'],'prompt':prompt_rel},
            actualModel=None, actualQuality=None,
            evidence={'receipt':str(rp.relative_to(ROOT)).replace('\\','/'), 'returnedFields':['image_url','output_hint'], 'output_hint':receipt.get('output_hint')},
            unverifiedReason='宿主管理，工具无 model/quality 选择器，返回未披露实际模型和质量。配置目标与提示不作为实际返回证据。',
            prompt=prompt_rel, references=refs, nativeRetention='host-managed generation output; no duplicate raw image saved in delivery directory')
write(source_record,data)
sidecar = dict(file=str(dest.relative_to(ROOT)).replace('\\','/'),sha256=sha(dest),width=1024,height=1024,format='PNG',mode='RGBA',
               generatedAt=receipt['completedAt'],derivedFrom={'path':str(native),'sha256':data['sha256'],'generationRecord':str(source_record.relative_to(ROOT)).replace('\\','/')},
               operation={'type':'whole-canvas-uniform-resize','sourceSize':list(original_size),'targetSize':[1024,1024],'resampling':'Lanczos','translation':[0,0],'contentAwareAlignment':False},
               configSnapshot=config, actualModel=None, actualQuality=None, submittedParameters=data['submittedParameters'],
               unverifiedReason=data['unverifiedReason'],prompt=prompt_rel,references=refs,evidence=data['evidence'],
               alphaBBox=list(bbox),visualStatus='individual-frame-reviewed; sequence review pending',
               pivot=[0.5,0.08],anchorTopLeft=[512,942],durationMs={'hit':40,'attack':30,'cast':45}[action])
write(Path(str(dest)+'.generation.json'),sidecar)
print(json.dumps({'file':str(dest),'nativeSize':original_size,'size':[1024,1024],'sha256':sidecar['sha256'],'alphaBBox':bbox}))
