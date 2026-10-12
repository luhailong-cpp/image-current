from pathlib import Path
import json
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[1]
d=json.loads((b/'audit/cast-selection.json').read_text(encoding='utf-8'))
for f in d['frames']:
 if f['frame']==1:continue
 di=f['direction'];key=f"cast-{di}-{f['frame']:02d}-foot-v1"
 ref=json.loads((b/'provenance/requests'/f"cast-{di}-01-foot-v1.json").read_text(encoding='utf-8'))
 ref['key']=key;ref['startedAt']=datetime.now(timezone.utc).isoformat();ref['originalSelectedSource']=f['source'];ref['originalSelectedSHA']=f['sha256']
 ref['submittedParameters']['referenced_image_paths'][0]=(b/f['source']).as_posix()
 (b/'provenance/requests'/f'{key}.json').write_text(json.dumps(ref,ensure_ascii=False,indent=2),encoding='utf-8')
 (b/'provenance/prompts'/f'{key}.txt').write_text(ref['submittedParameters']['prompt'],encoding='utf-8')
print('30 requests with individual original source refs prepared')

