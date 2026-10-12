from pathlib import Path
import json
from apply_registration import apply
R=Path(__file__).resolve().parents[1]
for direction in ('S','SW','SE'):
 p=R/'run'/direction/'registration.json'
 j=json.loads(p.read_text(encoding='utf-8-sig'))
 j['status']='reviewed_common_ground_then_final_sequence_review'
 j['applyTransform']=True
 j['method']='Manual pelvic centers; one shared source virtual ground y960 from support-sole review of 02/03 and 10/11; no per-frame sole alignment. Oblique/forward perspective is preserved.'
 for row in j['frames']:
  row['srcRoot'][1]=960
  row['basis']='Reviewed anatomical pelvic x; source ground y960 common to whole direction, not per-frame minimum pixel.'
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
 apply(p)
