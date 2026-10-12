from pathlib import Path
import json, hashlib
B=Path(__file__).resolve().parent
old=B/'receipts/p03_04.resume20261012-v01.receipt.json'
new=B/'receipts/p03_04.resume20261012-v01.actual-times.receipt.json'
r=json.loads(old.read_text(encoding='utf-8'))
assert not new.exists()
r.update(startedAtUtc='2026-10-12T12:22:17Z', returnedAtUtc='2026-10-12T12:23:01Z')
r['correction']={'supersedes':str(old),'supersededSha256':hashlib.sha256(old.read_bytes()).hexdigest(),'reason':'Previous recorder used an incorrectly transcribed pair of clock times; these are the actual clock tool values stored immediately around the successful builtin call.'}
new.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(new)
