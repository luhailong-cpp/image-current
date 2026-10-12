from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[{'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted((ROOT/'runtime').rglob('*.png'))]
assert len(rows)==196
expected={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines() if line}
assert len(expected)==196 and all(expected[r['file']]==r['sha256'] for r in rows)
canonical=''.join(r['sha256']+'  '+r['file']+'\n' for r in rows)
record={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'feedbackType':'relayed_user_feedback','verbatimFeedback':'弓足少女对了','resolvedCharacter':'09_bamboo_archer_girl / 竹弓少女','sourceThreadId':'01a0f76f-0056-7c23-a688-10733b6b89e3','sourceContext':'统筹聊天转达用户认可当前竹弓少女版本，要求保留正确动作、仅做必要交付整理和验证。','scope':'Current visible version accepted; the exact viewed directions/frames were not specified. Do not turn this feedback into blanket per-frame, whole-sequence or game-client acceptance.','decision':'Preserve these exact 196 current images; no further redraw from earlier generic foot-direction broadcasts.','imageSetSha256':hashlib.sha256(canonical.encode()).hexdigest(),'runtimeImageCount':196,'runDefaultCycleMs':720,'runDefaultFrameMs':45,'imageChangesDuringThisContinuation':0,'dynamicVisualApproval':False,'clientRuntimeApproval':False,'frames':rows}
(ROOT/'accepted-version.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
status=json.loads((ROOT/'status.json').read_text(encoding='utf-8-sig'))
status['userFeedback']={'record':'accepted-version.json','verbatimFeedback':record['verbatimFeedback'],'imageSetSha256':record['imageSetSha256'],'currentImagesMatch':True,'scope':record['scope']}
status['deliveryState']='current_user_accepted_version_preserved'
(ROOT/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
manifestPath=ROOT/'manifest.json';manifest=json.loads(manifestPath.read_text(encoding='utf-8-sig'))
manifest['userFeedback']=status['userFeedback'];manifest['deliveryState']=status['deliveryState']
manifestPath.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
dataPath=ROOT/'preview/data.js';raw=dataPath.read_text(encoding='utf-8-sig')
data=json.loads(raw.removeprefix('window.BAMBOO_PREVIEW = ').strip().removesuffix(';'))
data['userFeedback']=status['userFeedback'];data['deliveryState']=status['deliveryState']
dataPath.write_text('window.BAMBOO_PREVIEW = '+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
print(json.dumps({'frozenImages':len(rows),'imageSetSha256':record['imageSetSha256'],'imageChanges':0}))
