import json
from pathlib import Path
r=Path(__file__).resolve().parent
old='r09_c06_p04_03_v1'; stem='r09_c06_p04_03_v2'
j=json.loads((r/'native'/(old+'.request.json')).read_text(encoding='utf-8-sig'))
j['stem']=stem
j['references']=[{'path':(r/'native'/(old+'.png')).as_posix(),'role':'precise edit target; remove added metal shoe and keep bare wooden leg'},*json.loads((r/'references.json').read_text(encoding='utf-8'))]
(r/'native'/(stem+'.request.json')).write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

