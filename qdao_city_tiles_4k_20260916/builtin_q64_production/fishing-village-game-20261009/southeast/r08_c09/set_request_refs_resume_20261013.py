from pathlib import Path
import json,hashlib,sys
T=Path(__file__).resolve().parent
pid,v,rel,prompt=sys.argv[1:5];stem=f'{pid}-{v}'
assert not (T/f'{stem}.tool-response.json').exists(),'Already submitted'
p=T/f'{stem}.request.json';d=json.loads(p.read_text())
refs=[d['referenced_image_paths'][0]]+([] if rel=='-' else [str(T/rel)])
d.update(prompt=prompt,referenced_image_paths=refs,referenceRoles={'1':'Exact coordinate target with actual core115 halo; sole layout authority','2':'Selected native material and detail only, not position authority'},referenceEvidence=[dict(path=s,sha256=hashlib.sha256(Path(s).read_bytes()).hexdigest()) for s in refs])
p.write_text(json.dumps(d,indent=2),encoding='utf-8');(T/f'{stem}.prompt.txt').write_text(prompt,encoding='utf-8')
print(json.dumps(dict(request=str(p),refs=refs,promptSha256=hashlib.sha256(prompt.encode()).hexdigest())))

