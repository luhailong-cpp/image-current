"""Human observations of the actually viewed root-owned oblique frames."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
observed={
'SE':[
('右支撑','前下方闪电纹右腿承重，左后腿折收；左牌在前、右杖在后'),
('右支撑缓冲','保持00右脚接地，膝略压低；头尺寸局部修正后接近00'),
('右支撑后段','右腿在髋下支撑，对側左膝前提；双臂过中位'),
('右前掌蹬离候选','右腿向后下伸、左膝前上；靴后跟抬起，牌/杖持手正确'),
('左腿前摆腾空','前方无大闪电纹的左腿伸出，右后腿回收，杖前牌后'),
('左腿下降','左小腿展开，右腿后收；双手保持上一相位'),
('左腿近触地','左前靴仍有鞋底可见，向下准备接触；不是已充分承重'),
('左初接触候选','左靴转为接近平底，右后腿折收；v4保持正确持手与摆臂'),
('左支撑','左前靴平放轮廓，右后腿回收；v5沿00修正头部大小'),
('左支撑缓冲','左膝压低，脚掌平放；右杖前、左牌后'),
('左承重后段','左前靴保留水平支撑，右腿准备通过髋下'),
('左前掌蹬离候选','v6后侧无大闪电纹左腿伸向下，前侧闪电纹右腿屈膝抬起；避免v5重复错腿'),
('右腿前摆腾空','闪电纹右腿前伸，左后腿折收；左牌前、右杖后'),
('右腿下降','右小腿继续展开，前靴露底逐步减小，双手与12同向'),
('右预接触','右前靴更平，左腿后收；保持头部修正与左牌前摆'),
('右接触准备','右靴接近平底，准备衔接00；未按最低像素强贴地')],
'NW':[
('右支撑','画面右侧右靴下撑露后跟，左靴后收露鞋底，左牌前右杖后'),
('右支撑缓冲','右下靴维持支撑，左后腿屈膝；肩肘保持相位'),
('右承重后段','右膝略压，左后靴开始通过；右靴朝NW'),
('右前掌蹬离候选','右靴抬跟露底边，左膝转向前；两臂进入换向'),
('左腿前摆腾空','左膝向NW前方，右后靴大露底；左臂后下、右臂前摆'),
('左下降','v4保持04正确双臂，左腿小幅向下，右后腿继续回收'),
('左近触地','左下靴接近支撑、右靴后收；v5从肩肘后摆左手修复过早前举'),
('左初支撑候选','左靴更低、右靴抬起；左臂仍后摆，非同侧前摆'),
('左支撑','左靴支撑右腿后收；v5左臂从肩关节后摆、右臂前摆'),
('左支撑缓冲','左膝压低；v6保留v5左臂后侧开始回中，头部重新匹配08/10，撤换旧偏小头部'),
('左承重后段','左靴支撑、右腿屈膝；v5左手到腰侧中位，未举到脸前'),
('左蹬离到换腿候选','v4右前靴改为后跟/鞋面读法，左后靴抬跟；最后触地点仍需动态标定'),
('右腿前摆腾空','v4右腿前摆露后跟，左后靴露底，已撤换旧相反腿'),
('右腿下降','v4右下靴向下、左后靴回收，左牌前右杖后'),
('右预接触','v4右前靴变平露鞋面，左后靴露底，避免双腿都后踢'),
('右接触准备','v4右靴后跟/鞋面清晰，衔接00右支撑，保持两物原持手')]
}
for d,rows in observed.items():
 frames=[]
 for n,(phase,evidence) in enumerate(rows):
  p=R/f'runtime/run/{d}/{n:02d}.png';rec=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8-sig'))
  frames.append({'index':n,'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':rec.get('derivedFrom'),'observedPhase':phase,'pixelEvidence':evidence,'note':'逐张/整组静态查看记录；实际地面、位移滑步和最终时长未验证'})
 out={'direction':d,'reviewedAt':datetime.now(timezone.utc).isoformat(),'frames':frames,'method':'实际查看原生返回图、runtime与固定画布16格联系表；不按计划帧号自动批准','staticFootYawReview':'两靴朝本方向或自然回收，未见需要全组收窄站距的外八；局部真实肩肘和脚掌修正已记录','dynamicPassed':False,'clientVerified':False,'root':{'provisional':[512,942],'verified':False},'openIssues':['实际地面/根点与位移滑步','全圈正常慢速连续性','07/15到下一支撑的真实接触点','1200ms正常节奏下检查完整首尾与承重']}
 (R/'review'/f'run_{d}_grounding_phase_20261003.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print(d,len(frames))
