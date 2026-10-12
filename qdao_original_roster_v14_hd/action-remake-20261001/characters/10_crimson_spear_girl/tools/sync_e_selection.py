from pathlib import Path
import json
r=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl')
p=r/'source-selection.json'
j=json.loads(p.read_text(encoding='utf-8-sig'))
s=json.loads((r/'run-E-grounding-work/selection.json').read_text(encoding='utf-8-sig'))['slots']
j['slots'].update(s)
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('E current selection synchronized')

