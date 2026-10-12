"""Apply one fixed canvas transform to every native frame; no new poses."""
from pathlib import Path
from PIL import Image
import hashlib, json
from datetime import datetime,timezone

root=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
count=0
for native in sorted((root/'.work').glob('*/*/*.png')):
    action,direction=native.parts[-3:-1]; number=native.stem
    if action not in ('hit','attack','cast') or direction not in ('E','W') or not number.isdigit(): continue
    record=root/f'records/{action}/{direction}/{number}.generation.json'
    if not record.exists(): continue
    output=root/f'runtime/{action}/{direction}/{number}.png'
    deriv=output.with_suffix('.png.generation.json')
    source_sha=sha(native)
    if output.exists() and deriv.exists() and json.loads(deriv.read_text(encoding='utf-8')).get('derivedFrom',{}).get('sha256')==source_sha: continue
    meta=json.loads(record.read_text(encoding='utf-8-sig'))
    with Image.open(native) as raw:
        if raw.size!=(1254,1254): raise ValueError(f'Unexpected native size; must review shared transform: {native}: {raw.size}')
        im=raw.convert('RGBA').resize((896,896),Image.Resampling.LANCZOS)
        canvas=Image.new('RGBA',(1024,1024),(0,0,0,0))
        canvas.alpha_composite(im,(64,69))
        output.parent.mkdir(parents=True,exist_ok=True)
        canvas.save(output)
    derivative={'file':output.relative_to(root).as_posix(),'sha256':sha(output),'exportedAt':datetime.now(timezone.utc).isoformat(),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','derivedFrom':{'file':native.relative_to(root).as_posix(),'sha256':source_sha,'generationRecord':record.relative_to(root).as_posix()},'operation':{'type':'uniform full-canvas downsample and transparent pad','nativeSize':[1254,1254],'scaledCanvasSize':[896,896],'scale':896/1254,'offset':[64,69],'resampler':'Pillow LANCZOS','sameForAllFrames':True,'perFrameAlignment':False,'mirrored':False},'configSnapshot':meta.get('configSnapshot'),'actualModel':meta.get('actualModel'),'actualQuality':meta.get('actualQuality'),'unverifiedReason':meta.get('unverifiedReason'),'prompt':meta.get('prompt'),'evidence':meta.get('evidence'),'references':meta.get('references')}
    deriv.write_text(json.dumps(derivative,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    count+=1
print(f'Exported {count} frames with shared transform.')
