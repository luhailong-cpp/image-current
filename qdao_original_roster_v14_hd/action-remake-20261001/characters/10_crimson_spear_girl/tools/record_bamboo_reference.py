from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
ref=R.parent/'09_bamboo_archer_girl'
m=json.loads((ref/'manifest.json').read_text(encoding='utf-8-sig'))
rows=[{'label':s['label'],'frames':[{'slot':f['slot'],'file':f['file'],'sha256':f['sha256']} for f in s['frames']]} for s in m['sequences']]
rec={'source':'Latest user-authorized reference relayed by coordinating chat: 用户已确认竹弓少女对了，并要求其他窗口参照她','referenceDirectory':str(ref),'manifestSha256':hashlib.sha256((ref/'manifest.json').read_bytes()).hexdigest(),'timing':json.loads((ref/'animation-timing.json').read_text(encoding='utf-8-sig')),'referenceFrames':rows,'use':'Read-only same-direction gait/foot axis/weight/hand motion comparison. Preserve Crimson Spear Girl identity, spear and grip. No copying pixels or cross-direction frame indexing.','acceptanceScope':'Reference confirmed by user; does not automatically validate this character or game client.'}
(R/'BAMBOO_REFERENCE_20261003.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

