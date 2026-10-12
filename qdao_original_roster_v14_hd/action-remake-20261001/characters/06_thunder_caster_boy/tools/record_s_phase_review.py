"""Record human visual phase observations tied to current S-frame hashes, never infer approval."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
observations=[
 ('右脚接触/支撑候选','右靴在画面左前方、底近水平，左膝后收；左符前摆右杖在后','右','接触零点候选，需连播区分刚落地与已支撑'),
 ('右脚承重','右靴仍在前下方，右膝略屈，双手开始经过中位','右','可留作承重段，压低较微弱'),
 ('右脚承重压膝','v5锁定01头尺寸，髋/膝略压低，右靴保留，左靴抬起','右','已撤销旧v3/v4相机放大结论；仍需动态受力检查'),
 ('右前掌最后支撑候选','v4将下方右靴从向画面左外撇改为朝镜头，膝踝轴对齐，左膝前摆保持','右','脚向局部修正完成；正视角后跟读法、02到04脚尖轨迹仍需动态复核'),
 ('左腿前摆的腾空候选','两靴离开支撑轮廓，右腿折收、左腿前摆，右杖前左符后','无','短暂飞行可保留，实际离地高度仍待地面标定'),
 ('下降候选','左靴向镜头前伸露较大鞋底，右后膝收起','无','与04/06轮廓相似，长停留可能显踢腿'),
 ('左脚下降/近触地候选','左前靴更放平向下，右后靴抬起，双持连贯','左接近支撑','如放慢仍漂浮，优先局部修鞋底转平及膝踝'),
 ('左脚近触地/初支撑候选','v3左前靴接近地面，左符持续在后，右杖在前，不再提前回牌','左','与08共同辨别真实接触点，不能照搬计划08'),
 ('左脚支撑','左靴画面右下、右靴后收，右杖前、左符后','左','第二半圈落地基准候选'),
 ('左脚承重','v4保留08头大小和手势，左膝轻微缓冲，左靴前下，右靴后提','左','替换v2错腿与v3放大；受力幅度仍需连播'),
 ('左脚承重压膝/双臂过中位','v4沿09重新局部编辑，左靴支撑轴摆正，右膝前屈，左符回腰，右杖回肋旁','左','v3缩小已撤换，v4头尺寸改善；需09→10→11实际连播继续复核相机和压膝'),
 ('左前掌最后支撑候选','v5左腿下撑、右膝上折；雷杖已从横扫改朝上，左符前摆','左','后跟抬升不如03明确，10→11→12仍需播放复核'),
 ('右腿前摆的腾空','v3保留原腾空腿势，仅将后摆右手/雷杖降到后腰旁','无','消除11→12→13高低反跳，双足高度仍需整体标定'),
 ('下降/右腿展开','右前膝展开、左靴后收，左符前右杖后，保留原候选','无','作为14的构图参考'),
 ('右脚下降接触准备','v4沿13小幅展开右小腿，头尺寸及右杖后摆角度保持','右接近支撑','比旧v3消除大幅头/杖反摆，接地尚未通过'),
 ('右脚预接触','v5保持v4身体手臂，将右前靴从横扭大露底改为朝镜头并减少鞋底可见面','右接近支撑','鞋尖方向已摆正，15→00跟落地与实际承重还需连播')
]
holds=[75]*16
frames=[]
for i,(phase,evidence,leg,note) in enumerate(observations):
 p=ROOT/f'runtime/run/S/{i:02d}.png';record=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8-sig'))
 frames.append({'index':i,'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':record.get('derivedFrom'),'observedPhase':phase,'pixelEvidence':evidence,'supportLegIdentity':leg,'note':note,'suggestedTrialHoldMs':holds[i]})
out={'character':'06_thunder_caster_boy','direction':'S','reviewedAt':datetime.now(timezone.utc).isoformat(),'method':'逐张原生输出与runtime放大图、16格接触表人工查看；并实际对照09当前S整组脚轴；非客户端通过','frames':frames,'selectedTiming':{'totalMs':sum(holds),'frameHoldsMs':holds,'status':'最新用户要求已选定：正常1200ms，16帧均匀75ms','basis':'用户要求800ms再增加一半并整除；旧承重权重试验已停用'},'root':{'provisional':[512,942],'verified':False,'note':'旧清单虚拟根，客户端待标定；远近脚不能强压同一像素行'},'dynamicPassed':False,'clientVerified':False,'openIssues':['客户端实际地面和位移滑步','全圈1200ms正常与慢速实际播放复核']}
(ROOT/'review'/'run_S_grounding_phase_20261003.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'reviewedFrames':len(frames),'trialMs':sum(holds),'dynamicPassed':False}))
