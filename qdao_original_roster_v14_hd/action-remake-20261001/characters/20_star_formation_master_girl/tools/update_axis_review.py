"""Record the actual current axis review without rewriting older source evidence."""
from pathlib import Path
from datetime import datetime,timezone
import json,argparse
R=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ap=argparse.ArgumentParser();ap.add_argument('--browser-reviewed',action='store_true');a=ap.parse_args()
review=rd(R/'provenance/offline-visual-review.json'); applied=rd(R/'provenance/axis-edits-applied.json')
notes={
 'N':'全16帧靴跟与纵向鞋轴稳定，抬脚露底保持自然屈膝。',
 'S':'全16帧保留。06右摆靴随靴筒小幅侧倾，未见踝关节单独向外横转；不是硬性外八。',
 'NW':'全16帧保留。13宽厚支撑靴仍沿NW，右摆腿露底属于屈膝透视；15/16轴稳定。',
 'NE':'05右支撑靴原接近E侧面，局部修回NE后跟透视；06、09/10水平底边不等于鞋长轴横转，其余保留。',
 'SE':'全16帧保留。13/14膝踝鞋面中线朝右下，横置的是鞋底横截面，前摆透视与15/16相容。',
 'E':'全16帧双靴朝右，11至12是后折腿进入前摆，相位变化没有横转。',
 'W':'全16帧保留。05至08鞋尖朝左下为侧视屈膝后的垂足；前翘鞋尖属于踝屈伸。',
 'SW':'全16帧保留。05至08及13至16摆脚靴筒、鞋背、鞋尖连续，支撑靴朝SW。'}
files=['axis-review-20261004/audit-E-W-SW.json','axis-review-20261004/audit-N-S-NW.json','axis-review-20261004/audit-NE-SE.json']
assert all((R/f).exists() for f in files)
for g in review['groups']:
 if g['action']!='run':continue
 d=g['direction'];edited=[x['frame'] for x in applied['applied'] if x['direction']==d]
 g['axisReview']={'revision':'2026-10-04_knee_ankle_boot','reviewedFrames':list(range(1,17)),'replacementFrames':edited,'retainedFrames':[i for i in range(1,17) if i not in edited],'staticReviewed':True,'offlineReviewed':a.browser_reviewed,'browserNormalSlowSampled':a.browser_reviewed,'frameMs':75,'loopMs':1200,'note':notes[d],'auditRecords':files,'referenceEvidence':'provenance/axis-reference-review.json'}
review['updatedAt']=datetime.now(timezone.utc).isoformat()
review['reviewMethod']='当前128跑步逐张与足部放大/联系表审核膝踝鞋长轴；保留正常屈膝、短缩及露底透视。正常与慢放浏览器抽看、NE04/05/06与16→01边界逐帧检查另记。68战斗当前连图复查保留。技术帧数和SHA不替代视觉审核。'
review['browserEvidence'].update(currentRevision='2026-10-04_knee_ankle_boot',observed=a.browser_reviewed,axisDetailFrames=[4,5,6],observationScope='正常/慢放与关键边界抽样；不是游戏内速度或滑步验收。')
wr(R/'provenance/offline-visual-review.json',review)
if a.browser_reviewed:
 sel=rd(R/'selection.json')
 for f in sel['frames']:
  if f['action']!='run':continue
  p=R/f['generationRecord'];rec=rd(p)
  rec.update(axisVisualReview='current_runtime_static_reviewed',axisDynamicReview='browser_normal_slow_and_NE04_05_06_sampled',axisReviewRecord='provenance/offline-visual-review.json')
  if f.get('axisRevision'):rec['dynamicReview']='browser_axis_revision_sampled';f['dynamicReview']='browser_axis_revision_sampled'
  wr(p,rec)
 wr(R/'selection.json',sel)
print(json.dumps({'axisDirections':8,'replacementFrames':applied['count'],'offlineReviewed':a.browser_reviewed},ensure_ascii=False))
