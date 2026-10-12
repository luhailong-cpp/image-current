import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime
Z=Path(__file__).resolve().parents[1];N=Z/'native';Q=Z/'qa';stem='r08_c05_repair_j_stairjoint_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=Q/'repair-r08_c05-internal-v2-context-native.png';source=Q/(stem+'-source-1254.png')
r={'stem':stem,'tile':'r08_c05','tool':'image_gen__imagegen','route':'builtin','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prompt':(N/(stem+'.prompt.txt')).as_posix(),'coordinates':{'tileContextBox':[485,535,1739,1789],'contextBox':[600,650,1854,1904],'sourceContext':{'path':base.as_posix(),'sha256':sha(base)}},'submittedParameters':{'transparent_background':False,'referenced_image_paths':[source.as_posix()],'model':None,'quality':None},'actualModel':None,'actualQuality':None}
p=N/(stem+'.request.json');assert not p.exists();p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
