from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'candidate/battle-registration.json'
d=json.loads(p.read_text(encoding='utf-8-sig'))
d['groups']['attack/W']={'translation':[0,174],'basis':'Entire W direction uses common x0 to preserve complete spear tip in every stance; provisional native virtual root x746.3 y1120. Never per-frame foot alignment.'}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

