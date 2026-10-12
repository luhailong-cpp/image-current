"""Current full-body audit and review metadata; immutable source evidence stays intact."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,argparse
R=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ap=argparse.ArgumentParser();ap.add_argument('--browser-reviewed',action='store_true');a=ap.parse_args()
stamp=datetime.now(timezone.utc).isoformat()
old=rd(R/'provenance/full-body-prior-selection.json')
notes={
'E':'双靴长轴朝E。11→12后折腿进入前摆，没有踝部独立横转；06/07/08需要左卡手后摆、右盘手前摆连续。',
'SE':'13/14露出的鞋底横截面不等于鞋长轴。可见膝、踝、鞋面中线连续朝右下，与15/16相容。',
'S':'正向腿脚纵轴稳定；06整体靴筒和靴面小幅侧倾属于自然屈伸，没有踝部独立向外横转。',
'SW':'前后腿深度和膝部屈伸连续，支撑靴朝SW；05–08、13–16的靴筒、鞋面、鞋尖无独立外撇。'}
rows=[]
for f in old['frames']:
 if f['action']!='run' or f['direction'] not in notes:continue
 edit=f['direction']=='E' and f['frame']==7
 rows.append({'action':'run','direction':f['direction'],'frame':f['frame'],'path':f['source'],'sha256AtReview':f['sourceSha256'],'actuallyViewed':True,
 'method':'当前PNG全身连图与固定范围的手臂和腿部放大联系表；E06/07/08另看原尺寸。',
 'hands':{'rightObject':'round_star_disk','leftObject':'three_star_cards','confirmedGripOrHandSwapError':False,'phaseDecision':'repair' if edit else 'retain','note':'07双臂提前回收，06/08仍是右盘手前摆、左卡手后摆，需局部修复。' if edit else '可见袖口、腕、握持连贯；肩肘遮挡处不作直接可见宣称。'},
 'legChain':{'confirmedOutwardAnkleTwist':False,'decision':'retain','note':notes[f['direction']],'occlusionLimit':'长袍遮住部分髋部，不能直接证明所有隐藏关节及整半圈解剖腿别。'},
 'visibleSupportObservation':'前落地→身下→后侧→后蹬的可见支撑位置相容；不能仅以位置标签认定解剖腿身份。'})
wr(R/'hand-review-20261005/audit-run-E-SE-S-SW.json',{'reviewer':'/root','reviewedAtUtc':stamp,'frameCount':len(rows),'frames':rows,'confirmedRepairSet':['run/E/07 arms'],'retained':63,'qaSources':'hand-review-20261005/qa-inputs.json','priorFrameEvidence':'provenance/full-body-prior-selection.json','scope':'全身可见运动链静态补审，非客户端验收'})
files=['hand-review-20261005/audit-run-E-SE-S-SW.json','hand-review-20261005/audit-run-N-NE-NW-W.json','hand-review-20261005/audit-combat-E.json','hand-review-20261005/audit-combat-W.json']
assert all((R/f).exists() for f in files)
applied=rd(R/'provenance/full-body-edits-applied.json')
review=rd(R/'provenance/offline-visual-review.json')
for g in review['groups']:
 edit=[7] if g['action']=='run' and g['direction']=='E' else []
 n=g['frames']
 g['fullBodyReview']={'revision':'2026-10-05_full_body','staticReviewed':True,'offlineReviewed':a.browser_reviewed,'reviewedFrames':list(range(1,n+1)),'replacementFrames':edit,'retainedFrames':[i for i in range(1,n+1) if i not in edit],'auditRecords':files,
 'scope':'肩肘腕持物与髋下膝踝鞋头的可见连接及相邻帧连续性',
 'visibilityLimit':'长袖、头发及长袍遮挡的肩肘髋不能逐点直接看见；不以标签替代运动解剖证据。',
 'currentBrowserSampled':a.browser_reviewed and g['action']=='run',
 'combatBrowserEvidence':'图片和战斗计时与上一轮保持一致，沿用已有正常/慢放浏览器观察，本轮另做全68张静态补审。' if g['action']!='run' else None,
 'note':'E07双臂提前回收的跳动局部修正；其他195帧保留。'}
 if g['action']=='run':
  g['fullBodyReview'].update(frameMs=60,loopMs=960)
review['updatedAt']=stamp
review['reviewMethod']='全196张手部与整腿可见运动链补审，E07两次局部AI编辑后采用第二版；其余195张不重画。8向60ms正常与240ms慢放抽样，并检查E06/07/08衔接。遮挡关节不宣称直接可见，技术检查不替代视觉审核。'
review['browserEvidence'].update(currentRevision='2026-10-05_full_body_60ms',observed=a.browser_reviewed,armDetailFrames=[6,7,8],frameMs=60,loopMs=960,observationScope='八向正常及4×慢放与E06/07/08、16→01边界抽样；非游戏内移动速度或滑步验收。')
wr(R/'provenance/offline-visual-review.json',review)
if a.browser_reviewed:
 sel=rd(R/'selection.json')
 for f in sel['frames']:
  p=R/f['generationRecord'];rec=rd(p)
  rec.update(fullBodyVisualReview='current_runtime_static_reviewed',fullBodyDynamicReview='run_60ms_240ms_browser_sampled' if f['action']=='run' else 'unchanged_combat_prior_browser_review_retained',fullBodyReviewRecord='provenance/offline-visual-review.json')
  if f.get('fullBodyRevision'):
   rec['dynamicReview']='browser_E06_07_08_normal_slow_sampled';f['dynamicReview']=rec['dynamicReview']
  wr(p,rec)
 wr(R/'selection.json',sel)
print(json.dumps({'fullBodyFrames':196,'replacementFrames':applied['count'],'offlineReviewed':a.browser_reviewed},ensure_ascii=False))

