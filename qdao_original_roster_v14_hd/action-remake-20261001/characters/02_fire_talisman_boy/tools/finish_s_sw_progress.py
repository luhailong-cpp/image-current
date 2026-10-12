from pathlib import Path
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1]
inv=json.loads((R/'inventory-hit.json').read_text(encoding='utf-8-sig'))
files=[]
for f in inv['frames']:
 if f['action']=='run' and f['direction'] in ['S','SW']:
  files.append({'file':f['path'],'sha256':f['sha256'],'source_record':f['source_record']})
selected={f['source_record'] for f in files}
rejected={'run-SW-02-grounding-v3-20261004-candidate1':'wrong_support_leg_swap','run-SW-05-grounding-v3-20261004-candidate1':'six_cards_instead_of_five','run-S-09-grounding-v3-20261004-candidate1':'insufficient_depth_progression','run-S-13-grounding-v3-20261004-candidate1':'rear_support_lateral_position_not_paired','run-SW-09-grounding-v3-20261004-candidate1':'prop_grip_swap_and_card_count','run-SW-09-grounding-v3-20261004-candidate2':'insufficient_position_progression','run-SW-10-grounding-v3-20261004-candidate1':'moved_support_too_far_for_second_pair'}
for stem,reason in rejected.items():
 p=R/'reviews'/f'{stem}.review.json'
 p.write_text(json.dumps({'candidate':stem,'verdict':'rejected_not_current_formal','reason':reason,'formalImport':False,'selectedSourceRecord':False},ensure_ascii=False,indent=2),encoding='utf-8')
progress={'updatedAt':datetime.now(ZoneInfo('America/New_York')).isoformat(),'status':'S_and_SW_formal_32_frames_static_review_complete_main_dynamic_pending','latestRule':'同脚连续8帧，四个渐进位置每位置2张独立姿态，每张75ms，1200ms整圈','frames':sorted(files,key=lambda x:x['file']),'reviews':['reviews/run-S-position-pairs-final-review-20261004.json','reviews/run-SW-position-pairs-final-review-20261004.json'],'formalRevisedSlots':sum('grounding-v3' in f['source_record'] for f in files),'actualModel':None,'actualQuality':None,'knownUnresolvedArtFailures':[],'remaining':['主线程统一可见浏览器动态抽验','客户端未接入'],'cleanup':'未执行删除。沿用主线程已记录的批量删除自动审批拒绝，不绕过。'}
(R/'reviews/grounding-v3-hit-progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf-8')
print('final source count',len(files),'revised slots',progress['formalRevisedSlots'])

