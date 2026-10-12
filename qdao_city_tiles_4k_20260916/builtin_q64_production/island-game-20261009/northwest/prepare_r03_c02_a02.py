from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stem='r03_c02_s01_04_a02';o=json.loads((Z/'guides/r03_c02_s01_04_a01.input.json').read_text(encoding='utf-8'))
target=Z/'native/r03_c02_s01_04_a01.png'
inputs=[dict(path=target.as_posix(),sha256=sha(target),nativeSize=[1254,1254],role='edit target: remove invented upper curl and correct cropped sword-guard fragment without changing main roof or right neighbor')]+o['inputs'][1:]
r=dict(o);r.update(versionStem=stem,attempt='a02',inputs=inputs,imageGenReferencedImagePaths=[e['path'] for e in inputs],editTarget=dict(path=target.as_posix(),sha256=sha(target)),operation='builtin edit preserving native coordinates; macro layout correction')
for suffix,value in [('input',r),('references',dict(inputs=inputs))]:
 p=Z/'guides'/f'{stem}.{suffix}.json';assert not p.exists();p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
