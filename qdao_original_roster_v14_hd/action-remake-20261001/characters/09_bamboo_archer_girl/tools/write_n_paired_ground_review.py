from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
notes={
1:"右脚身下偏后承重，右靴平底；左腿后屈、鞋底抬起；以02正确比例独立重画，头身保持。",
2:"右脚继续身下偏后承重，膝仍微屈，右靴后跟杯直立；左脚摆动，未换支撑脚。",
3:"右脚随身体经过进入后侧，膝踝自然延伸；绿靴跟杯和薄金底仍可读，不把鞋饰当脚尖。",
4:"右腿末段后蹬，跟抬、前掌持续接触；左腿抬起准备下一步，手臂已反向回转。",
5:"已真实重画左脚前位落地：左靴跟杯落平、软膝，支点较远投影较高；右腿明显屈膝收起，摆动底高于支撑底。",
6:"左脚第二张前位接触与加载：膝踝角度变化、支点较05稍后；右腿仍屈膝抬起，左弓臂后、右空手前。",
7:"左脚身下偏前支撑，后跟和金底落平；右腿恢复，左右根部可追踪。",
8:"左脚继续身下偏前承重，膝有缓冲，右腿收后；完整手握长弓与空手反相。",
9:"左支点随身体经过进入身下偏后，左跟金边落平，右鞋底抬起。",
10:"左脚同一后中位持续承重，支撑膝较前段伸展但未锁膝；右腿继续恢复。",
11:"已重画左脚近后位置，左腿承重延伸、薄金底仍接触；右腿后屈，不用悬空帧凑数。",
12:"左前掌后蹬末段，跟抬而前掌保持接触；右腿抬起，为13换脚。",
13:"右脚前位地面接触，鞋跟杯落平；远侧接地投影高于中后段，左脚明显抬起。",
14:"已把旧飞行帧改为右前位加载：右跟与前掌落平，左腿后屈，开始持续8张右支撑。",
15:"独立以16正确比例重画右脚身下偏前承重，保留自然小腿长度；左脚抬起与16不同，未压扁腿形。",
16:"右脚继续早中位支撑、膝微屈，靴跟直立薄金底落平；与01同脚连续跨循环。"
}
segments=[
{"foot":"left","positions":[{"frames":[5,6],"position":"前位落地加载","evidence":"支撑左脚在远侧前位、膝踝有投影缩短；右腿收起，05/06为独立姿态。"},{"frames":[7,8],"position":"身下偏前承重","evidence":"支点随后更靠近身下，跟杯落平，支持膝继续缓冲。"},{"frames":[9,10],"position":"身体经过后的中后支撑","evidence":"左腿较前段展开，身体经过支撑脚，右腿仍摆动。"},{"frames":[11,12],"position":"后侧延伸与蹬离","evidence":"11负重延伸，12可见抬跟和低位前掌，尚未换左支撑。"}]},
{"foot":"right","positions":[{"frames":[13,14],"position":"前位落地加载","evidence":"右靴前位触地、透视投影较高，左腿抬起；14不再飞行。"},{"frames":[15,16],"position":"身下偏前承重","evidence":"右腿自然展开至身下，未压缩成短胫骨；平跟连续。"},{"frames":[1,2],"position":"身体经过后的中后支撑","evidence":"循环跨界后仍同一右脚负重，左腿和手臂继续独立变化。"},{"frames":[3,4],"position":"后侧延伸与蹬离","evidence":"03负重后侧，04跟升前掌保持接触，接05左脚落地。"}]}]
rows=[]
for f,note in notes.items():
 p=ROOT/f'runtime/run/N/{f:02d}.png'
 rows.append({'slot':f'run/N/{f:02d}','frame':f,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'status':'passed','staticAnatomy':'passed','evidence':note,'footOrientation':'脚长轴沿北向运动纵深，与同侧小腿一致；正常膝屈和提踵保留，未见脚掌左右外撇。','dynamicApproval':False})
out={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'action':'run','direction':'N','latestRequirement':'同脚8连帧持续接触，逐步改变相对地面位置，每位置两张独立姿态，再与另一脚交替。','staticPairedGroundStatus':'passed_with_perspective_limits','frameMs':75,'cycleMs':1200,'positionMs':150,'segments':segments,'frames':rows,'method':'逐张当前原图、256px接触表实看；空间依据股胫踝关系、支持底朝向及同脚追踪，坐标仅辅助，非最低脚对齐。','remainingIssues':['未完成正常速度实播视觉验收，逐帧证据不能保证游戏运动中完全无滑步。','北向为纵深透视，前中后的投影距离比侧向小；每对通过连续原图判定，不以提示坐标证明。'],'dynamicVisualAcceptance':False,'clientIntegration':'not_integrated'}
(ROOT/'audit/run-N-paired-ground-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
review={'reviewedAtUtc':out['reviewedAtUtc'],'reviewMethod':out['method'],'frames':rows,'sequences':[{'sequence':'run/N','status':'needs_review','staticPairedGroundStatus':out['staticPairedGroundStatus'],'frameSha256':[r['sha256'] for r in rows],'evidence':'左右脚各8张连续支撑，四个空间阶段各两张独立姿态。详见audit/run-N-paired-ground-review.json。','segments':segments,'remainingIssues':out['remainingIssues'],'dynamicApproval':False,'currentTiming':{'frameMs':75,'cycleMs':1200,'frameDurationsMs':[75]*16,'extraLoopPauseMs':0,'clientTimingConfirmed':False}}],'pairedGroundReview':'audit/run-N-paired-ground-review.json'}
(ROOT/'review-parts/run-N.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
print('N paired-ground review:16 current frames; static only, dynamic unverified.')

