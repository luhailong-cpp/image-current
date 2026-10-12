from pathlib import Path
from datetime import datetime,timezone
import json
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy');p=B/'review/review-run-S.json';d=json.loads(p.read_text(encoding='utf-8'));e=json.loads((B/'review/reference09-S/input-evidence.json').read_text(encoding='utf-8'))
notes={
1:'右前靴长轴向镜头，左后靴回收；两手归属和肩袖连接正确。',
2:'右靴平底支撑、左膝回收，已修靴轴合理；不因微小落点差异重画。',
3:'右支撑左通过，两手可追踪；02→03右笔臂变化较快，但不构成换手或断肩。',
4:'右脚低位支撑、左靴抬起，鞋轴与膝踝相符；认可参考对应前视姿态也不要求夸张露跟。',
5:'右支撑脚近正向、左前膝屈伸；不能仅凭前视图看不清后跟就判蹬地错误。',
6:'左前腿屈收、右腿后收，双靴向前；保留已改善的短腾空姿态。',
7:'左前腿较06伸开，仍未接触，右脚后收；与08脚轴一致。',
8:'左脚继续下降接近接触，膝踝方向直；不因未命中提示坐标重画。',
9:'左脚前伸接触、右脚后收，右笔前左卷后；头部起伏不作为单独重画理由。',
10:'左腿承重、右脚回收，两靴轴已纠正；09→10轻微体态变化留给完整播放观察。',
11:'左支撑右通过、右回收靴方向已修，笔头已补；持物归属正确。',
12:'左脚低位支撑、右脚回收倾斜主要是俯仰透视，未确证外撇，保留。',
13:'双靴长轴向前、左膝踝路径合理；参考同类前视支撑也未明显露出后跟，暂不作蹬离强化重画。',
14:'右脚前伸左后收，脚轴朝镜头；卷轴更正面可有投影变宽，不因尺寸数字机械改画。',
15:'右腿下降，左手卷前右手笔后，持物肩连接明确；脚轴正确保留。',
16:'右脚临接触，靴轴向前，与01持物侧别连续；微小ROI差不单独触发重画。'}
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'character':'17_ghost_script_calligrapher_boy','direction':'S',
'userReferenceAuthorization':'主代理转达最新用户认可09竹弓少女当前版“对了”，要求其他窗口参照；本记录按其当前runtime/run/S实图比较，不改09。',
'referenceEvidence':e,'referenceMetadataCaveat':'09 manifest旧visual/dynamic字段仍pending；最新人工认可另记，不改其历史状态。',
'comparisonMethod':'实际查看09当前16张与17选图16张的固定整画布240px配对图，并放大09的04/12和17的02/03/13。以鞋尖-鞋跟长轴、膝踝、肩袖到持物手为准；不按提示相位/精确像素验收。',
'phaseAlignment':{'referenceOffsetFrames':8,'reason':'09的01左腿领先，而17的01右腿领先；半循环相移只用于同侧腿比较，不对图片镜像或改序。','phaseLabelsAreNotApproval':True},
'timing':{'frameMs':45,'cycleMs':720,'referenceTimingStatus':e['timing']['run']['timingStatus'],'phaseWeightsApplied':False,'comparisonPage':'reference09-S/compare-720.html','livePlaybackObserved':False,'livePlaybackLimitation':'cua.createBrowserTab iab返回 Browser is not available: iab；后续cua.getState apps/browsers均为空。页面已保存，未伪称动态通过。'},
'footAxisConclusion':'17当前S脚轴的明显向外撇已修，鞋尖/后跟中心总体与前进膝踝同向；12的抬脚倾斜不足以判外撇。',
'handConclusion':'17保留右手毛笔、左手卷轴、2墨灵，16张未见换手或肩袖断接。02→03较快转换、06–08持物臂保持相近可在720ms实播复核，不因重物持手的短时保持就盲目重画。',
'groundingConclusion':'左右支撑/通过与短腾空可区分。认可参考的前视支撑亦不总能看见后跟抬起，因此撤回“05/13必须因前掌蹬离不够显著而继续重画”的优先级；实际脚轴正确的帧保留。',
'naturalMotionPolicy':'头部/肩膀自然起伏、道具朝向变化和几像素ROI差均不作为单独重画理由；当前16帧没有确证需要这轮新增的局部脚轴/肩连接修复。',
'generationThisPass':[],'selectionDecision':'retain_all_current_16','visualApprovalFor17':False,'fullDynamicApprovalFor17':False,
'frames':[{'frame':f['frame'],'file':f['file'],'sha256':f['sha256'],'referenceComparisonFrame':(f['frame']-1+8)%16+1,'decision':'retain','observed':notes[f['frame']]} for f in d['frames']],
'remainingReview':['完整720ms播放中判断02→03手臂变化和06–08近似持物臂是否可接受','实际透明边缘彩点仍需最终资源质量检查；不能从参考认可推导17已通过','客户端未接入，整体角色方向未齐']}
(B/'review/reference09-S-20261003.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d['approvedReferenceReview']='reference09-S-20261003.json';d['priorityRedrawFrames']=[]
d['footAxisReviewPolicy']='最新人工认可09竹弓少女当前版作为动作参考；仍分开判断鞋轴、膝踝、肩手与接地，不把精确坐标或自然头部起伏当硬错误。'
d['referenceBasedDecision']='保留当前S16；05/13前视蹬离显著度、16→01数像素差异不再自动触发重画。整体720ms实播仍待主代理复核。'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (B/'review/grounding-S/README.md').open('a',encoding='utf-8') as f:f.write('\n## 最新认可参考复核\n\n按用户最新认可的09竹弓少女当前S16实图复核，保留上述16张。明显脚轴外撇已修，右笔左卷及肩袖连接均保持；不再因05/13前视图看不清抬跟、自然头部起伏或数像素落点差单独追加重画。详见[认可参考复核](../reference09-S-20261003.json)。720ms对照页已保存，当前浏览器工具无可用浏览器，未宣告动态通过。\n')
print('reference S review saved; unchanged selections')

