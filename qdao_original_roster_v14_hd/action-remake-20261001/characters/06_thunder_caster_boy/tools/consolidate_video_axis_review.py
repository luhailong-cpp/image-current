"""Bind actual axis observations and repairs to current files, preserving phase maps."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from current_run_pairs import current_run_pairs
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads((R/p).read_text(encoding='utf-8-sig'))
names=['video_axis_N_NE_NW_20261004.json','video_axis_S_SE_SW_20261004.json','video_axis_EW_combat_20261004.json']
rows={};sources=[]
for name in names:
 data=read('review/'+name)
 assert not data.get('unresolvedBlockingIssues',[]),name
 for f in data['frames']:
  rel=f.get('file',f.get('path'));assert sha(R/rel)==f['sha256'],rel
  assert rel not in rows,rel
  rows[rel]={**f,'file':rel,'axisReview':'review/'+name}
 sources.append({'file':'review/'+name,'sha256':sha(R/'review'/name)})
assert len(rows)==196,len(rows)
pairs=current_run_pairs();assert len(pairs)==128
for rel,f in rows.items():
 if '/run/' in rel:
  f.update({k:v for k,v in pairs[rel].items() if k in ['supportLeg','pairFrames','positionPhase']})
  f['phaseReview']=pairs[rel]['sourceReview']
before=read('records/review_before_video_axis_feedback_20261004.json')
old={f['file']:f['sha256'] for f in before['frames']}
changed=[{'file':rel,'previousSha256':old.get(rel),'sha256':f['sha256']} for rel,f in sorted(rows.items()) if old.get(rel)!=f['sha256']]
video=read('records/reference_video_observation_20261004.json')
video.update(actualObservation={'browser':'实际本地原视频正常播放并启动四分之一慢放；慢放在12.622秒后浏览器画面响应卡住，未把未观察段冒称看完','sequentialFrames':'已实际查看五段连续32帧：0.000–1.292、4.000–5.292、8.000–9.292、12.000–13.292、16.000–17.292秒，共160张连续抽帧','finding':'原视频同向步伐沿身体纵向平面前后推进，屈膝、抬跟及正常露底均存在；转向时全身改变方向。人物小且部分遮挡，不能确定每张鞋掌细节','screenshot':'用户截图为12山岳守卫NW，作为问题类型参照，不当作06帧证据'})
(R/'records/reference_video_observation_20261004.json').write_text(json.dumps(video,ensure_ascii=False,indent=2),encoding='utf-8')
out={'reviewedAt':datetime.now(timezone.utc).isoformat(),'scope':'06雷法少年196帧最新视频歪脚/外翻反馈复核','staticReviewComplete':True,'sourceReports':sources,'referenceVideo':'records/reference_video_observation_20261004.json','criteria':['膝至踝至鞋长轴保持同一运动平面','正常屈膝、透视短缩和前后俯仰露底可保留','不把单帧鞋底可见等同横向外翻','相邻帧鞋轴不独立骤转，斜向脚位沿该方向推进'],'changedFramesThisRound':changed,'retainedFramesThisRound':196-len(changed),'frames':[rows[k] for k in sorted(rows)],'runTiming':{'frameMs':75,'cycleMs':1200,'twoIndependentPosesPerPosition':True,'mirrorsOrDuplicatesUsed':False},'rootReview':['重新查看当前8方向16帧联系图，E/W旧板已重建后复看','实际查看castW12、13、14全图；13修改前鞋头偏向镜头，修改后朝W且膝踝/两手持物保留','S/SE/SW由独立检查逐图及指定顺序邻帧对照，未确证需重画外翻','N/NE/NW以独立报告逐张观察和当前SHA为准'],'unresolvedBlockingIssues':[],'userFinalApproved':False,'clientIntegrated':False,'offlinePlaybackEvidence':'review/current_playback_evidence_20261004.json','limits':'本报告为逐图与顺序邻帧观察；实际浏览器功能与时序另记，不代用户最终动态观感批准。'}
(R/'review/video_axis_final_20261004.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(rows),'changed':changed,'staticReviewComplete':True},ensure_ascii=False))
