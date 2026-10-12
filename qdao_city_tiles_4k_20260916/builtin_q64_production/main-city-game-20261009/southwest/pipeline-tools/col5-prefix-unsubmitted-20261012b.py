from pathlib import Path
import sys, json, hashlib, shutil
request = Path(sys.argv[1]); prefix = sys.argv[2]
assert '/southwest/r' in request.as_posix() and '_c05/' in request.as_posix()
r = json.loads(request.read_text(encoding='utf-8-sig'))
receipt = request.parent.parent / 'receipts' / request.name.replace('.request.json','.receipt.json')
assert not receipt.exists()
prompt = Path(r['promptFile'])
for p in (request,prompt):
    target = p.with_name(p.name + '.unsubmitted-before-native-coordinates')
    assert not target.exists(); shutil.copy2(p,target)
body = r['prompt'][r['prompt'].index('Use case:'):]
r['prompt'] = prefix + '\n\n' + body
prompt.write_text(r['prompt'], encoding='utf-8')
r['promptSha256'] = hashlib.sha256(prompt.read_bytes()).hexdigest()
r['unsubmittedPrefixCorrectedAfterSeedView'] = True
request.write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(request)
