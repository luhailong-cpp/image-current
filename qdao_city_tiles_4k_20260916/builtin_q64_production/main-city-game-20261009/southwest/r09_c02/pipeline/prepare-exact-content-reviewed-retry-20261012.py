from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
T = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
old = T / 'pipeline/prompts/p03_02.resume20261012-v01.request.json'
r = json.loads(old.read_text(encoding='utf-8-sig'))
assert r['tile'] == 'r09_c02' and r['coordinates']['id'] == 'p03_02'
assert not (T/'native/p03_02.png').exists()
for ref in r['references'] + r.get('neighborSources', []):
    assert sha(ref['file']) == ref['sha256']
attempt = 'resume20261012-reviewed-retry-v02'
pp = T / 'pipeline/prompts' / f'p03_02.{attempt}.prompt.txt'
rp = T / 'pipeline/prompts' / f'p03_02.{attempt}.request.json'
assert not pp.exists() and not rp.exists()
pp.write_text(r['prompt'], encoding='utf-8')
assert sha(pp) == r['promptSha256']
r['promptFile'] = str(pp)
r['preparedAtUtc'] = datetime.now(timezone.utc).isoformat()
r['sourceRejectedRequest'] = {'file':str(old),'sha256':sha(old)}
r['sourceRejectedReceipt'] = str(T/'pipeline/receipts/p03_02.resume20261012-v01.rejected-receipt.json')
r['reviewedRetryEvidence'] = {'reviewer':'root','review':'Root independently inspected exact original prompt and actual target and found ordinary game smith-tool relief on gold plaque, no persons, harm or violent scene; one unchanged-content attempt authorized.','exactPromptUnchanged':True,'exactReferencePathsAndHashesUnchanged':True,'bypassAttempted':False,'onRepeatedRejection':'Preserve missing slot and report; no evasive rewording or alternate route.'}
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(rp)
