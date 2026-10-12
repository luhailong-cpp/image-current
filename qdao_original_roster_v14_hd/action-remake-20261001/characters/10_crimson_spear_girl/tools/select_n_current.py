from pathlib import Path
import json
r=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl')
p=r/'source-selection.json';j=json.loads(p.read_text(encoding='utf-8-sig'))
for i in range(1,17): j['slots'][f'run/N/{i:02}']=f'generation/run-N-{i:02}/native.png'
j['slots']['run/N/06']='generation/run-N-06-v2/native.png'
j['slots']['run/N/07']='generation/run-N-07-v2/native.png'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'candidate/registration.json';j=json.loads(p.read_text(encoding='utf-8-sig'))
j['directions']['N']={'translation':[73,134],'basis':'Back view common pelvis x640, virtual ground1178. Integer fixed direction placement; compression and travel-perspective changes remain, no per-frame foot alignment.'}
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('N selected16 and provisional fixed root registered')

