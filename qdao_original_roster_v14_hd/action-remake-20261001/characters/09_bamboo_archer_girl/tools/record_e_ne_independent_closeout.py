from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'audit/run-E-paired-ground-review.json'
d=json.loads(p.read_text(encoding='utf-8-sig'))
d['sameAnatomicalFootConfirmed']=False
d['rootIndependentReview']={'atUtc':datetime.now(timezone.utc).isoformat(),'scope':'Current full E01/03/07/10/13/15 originals and 16-frame contact sheet','observed':'Support boot progresses from screen-right forward to screen-left rear; knee/ankle sagittal direction and arm cycle readable. Side-facing robe hides proximal hips.','retractedInference':'Changing screen-left/right shorts opening is not sufficient evidence of an anatomical leg swap; shorts follow the thighs. No additional hip edit is justified by that observation alone.'}
note='E侧视袍裙遮髋；现有L/R为预定支撑组，不能仅凭固定屏幕裤口证实同脚八连，也不能据裤口前后变化断定换腿。'
if note not in d['remainingNotPassed']:d['remainingNotPassed'].append(note)
for pair in d['spatialPairs']:pair['sameFootRoots']='侧向近远髋被衣服遮挡；空间推进已看图，解剖同脚身份尚未独立证实。'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=ROOT/'runtime/run/NE/08.png'
out={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'slot':'run/NE/08','frame':8,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'staticInspected':True,'evidence':'实际查看新原生及1024导出：承重右靴鞋尖缩短、向远处右上收回；鞋跟在近侧，长横向外伸鞋掌已缩减。膝踝、髋连接与悬起左脚保留。','footOrientation':'后右NE透视，鞋尖比鞋跟更远、较高；并非侧向整只脚横伸。','remaining':'实体世界地面与动态接缝未验收；只报告原图可见变化。','dynamicVisualAcceptance':False}
(ROOT/'audit/NE08-boot-axis-final-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('Recorded independent E identity limits and NE08 actual boot-axis inspection.')

