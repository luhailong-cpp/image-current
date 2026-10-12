from pathlib import Path
import json
r=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl')
p=r/'review/run-phase-review.json';j=json.loads(p.read_text(encoding='utf-8'))
for d in ['SE','SW']:
 j['phases'][d][3]='support_exit_A'
 j['phases'][d][4]='toe_off_A'
 j['phases'][d][11]='support_exit_B'
 j['phases'][d][12]='toe_off_B'
j['phases']['SW'][6]='flight'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')

