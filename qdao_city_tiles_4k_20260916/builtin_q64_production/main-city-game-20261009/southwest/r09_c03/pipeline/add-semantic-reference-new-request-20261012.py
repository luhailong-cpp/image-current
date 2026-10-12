from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib
T = Path(__file__).resolve().parents[1]
patch, base_attempt, attempt, ref_name = sys.argv[1:]
rp = T / 'pipeline/prompts' / f'{patch}.{base_attempt}.request.json'
r = json.loads(rp.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert r['tile'] == T.name and len(r['references']) == 4
pp = T / 'pipeline/prompts' / f'{patch}.{attempt}.prompt.txt'
new_rp = T / 'pipeline/prompts' / f'{patch}.{attempt}.request.json'
assert not pp.exists() and not new_rp.exists()
ref = Path(ref_name)
assert ref.is_file()
pp.write_text(r['prompt'], encoding='utf-8')
r['promptFile'] = str(pp)
r['promptSha256'] = sha(pp)
r['references'].append({'file':str(ref),'sha256':sha(ref),'role':'supporting mechanically enlarged approved semantic layout only; never final art'})
r['referenced_image_paths'] = [q['file'] for q in r['references']]
r['preparedAtUtc'] = datetime.now(timezone.utc).isoformat()
r['sourcePreparedRequest'] = {'file':str(rp),'sha256':sha(rp)}
new_rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(new_rp)
