"""Record the lead's actual static review, without declaring dynamic acceptance."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from build_delivery import render_main_preview
from render_review_board import render_review_board,load_run_timing
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 m=read(ROOT/'manifest.json');now=datetime.now(timezone.utc).isoformat()
 notes={
 'run-N':'完整全身分足连图复核：左足15/16→01/02→03/04→05/06，右足07/08→09/10→11/12→13/14。沿纵轴分段接地；膝、踝和腾空腿独立变化，右扇左空手。',
 'run-S':'完整全身分足连图复核：左足15/16→01/02→03/04→05/06，右足07/08→09/10→11/12→13/14。支撑足相对身体由前近向后远推进；修S14腾空鞋向。',
 'run-NE':'完整16帧全身连图复核：两半圈连续支撑位置每两帧推进，末段右足保持支撑，纠正外翻和错误换腿候选。',
 'run-E':'完整16帧连图及局部原生复核：前接触、身下、身体经过、后蹬四位置各两张，E11持扇前摆衔接修复；E12/13按实际支撑位置选择独立图，鞋尖朝右。',
 'run-SE':'完整16帧连图及原生复核；与第二审核者交叉检查。鞋尖沿右下行进轴，SE10灰内衬清理，SE11持扇中间相位，接触及后蹬局部修正。08–10裤裆被袍摆遮挡，解剖足别信心中等，未伪称完全可见。',
 'run-SW':'完整16帧全身连图复核；右足15/16→01–06、左足07–14，修原重复同足支撑。05/06局部收回支撑腿增加后推，身体和手扇保留。',
 'run-W':'完整16帧全身连图复核；鞋尖朝左，同足各位置连续承重。03/04/11扇手过渡修正，06和16局部接地高度复查。',
 'run-NW':'完整16帧全身连图复核；左足15/16→01–06、右足07–14，修近远腿遮挡和重复支撑。07–10按真实足位重选独立姿态减少回退，11持扇远侧遮挡过渡局部修复。',
 'hit-E':'6张现有成品连图复核；鞋头朝右，受力后仰、缓冲、恢复及右手持扇可读。',
 'hit-W':'6张现有成品连图复核；鞋头朝左，受力后仰、缓冲、恢复及右手持扇可读。',
 'attack-E':'12张现有成品连图复核；双鞋朝右、蓄势出手收招成立；保留已修脚向和右手扇。',
 'attack-W':'12张现有成品连图复核；双鞋朝左、蓄势出手收招成立；保留已修脚向和右手扇。',
 'cast-E':'16张现有成品连图复核；双鞋朝右、右手扇左手诀；聚势释放收势可读，保留之前已修的脚位。',
 'cast-W':'16张现有成品连图复核；双鞋朝左、右手扇左手诀；聚势释放收势可读。'}
 current_round=read(ROOT/'audit/video-direction-20261004/repair-result.json')
 round_notes={
 'run-N':'本轮原生与新版16帧连图复核：01/02/07/08/09/10/11/15支撑靴收回纵向，保留左右交替和屈膝；11另补右腕半抬、扇面向右的中间相位，保留新脚向。',
 'run-NE':'本轮原生与新版16帧连图复核：08/09/12/13/15支撑靴从横向长鞋面收回东北透视；脚踝、鞋尖沿前进轴。',
 'run-SE':'本轮原生与新版16帧连图复核：04/05支撑靴收回东南透视。鞋尖投影向下改变，不是整腿下移；不按鞋尖最低点重新贴地。',
 'run-NW':'本轮原生与新版16帧连图复核：10腾空左靴的鞋底朝向与09/11连续，右支撑靴保持；03补右腕经过远侧身体遮挡的扇手中间相位。',
 'run-E':'本轮03右持扇腕收至腰前身侧，左拳向前摆经过身侧；保留已修腿脚。',
 'run-W':'本轮03胸肩提前侧转，右手保留腹侧扇、近左拳不握扇柄；保留已修腿脚。',
 'run-SW':'本轮原生与新版16帧连图复核：10左支撑鞋尖收回西南轴；13/14为正常前足背屈，保留。',
 'attack-W':'本轮复核发现03持扇上臂连到近侧肩，已局部修正远右臂举扇、近左臂空手跨胸，复看02/03/04衔接。'}
 changed_groups={'-'.join(r['slot'].split('-')[:2]) for r in current_round['changes']}
 for group in changed_groups:
  notes[group]+=' '+round_notes[group]
 for r in m['frames']:
  assert sha(ROOT/r['output'])==r['sha256']
 record={'character':ROOT.name,'reviewer':'root','reviewedAt':now,'scope':'static_sequence_and_provenance_only','status':'static_sequence_reviewed_dynamic_pending','frames':[{'slot':r['slot'],'sourceSha256':r['derivedFrom']['sha256'],'outputSha256':r['sha256']} for r in m['frames']],'groups':[{'action':g['action'],'direction':g['direction'],'staticReviewed':True,'dynamicApproved':False,'notes':notes[g['action']+'-'+g['direction']]} for g in m['groups']],'timing':{'runFrameMs':60,'runCycleMs':960,'pairMs':120},'dynamicReview':{'status':'pending','reason':'Browser automation rejected the local file:// preview under URL security policy; no alternate route attempted. Static frame sequence and encoded timing reviewed; live normal/slow playback not observed for this final revision.'},'remainingObservation':['正常1×与0.25×最新整圈观感、16→01衔接；逐帧复核与时序核验不冒充实际播放验收。','斜向遮挡足别及局部接地点约10–25原生像素变化，未做最低像素贴地。'],'clientIntegration':'not_integrated','clientRuntimeAcceptance':'not_tested','userAcceptance':'not_reviewed_after_latest_repairs'}
 record['latestRepairRound']={'file':'audit/video-direction-20261004/repair-result.json','sha256':sha(ROOT/'audit/video-direction-20261004/repair-result.json'),'changedCount':current_round['changedCount'],'unchangedCount':current_round['unchangedCount']}
 record['evidenceMethod']='本轮逐张实际查看新原生图、受影响完整连图；未改帧同时核验旧审核SHA并复看各动作连图。各方向手臂和全腿轴线经过第二审核者复核，发现摆臂缺口后新增候选另经root复看；旧二审SHA只适用于当时图片，不自动扩为新图动态通过。'
 record['secondaryRunStructureReviews']=[{'file':p,'sha256':sha(ROOT/p)} for p in ['audit/video-direction-20261004/ne-e-se-w-hands-review.json','audit/video-direction-20261004/ns-nw-sw-hands-review.json']]
 p=ROOT/'audit/current-static-review.json';save(p,record)
 evidence={'record':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'reviewer':'root','reviewedAt':now,'scope':record['scope']}
 for r in m['frames']:
  r.update(visualApproval='static_sequence_reviewed',animationApproval='pending_final_dynamic_review',staticReview=evidence);r.pop('offlineReview',None)
  d=read(ROOT/r['derivedRecord']);d.update(animationApproval='pending_final_dynamic_review',staticReview=evidence,userAcceptance='not_reviewed_after_latest_repairs');d.pop('offlineReview',None);save(ROOT/r['derivedRecord'],d)
 for g in m['groups']:
  g.update(visualApproval='static_sequence_reviewed',animationApproval='pending_final_dynamic_review',staticReview=evidence);g.pop('offlineReview',None)
 m.update(animationApproval='pending_final_dynamic_review',staticReview=evidence,userAcceptance='not_reviewed_after_latest_repairs',clientIntegration='not_integrated',clientRuntimeAcceptance='not_tested',note='196帧已实际导出，当前完整连图逐帧静态复核；最新版本动态播放观感待验收。旧final-review已被用户反馈撤回，不再应用。');m.pop('offlineReview',None)
 save(ROOT/'manifest.json',m)
 t=load_run_timing();(ROOT/'preview/index.html').write_text(render_main_preview(m,t),encoding='utf-8');(ROOT/'preview/all-directions.html').write_text(render_review_board(m,t),encoding='utf-8')
 print(json.dumps({'staticFrames':len(m['frames']),'staticGroups':len(m['groups']),'dynamicApproved':False}))
if __name__=='__main__':main()
