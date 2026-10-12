from pathlib import Path
import json
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,data):(R/p).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
review=read('reviews/final-review.json')
archive=R/'reviews/final-review-before-four-frame-feedback.json'
if not archive.exists():archive.write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
review['reopenedAtUtc']=datetime.now(timezone.utc).isoformat()
review['knownUnresolvedArtFailures']=['2026-10-04用户反馈：脚着地感觉仍不足；每脚每次落地至少连续4张真实接触/缓冲/支撑帧，当前八方向重新绘制与复核中；仍需复核残余膝踝鞋掌外翻。']
review['frames']=[x for x in review.get('frames',[]) if '/run/' not in x['path']]
for seq in review.get('sequences',[]):
 if seq['action']=='run':
  seq['offlineReview']='reopened_four_frame_grounding_revision'
  seq['observations']='四帧接地修订中：旧一轮手脚检查不能作为本次承重通过；真实姿态与逐向帧段待复核。'
write('reviews/final-review.json',review)
for name in ['inventory.json','previews/report.json']:
 p=R/name
 if p.exists():
  obj=read(name);obj['offline_materials_complete']=False;obj['grounding_revision_status']='four_contact_frames_revision_in_progress'
  for frame in obj.get('frames',[]):
   if frame.get('action')=='run':frame['visual_status']='four_frame_grounding_revision_pending'
  write(name,obj)
for name in ['tools/run-grounding-template.html','previews/run-grounding.html','previews/index.html']:
 p=R/name
 if p.exists():
  s=p.read_text(encoding='utf-8')
  s=s.replace('八方向手脚素材与离线复核已完成','八方向连续四帧接地修订中').replace('离线复核完成·客户端未接入','连续四帧接地修订中·客户端未接入').replace('素材与离线复核完成','连续四帧接地修订中')
  p.write_text(s,encoding='utf-8')
(R/'STATUS.md').write_text('# 02 火符少年当前进度\n\n2026-10-04：根据用户“脚着地还是少了感觉”重新打开八方向跑步修订。196张现有正式帧不等于新接地要求通过。\n\n- 跑步128张：重绘必要关键帧，核验每脚每次落地至少连续4张不同的接触、缓冲、支撑姿态；整圈仍16×75ms=1200ms。膝踝与鞋掌沿行进方向，排除外翻。\n- 受击12、普攻24、施法32：保留此前离线复核结果。\n- 正式替换后重建动态预览、逐图来源、SHA与合并交接。客户端未接入。\n',encoding='utf-8')
print({'runReview':'reopened','battleReviewedFrames':len(review['frames'])})
