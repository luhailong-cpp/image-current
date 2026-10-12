from pathlib import Path
from PIL import Image
import json,hashlib,datetime
BASE=Path(__file__).resolve().parents[1]
p=BASE/'review/review-run-S.json';d=json.loads(p.read_text(encoding='utf-8'))
versions={4:3,5:2,7:2,8:2,12:2,13:2,15:2,16:2}
new={
7:('左腿前伸、右脚后收；下降段候选','none_or_ambiguous','left','右笔臂前、左卷臂后，右袖明显张开，肩手仍相连。','前左腿比06伸长并下降，但前靴比09接触靴更低；不可认作已校准离地。','07→08头身/袖形跳变；前脚下降过深需修'),
8:('左脚临接触候选','none_or_ambiguous','left','右手持笔胸前、左手持卷髋后，未换手。','左前靴露底、右后脚折起，符合临接触轮廓；前靴最低点仍比09偏低，落地趋势需重画校正。','08→09前靴反向上跳；07→08头部尺度变化'),
15:('右腿前伸、左脚后收；下降段候选','none_or_ambiguous','right','右笔臂后，左卷臂前，握持持续但卷轴偏大。','右前靴伸得更低、腿较14更长，靴底比01接触帧低；不能仅因提示词叫下降就认定物理正确。','15→16卷轴/头身尺度跳变；前脚过低'),
16:('右脚临接触候选','none_or_ambiguous','right','右笔手髋旁后、左卷手胸前，侧别与01连续。','右前靴露底，下一帧01靴底较平；脚的相位方向正确，但16最低点仍比01稍低，需修正临接触高度。','16→01前靴上跳；15→16道具尺度变化')
}
for n,v in new.items():
    phase,support,lead,hands,ground,issues=v
    d['frames'].append(dict(frame=n,file=f'staging/run-S-{n:02d}-v2.png',observedPhase=phase,supportCandidate=support,lead=lead,handConnection=hands,groundingObservation=ground,issues=[issues,'透明边缘彩点'],status='needs_review',approval=False))
for f in d['frames']:
    n=f['frame'];v=versions.get(n,1);path=BASE/'staging'/f'run-S-{n:02d}-v{v}.png';f['file']=str(path.relative_to(BASE)).replace('\\','/');f['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();im=Image.open(path);f['nativeSize']=list(im.size)
    if n==5:
        f.update(observedPhase='右脚前掌推离趋势候选',supportCandidate='right_toe_candidate',groundingObservation='v2由04-v3定点绘制；右靴更窄、脚尖下压、后跟侧缘稍高，左脚抬离；比v1更接近推离。前视角下脚跟抬起仍弱，暂不通过。',issues=['前掌推离需动态复核','05→06摆动脚投影变化','透明边缘彩点'])
    if n==13:
        f.update(observedPhase='左脚前掌推离尝试，但支撑腿外摆过大',supportCandidate='left_toe_ambiguous',groundingObservation='v2由12-v2定点绘制；左靴脚尖向下且较窄，但支撑脚大幅外摆到画面右侧，骨盆到前掌的负重路径可疑；不可标蹬地通过。',issues=['支撑腿外摆过大需修','13→14腿位跳变','透明边缘彩点'])
d['frames'].sort(key=lambda f:f['frame'])
d.update(reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),available=16,expected=16,missing=[],approved=0,fullLoopDynamicReview='all_slots_available_not_yet_passed',candidateSupportFrames=[2,3,4,10,11,12],priorityRedrawFrames=[7,8,13,15,16],otherProblemFrames=[5,9,11,14],normal240pxFindings='16槽现已齐。固定整画布240px对照可辨02/03/04右支撑与10/11/12左支撑；13外摆、11毛笔缩短、07→08/09→10头身变化以及14/15卷轴放大仍明显。07/08/15/16鞋底投影在接触帧之前过低，需按膝踝局部重画，不移动整图。尚未宣告完整动态通过。',newRepairAttempts=['run-S-04-v3','run-S-05-v2','run-S-12-v2','run-S-13-v2'],newMissingSlotFills=['run-S-07-v2','run-S-08-v2','run-S-15-v2','run-S-16-v2'])
d['root']['additionalFinding']='依据实图，S01/S09近侧接触靴约在原生y1180附近；S07/S08/S15临接触靴约y1210，较其后接触帧反而偏低约20–30像素。这是人工像素位置估计，不是校准锚点。需修正腿/踝投影；不能以整图上移补偿。'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Reviewed',len(d['frames']),'selected S frames; all remain pending')
